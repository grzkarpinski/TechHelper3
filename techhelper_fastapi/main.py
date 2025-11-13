from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import create_db_and_tables
from .routers import calculators, tools

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="TechHelper")

static_dir = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

templates_dir = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@app.on_event("startup")
async def on_startup() -> None:
	"""Initialize database tables once the application starts."""
	create_db_and_tables()


app.include_router(calculators.router)
app.include_router(tools.router)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request) -> HTMLResponse:
	"""Render the landing page for the application."""
	return templates.TemplateResponse(request, "index.html")
