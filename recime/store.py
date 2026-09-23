import json
import os
import sqlite3
import unicodedata
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from probe import reel_url
from recime.models import DraftEdit, ImportRequest


class Problem(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message
        super().__init__(message)


def now():
    return datetime.now(timezone.utc).isoformat()


def db_path():
    return Path(os.environ.get("RECIME_DB", "data/recime.sqlite3")).resolve()


def normalize(value):
    return "".join(c for c in unicodedata.normalize("NFD", value.casefold())
                   if not unicodedata.combining(c))


class Store:
    def __init__(self, path):
        self.path = Path(path).resolve()

    def connect(self):
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.transaction() as db:
            version = db.execute("PRAGMA user_version").fetchone()[0]
            if version > 1:
                raise RuntimeError("Banco criado por uma versão mais recente do ReciMe.")
            if version == 0:
                db.execute("""CREATE TABLE imports (
                    id TEXT PRIMARY KEY, code TEXT NOT NULL UNIQUE,
                    source_url TEXT NOT NULL, canonical_url TEXT NOT NULL,
                    scenario TEXT NOT NULL, state TEXT NOT NULL
                    CHECK(state IN ('queued','processing','ready','failed','confirmed','discarded')),
                    version INTEGER NOT NULL DEFAULT 1, attempts INTEGER NOT NULL DEFAULT 0,
                    original TEXT, draft TEXT, error TEXT,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL)""")
                db.execute("""CREATE TABLE recipes (
                    id TEXT PRIMARY KEY, import_id TEXT NOT NULL UNIQUE REFERENCES imports(id),
                    content TEXT NOT NULL, created_at TEXT NOT NULL)""")
                db.execute("PRAGMA user_version = 1")

    @contextmanager
    def transaction(self):
        db = self.connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    @contextmanager
    def reader(self):
        db = self.connect()
        try:
            yield db
        finally:
            db.close()

    @staticmethod
    def row(db, ident):
        row = db.execute("SELECT * FROM imports WHERE id = ?", (ident,)).fetchone()
        if row is None:
            raise Problem(404, "Importação não encontrada.")
        return row

    @staticmethod
    def present(row):
        value = dict(row)
        for field in ("draft", "original"):
            value[field] = json.loads(value[field]) if value[field] else None
        value["demo"] = True
        return value

    def get(self, ident):
        with self.reader() as db:
            return self.present(self.row(db, ident))

    def pending(self):
        with self.reader() as db:
            rows = db.execute("SELECT * FROM imports WHERE state NOT IN ('confirmed','discarded') ORDER BY created_at DESC").fetchall()
            return [self.present(row) for row in rows]

    def submit(self, request: ImportRequest):
        canonical = reel_url(request.url)
        code = canonical.rstrip("/").rsplit("/", 1)[-1]
        with self.transaction() as db:
            existing = db.execute("SELECT * FROM imports WHERE code = ?", (code,)).fetchone()
            if existing:
                if existing["state"] == "discarded":
                    db.execute("""UPDATE imports SET state='queued', error=NULL,
                        draft=NULL, original=NULL, version=version+1, updated_at=? WHERE id=?""",
                               (now(), existing["id"]))
                return self.present(self.row(db, existing["id"]))
            ident, timestamp = str(uuid4()), now()
            db.execute("""INSERT INTO imports
                (id, code, source_url, canonical_url, scenario, state, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 'queued', ?, ?)""",
                       (ident, code, request.url, canonical, request.demo_scenario, timestamp, timestamp))
            return self.present(self.row(db, ident))

    @staticmethod
    def require(row, states, version=None):
        if row["state"] not in states:
            raise Problem(409, "Essa ação não está disponível no estado atual. Recarregue a página.")
        if version is not None and row["version"] != version:
            raise Problem(409, "O rascunho mudou em outra aba. Seu texto foi mantido nesta tela; copie as alterações antes de recarregar.")

    def edit(self, ident, edit: DraftEdit):
        with self.transaction() as db:
            row = self.row(db, ident)
            self.require(row, {"ready"}, edit.version)
            draft = json.loads(row["draft"])
            draft["title"] = edit.title.strip() or None if edit.title else None
            for field in ("ingredients", "steps"):
                previous = {item["id"]: item for item in draft[field]}
                # Allocate IDs above both original and edited IDs; never reuse a source ID.
                original = json.loads(row["original"])[field]
                next_id = max([*previous, *(item["id"] for item in original)], default=-1) + 1
                used, items = set(), []
                for item in getattr(edit, field):
                    value = item.model_dump()
                    ident_item = value["id"]
                    if ident_item is not None and (ident_item not in previous or ident_item in used):
                        raise Problem(422, "Item repetido ou desconhecido no rascunho.")
                    value["evidence"] = previous[ident_item]["evidence"] if ident_item is not None else []
                    if ident_item is None:
                        ident_item, next_id = next_id, next_id + 1
                    used.add(ident_item)
                    value["id"] = ident_item
                    for key, content in list(value.items()):
                        if isinstance(content, str):
                            value[key] = content.strip() or None
                    items.append(value)
                draft[field] = items
            db.execute("UPDATE imports SET draft=?, version=version+1, updated_at=? WHERE id=?",
                       (json.dumps(draft, ensure_ascii=False), now(), ident))
            return self.present(self.row(db, ident))

    def confirm(self, ident, version):
        with self.transaction() as db:
            row = self.row(db, ident)
            if row["state"] == "confirmed":
                return dict(db.execute("SELECT id FROM recipes WHERE import_id=?", (ident,)).fetchone())
            self.require(row, {"ready"}, version)
            recipe_id = str(uuid4())
            db.execute("INSERT INTO recipes VALUES (?, ?, ?, ?)", (recipe_id, ident, row["draft"], now()))
            db.execute("UPDATE imports SET state='confirmed', version=version+1, updated_at=? WHERE id=?", (now(), ident))
            return {"id": recipe_id}

    def transition(self, ident, action):
        states, target = ({"failed"}, "queued") if action == "retry" else ({"queued", "ready", "failed"}, "discarded")
        with self.transaction() as db:
            row = self.row(db, ident)
            self.require(row, states)
            db.execute("UPDATE imports SET state=?, error=NULL, version=version+1, updated_at=? WHERE id=?", (target, now(), ident))
            return self.present(self.row(db, ident))

    def claim(self):
        with self.transaction() as db:
            row = db.execute("SELECT id FROM imports WHERE state='queued' ORDER BY created_at LIMIT 1").fetchone()
            if row is None:
                return None
            db.execute("UPDATE imports SET state='processing', attempts=attempts+1, version=version+1, updated_at=? WHERE id=?", (now(), row["id"]))
            return self.present(self.row(db, row["id"]))

    def finish(self, ident, draft=None, error=None):
        with self.transaction() as db:
            row = self.row(db, ident)
            self.require(row, {"processing"})
            payload = json.dumps(draft, ensure_ascii=False) if draft is not None else None
            db.execute("""UPDATE imports SET state=?, original=?, draft=?, error=?,
                       version=version+1, updated_at=? WHERE id=?""",
                       ("failed" if error else "ready", payload, payload, error, now(), ident))

    def recover(self):
        # Called only by the executor while holding its exclusive OS lock.
        with self.transaction() as db:
            db.execute("""UPDATE imports SET state='failed',
                error='Processamento interrompido. Você pode tentar novamente.',
                version=version+1, updated_at=? WHERE state='processing'""", (now(),))

    def recipes(self, query=""):
        with self.reader() as db:
            rows = db.execute("""SELECT r.*, i.source_url, i.canonical_url FROM recipes r
                JOIN imports i ON i.id=r.import_id ORDER BY r.created_at DESC""").fetchall()
        result = [{**dict(row), "content": json.loads(row["content"]), "demo": True} for row in rows]
        return [r for r in result if normalize(query.strip()) in normalize(r["content"]["title"] or "não informado")]

    def recipe(self, ident):
        for recipe in self.recipes():
            if recipe["id"] == ident:
                return recipe
        raise Problem(404, "Receita não encontrada.")
