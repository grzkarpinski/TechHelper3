"""Router definitions for tool management endpoints."""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(
	directory=str(Path(__file__).resolve().parent.parent / "templates")
)

router = APIRouter(prefix="/tools", tags=["tools"])


@router.get("/", response_class=HTMLResponse)
async def tools_home(request: Request) -> HTMLResponse:
	"""Render tools overview page."""
	return templates.TemplateResponse(
		"tools/index.html",
		{"request": request},
	)
