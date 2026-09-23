from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time

from fastapi.testclient import TestClient
import pytest

from recime.app import create_app
from recime.demo import DEMO_URL, recipe
from recime.models import DraftEdit, ImportRequest
from recime.store import Problem, Store
from recime.worker import exclusive_worker, process_one


@pytest.fixture
def store(tmp_path):
    value = Store(tmp_path / "recipes.sqlite3")
    value.initialize()
    return value


@pytest.fixture
def client(store):
    with TestClient(create_app(store.path)) as value:
        yield value


def submit(client, **extra):
    response = client.post("/api/imports", json={"url": DEMO_URL, **extra})
    assert response.status_code == 202
    return response.json()


def editable(item):
    return {"version": item["version"], "title": item["draft"]["title"],
            "ingredients": [{k: v for k, v in i.items() if k != "evidence"} for i in item["draft"]["ingredients"]],
            "steps": [{k: v for k, v in i.items() if k != "evidence"} for i in item["draft"]["steps"]]}


def ready(client, store):
    item = submit(client)
    assert process_one(store)
    return client.get(f"/api/imports/{item['id']}").json()


def test_end_to_end_persists_and_requires_review(client, store):
    item = submit(client)
    ident = item["id"]
    assert Store(store.path).get(ident)["state"] == "queued"
    assert client.post(f"/api/imports/{ident}/confirm", json={"version": item["version"]}).status_code == 409
    process_one(store)
    item = client.get(f"/api/imports/{ident}").json()
    assert item["state"] == "ready" and item["demo"]
    assert client.get("/api/recipes").json() == []
    body = editable(item)
    body["title"] = "Almoço de domingo"
    body["ingredients"][0]["quantity_text"] = "quantidade corrigida por mim"
    body["steps"][0]["instruction"] = "Minha etapa revisada"
    body["ingredients"].append({"id": None, "name": "Novo item", "quantity_text": None})
    changed = client.patch(f"/api/imports/{ident}/draft", json=body)
    assert changed.status_code == 200
    changed = changed.json()
    assert client.get("/api/recipes").json() == []
    assert changed["original"]["title"] != body["title"]
    assert changed["draft"]["ingredients"][-1]["id"] is not None
    result = client.post(f"/api/imports/{ident}/confirm", json={"version": changed["version"]}).json()
    with TestClient(create_app(store.path)) as restarted:
        found = restarted.get("/api/recipes", params={"query": "ALMOCO"}).json()
        assert len(found) == 1 and found[0]["id"] == result["id"]
        assert found[0]["content"]["steps"][0]["instruction"] == "Minha etapa revisada"
        assert found[0]["source_url"] == DEMO_URL
        assert restarted.get("/api/imports").json() == []
        assert restarted.get(f"/recipes/{result['id']}").status_code == 200


def test_concurrent_duplicates_and_confirmation_are_idempotent(store):
    urls = [DEMO_URL, DEMO_URL + "?igsh=one", DEMO_URL.replace("/p/", "/reel/"), DEMO_URL.replace("/p/", "/reels/")]
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda url: store.submit(ImportRequest(url=url)), urls))
    assert len({row["id"] for row in results}) == 1
    process_one(store)
    item = store.get(results[0]["id"])
    with ThreadPoolExecutor(max_workers=4) as pool:
        confirmed = list(pool.map(lambda _: store.confirm(item["id"], item["version"]), range(4)))
    assert len({row["id"] for row in confirmed}) == 1
    assert len(store.recipes()) == 1
    assert store.submit(ImportRequest(url=DEMO_URL))["state"] == "confirmed"


def test_stale_edit_and_confirm_cannot_overwrite(client, store):
    item = ready(client, store)
    route = f"/api/imports/{item['id']}"
    body = editable(item)
    body["title"] = "A primeira aba salvou"
    assert client.patch(route + "/draft", json=body).status_code == 200
    body["title"] = "Segunda aba atrasada"
    assert client.patch(route + "/draft", json=body).status_code == 409
    assert client.post(route + "/confirm", json={"version": item["version"]}).status_code == 409
    assert client.get(route).json()["draft"]["title"] == "A primeira aba salvou"


def test_evidence_original_attribution_and_warnings_survive_edits(store):
    item = store.submit(ImportRequest(url=DEMO_URL))
    store.claim()
    source = recipe()
    source["author"] = "Autoria de teste"
    evidence = [{"channel": "caption", "observation": "fraldinha", "timestamp_seconds": None}]
    source["ingredients"][0]["evidence"] = evidence
    store.finish(item["id"], draft=source)
    item = store.get(item["id"])
    body = editable(item)
    body["ingredients"] = list(reversed(body["ingredients"]))
    body["ingredients"][-1]["name"] = "Nome corrigido"
    edited = store.edit(item["id"], DraftEdit.model_validate(body))
    assert edited["draft"]["ingredients"][-1]["evidence"] == evidence
    assert edited["original"] == source
    assert edited["draft"]["author"] == source["author"]
    assert edited["draft"]["warnings"] == source["warnings"]


def test_nulls_and_empty_lists_are_allowed(client, store):
    item = ready(client, store)
    route = f"/api/imports/{item['id']}"
    response = client.patch(route + "/draft", json={"version": item["version"], "title": "  ", "ingredients": [], "steps": []})
    item = response.json()
    assert response.status_code == 200 and item["draft"]["title"] is None
    result = client.post(route + "/confirm", json={"version": item["version"]}).json()
    assert "não informado" in client.get(f"/recipes/{result['id']}").text


