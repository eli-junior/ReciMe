from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.trustedhost import TrustedHostMiddleware

from recime.demo import DEMO_URL
from recime.models import DraftEdit, ImportRequest, Version
from recime.store import Problem, Store, db_path

ROOT = Path(__file__).parent
LABELS = {"queued": "Na fila", "processing": "Preparando receita", "ready": "Pronta para ajustar",
          "failed": "Precisa de atenção", "confirmed": "Na biblioteca", "discarded": "Descartada"}


def create_app(path=None):
    store = Store(path or db_path())

    @asynccontextmanager
    async def lifespan(app):
        store.initialize()
        yield

    app = FastAPI(title="ReciMe — demonstração local", lifespan=lifespan, docs_url=None, redoc_url=None)
    app.state.store = store
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "[::1]", "testserver"])
    app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
    templates = Jinja2Templates(directory=ROOT / "templates")

    @app.middleware("http")
    async def local_browser(request, call_next):
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            origin = request.headers.get("origin")
            if origin and origin != str(request.base_url).rstrip("/"):
                return JSONResponse({"detail": "Envio de outra origem não permitido."}, status_code=403)
            if request.headers.get("sec-fetch-site") == "cross-site":
                return JSONResponse({"detail": "Envio de outra origem não permitido."}, status_code=403)
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        return response

    def page(request, template, **context):
        return templates.TemplateResponse(request=request, name=template,
                                          context={"labels": LABELS, "demo_url": DEMO_URL, **context})

    @app.exception_handler(Problem)
    async def problem(request, exc):
        if request.url.path.startswith("/api/"):
            return JSONResponse({"detail": exc.message}, status_code=exc.status)
        response = page(request, "error.html", title="Não foi possível abrir", message=exc.message)
        response.status_code = exc.status
        return response

    @app.exception_handler(RequestValidationError)
    async def invalid(request, exc):
        return JSONResponse({"detail": "Confira os dados enviados. Use um link https do Instagram em /reel/CODIGO/ ou /p/CODIGO/ e respeite os limites dos campos."}, status_code=422)

    @app.post("/api/imports", status_code=202)
    def submit(body: ImportRequest):
        return store.submit(body)

    @app.get("/api/imports")
    def imports():
        return store.pending()

    @app.get("/api/imports/{ident}")
    def imported(ident: str):
        return store.get(ident)

    @app.patch("/api/imports/{ident}/draft")
    def edit(ident: str, body: DraftEdit):
        return store.edit(ident, body)

    @app.post("/api/imports/{ident}/confirm")
    def confirm(ident: str, body: Version):
        return store.confirm(ident, body.version)

    @app.post("/api/imports/{ident}/retry")
    def retry(ident: str):
        return store.transition(ident, "retry")

    @app.post("/api/imports/{ident}/discard")
    def discard(ident: str):
        return store.transition(ident, "discard")

    @app.get("/api/recipes")
    def recipes(query: str = ""):
        return store.recipes(query)

    @app.get("/api/recipes/{ident}")
    def recipe(ident: str):
        return store.recipe(ident)

    @app.get("/")
    def inbox(request: Request):
        pending = store.pending()
        return page(request, "inbox.html", title="Caixa de entrada", active="inbox", items=pending,
                    ready_count=sum(item["state"] == "ready" for item in pending))

    @app.get("/imports/{ident}")
    def review(request: Request, ident: str):
        item = store.get(ident)
        return page(request, "review.html", title="Ajustar receita", active="inbox", item=item)

    @app.get("/library")
    def library(request: Request, query: str = ""):
        return page(request, "library.html", title="Minha biblioteca", active="library", recipes=store.recipes(query), query=query)

    @app.get("/recipes/{ident}")
    def detail(request: Request, ident: str):
        recipe = store.recipe(ident)
        return page(request, "recipe.html", title=recipe["content"]["title"] or "não informado", active="library", recipe=recipe)

    return app


app = create_app()
