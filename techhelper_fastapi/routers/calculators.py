"""Router definitions for calculator endpoints."""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(
	directory=str(Path(__file__).resolve().parent.parent / "templates")
)

router = APIRouter(prefix="/calculators", tags=["calculators"])


@router.get("/", response_class=HTMLResponse)
async def calculators_home(request: Request) -> HTMLResponse:
	"""Render calculators overview page."""
	return templates.TemplateResponse(
		"calculators/index.html",
		{"request": request},
	)