@pytest.mark.parametrize("url", ["http://instagram.com/p/ABC/", "https://instagram.com.evil.test/p/ABC/",
    "https://user@instagram.com/p/ABC/", "https://instagram.com:bad/p/ABC/", "https://instagram.com/p/ABC/\nextra"])
def test_invalid_urls_do_not_create_imports(client, url):
    assert client.post("/api/imports", json={"url": url}).status_code == 422
    assert client.get("/api/imports").json() == []


def test_arbitrary_valid_url_never_gets_sample(client, store):
    item = submit(client, url="https://www.instagram.com/reel/NOT_THE_SAMPLE/")
    process_one(store)
    item = store.get(item["id"])
    assert item["state"] == "failed" and item["draft"] is None
    assert "Não há amostra" in item["error"]


def test_failure_retry_and_discard_reopen(client, store):
    item = submit(client, demo_scenario="fail_once")
    route = f"/api/imports/{item['id']}"
    process_one(store)
    assert store.get(item["id"])["state"] == "failed"
    assert client.post(route + "/retry").status_code == 200
    process_one(store)
    assert store.get(item["id"])["state"] == "ready"
    assert client.post(route + "/retry").status_code == 409
    assert client.post(route + "/discard").status_code == 200
    assert client.get("/api/imports").json() == []
    reopened = submit(client)
    assert reopened["id"] == item["id"] and reopened["state"] == "queued"
    assert reopened["draft"] is None


def test_claim_is_exclusive_and_processing_cannot_be_discarded(store):
    item = store.submit(ImportRequest(url=DEMO_URL))
    with ThreadPoolExecutor(max_workers=2) as pool:
        claims = list(pool.map(lambda _: store.claim(), range(2)))
    assert sum(claim is not None for claim in claims) == 1
    with pytest.raises(Problem):
        store.transition(item["id"], "discard")
    store.recover()
    assert store.get(item["id"])["state"] == "failed"
    assert store.claim() is None  # No automatic retry after an interruption.


def test_graceful_stop_marks_interrupted(store):
    item = store.submit(ImportRequest(url=DEMO_URL))
    stop = threading.Event()
    stop.set()
    process_one(store, stop=stop)
    assert store.get(item["id"])["state"] == "failed"


def test_executor_lock_and_recovery_after_process_kill(store):
    item = store.submit(ImportRequest(url=DEMO_URL))
    env = {**os.environ, "RECIME_DB": str(store.path), "PYTHONUTF8": "1"}
    root = Path(__file__).resolve().parents[1]
    process = subprocess.Popen([sys.executable, "-m", "recime.worker", "--delay", "120"],
                               cwd=root, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline and store.get(item["id"])["state"] != "processing":
            if process.poll() is not None:
                pytest.fail(process.stderr.read().decode("utf-8", errors="replace"))
            time.sleep(.05)
        assert store.get(item["id"])["state"] == "processing"
        with pytest.raises(RuntimeError, match="Já existe"):
            with exclusive_worker(store.path):
                pass
    finally:
        process.kill()
        process.communicate(timeout=10)
    restart = subprocess.run([sys.executable, "-m", "recime.worker", "--once", "--delay", "0"],
                             cwd=root, env=env, capture_output=True, timeout=15)
    assert restart.returncode == 0, restart.stderr
    assert store.get(item["id"])["state"] == "failed"
    assert store.get(item["id"])["attempts"] == 1


def test_edit_rejects_duplicate_or_forged_items_and_rolls_back(client, store):
    item = ready(client, store)
    body = editable(item)
    body["title"] = "Não deve ser salvo"
    body["ingredients"].append(body["ingredients"][0])
    assert client.patch(f"/api/imports/{item['id']}/draft", json=body).status_code == 422
    assert store.get(item["id"])["draft"] == item["draft"]


def test_local_origin_protection_and_safe_rendering(client, store):
    assert client.post("/api/imports", json={"url": DEMO_URL}, headers={"Origin": "https://evil.test"}).status_code == 403
    assert client.get("/", headers={"Host": "evil.test"}).status_code == 400
    item = ready(client, store)
    body = editable(item)
    body["title"] = '<script>alert("x")</script>'
    result = client.patch(f"/api/imports/{item['id']}/draft", json=body)
    assert result.status_code == 200
    response = client.get(f"/imports/{item['id']}")
    assert response.status_code == 200
    assert '<script>alert("x")</script>' not in response.text
    assert "&lt;script&gt;" in response.text
    assert "script-src 'self'" in response.headers["content-security-policy"]


def test_pages_errors_and_assets(client):
    for path in ("/", "/library", "/static/app.js", "/static/app.css"):
        assert client.get(path).status_code == 200
    assert client.get("/api/imports/missing").status_code == 404
    assert "Importação não encontrada" in client.get("/imports/missing").text
    assert client.get("/recipes/missing").status_code == 404


def test_schema_version_is_checked(store):
    store.initialize()  # Existing schema can be opened again without data loss.
    with store.transaction() as db:
        db.execute("PRAGMA user_version = 99")
    with pytest.raises(RuntimeError, match="mais recente"):
        store.initialize()
