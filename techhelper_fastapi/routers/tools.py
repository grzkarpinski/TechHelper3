"""Router definitions for tool management endpoints."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from ..database import get_session
from ..models.milling_heads import MillingHeads
from ..models.milling_cutters import MillingCutters
from ..models.drills import Drills

templates = Jinja2Templates(
	directory=str(Path(__file__).resolve().parent.parent / "templates")
)

router = APIRouter(prefix="/tools", tags=["tools"])


@router.get("/", response_class=HTMLResponse, name="tools_home")
async def tools_home(request: Request) -> HTMLResponse:
	"""Render tools overview page."""
	return templates.TemplateResponse(request, "tools/index.html")


# ============================================================================
# MILLING HEADS ROUTES
# ============================================================================


@router.get("/milling-heads", response_class=HTMLResponse, name="milling_heads_list")
async def milling_heads_list(
	request: Request,
	session: Session = Depends(get_session),
) -> HTMLResponse:
	"""Render milling heads list page (sorted by diameter ascending)."""
	heads = session.exec(
		select(MillingHeads).order_by(MillingHeads.średnica_D_mm.asc())
	).all()
	return templates.TemplateResponse(
		request,
		"tools/milling_heads_list.html",
		{"heads": heads},
	)


@router.get("/milling-heads/filter", response_class=HTMLResponse, name="milling_heads_filter")
async def milling_heads_filter(
	request: Request,
	search: str = "",
	session: Session = Depends(get_session),
) -> HTMLResponse:
	"""Filter milling heads by diameter, symbol, or manufacturer (HTMX endpoint)."""
	from sqlalchemy import or_

	query = select(MillingHeads)

	# If search term provided, filter across three fields
	if search.strip():
		search_term = f"%{search.strip()}%"
		query = query.where(
			or_(
				MillingHeads.symbol_narzędzia.ilike(search_term),
				MillingHeads.producent.ilike(search_term),
			)
		)
		# Try to parse as float for diameter search
		try:
			diameter_val = float(search.strip())
			query = query.where(MillingHeads.średnica_D_mm == diameter_val)
		except ValueError:
			pass

	# Sort by diameter ascending
	query = query.order_by(MillingHeads.średnica_D_mm.asc())
	heads = session.exec(query).all()
	return templates.TemplateResponse(
		request,
		"tools/partials/milling_heads_table.html",
		{"heads": heads},
	)


@router.get("/milling-heads/add", response_class=HTMLResponse, name="milling_heads_add_form")
async def milling_heads_add_form(request: Request) -> HTMLResponse:
	"""Render milling heads add form page."""
	return templates.TemplateResponse(
		request,
		"tools/milling_heads_form.html",
		{"is_edit": False, "head": None, "errors": []},
	)


@router.get("/milling-heads/{head_id}/edit", response_class=HTMLResponse, name="milling_heads_edit_form")
async def milling_heads_edit_form(
	request: Request,
	head_id: int,
	session: Session = Depends(get_session),
) -> HTMLResponse:
	"""Render milling heads edit form page."""
	head = session.get(MillingHeads, head_id)
	if not head:
		return templates.TemplateResponse(
			request,
			"tools/milling_heads_list.html",
			{"heads": [], "error": "Głowica nie znaleziona"},
			status_code=404,
		)
	return templates.TemplateResponse(
		request,
		"tools/milling_heads_form.html",
		{"is_edit": True, "head": head, "errors": []},
	)


@router.get("/milling-heads/{head_id}/details", response_class=HTMLResponse, name="milling_heads_details")
async def milling_heads_details(
	request: Request,
	head_id: int,
	session: Session = Depends(get_session),
) -> HTMLResponse:
	"""Render milling head details page."""
	head = session.get(MillingHeads, head_id)
	if not head:
		return templates.TemplateResponse(
			request,
			"tools/milling_heads_list.html",
			{"heads": [], "error": "Głowica nie znaleziona"},
			status_code=404,
		)
	return templates.TemplateResponse(
		request,
		"tools/milling_heads_details.html",
		{"head": head},
	)


@router.post("/milling-heads", response_class=HTMLResponse, name="milling_heads_create")
async def milling_heads_create(
	request: Request,
	średnica_D_mm: float = Form(...),
	symbol_narzędzia: str = Form(...),
	liczba_ostrzy: int = Form(...),
	producent: str = Form(default=""),
	symbol_płytki: str = Form(default=""),
	materiał: str = Form(default=""),
	posuw_na_ząb_min: str = Form(default=""),
	posuw_na_ząb_max: str = Form(default=""),
	prędkość_skrawania_min: str = Form(default=""),
	prędkość_skrawania_max: str = Form(default=""),
	obroty: str = Form(default=""),
	posuw: str = Form(default=""),
	głębokość_skrawania_ap: str = Form(default=""),
	uwagi: str = Form(default=""),
	session: Session = Depends(get_session),
):
	"""Create a new milling head."""
	errors: list[str] = []

	# Validate required fields
	if not symbol_narzędzia.strip():
		errors.append("Symbol narzędzia jest wymagany")
	if średnica_D_mm <= 0:
		errors.append("Średnica musi być większa od 0")
	if liczba_ostrzy <= 0:
		errors.append("Liczba ostrzy musi być większa od 0")

	# Validate optional numeric fields
	try:
		posuw_na_ząb_min_val = (
			float(posuw_na_ząb_min) if posuw_na_ząb_min.strip() else None
		)
		if posuw_na_ząb_min_val is not None and posuw_na_ząb_min_val < 0:
			errors.append("Posuw na ząb (min) nie może być ujemny")
	except ValueError:
		errors.append("Posuw na ząb (min) musi być liczbą")

	try:
		posuw_na_ząb_max_val = (
			float(posuw_na_ząb_max) if posuw_na_ząb_max.strip() else None
		)
		if posuw_na_ząb_max_val is not None and posuw_na_ząb_max_val < 0:
			errors.append("Posuw na ząb (max) nie może być ujemny")
	except ValueError:
		errors.append("Posuw na ząb (max) musi być liczbą")

	try:
		prędkość_skrawania_min_val = (
			float(prędkość_skrawania_min) if prędkość_skrawania_min.strip() else None
		)
		if prędkość_skrawania_min_val is not None and prędkość_skrawania_min_val < 0:
			errors.append("Prędkość skrawania (min) nie może być ujemna")
	except ValueError:
		errors.append("Prędkość skrawania (min) musi być liczbą")

	try:
		prędkość_skrawania_max_val = (
			float(prędkość_skrawania_max) if prędkość_skrawania_max.strip() else None
		)
		if prędkość_skrawania_max_val is not None and prędkość_skrawania_max_val < 0:
			errors.append("Prędkość skrawania (max) nie może być ujemna")
	except ValueError:
		errors.append("Prędkość skrawania (max) musi być liczbą")

	try:
		obroty_val = float(obroty) if obroty.strip() else None
		if obroty_val is not None and obroty_val < 0:
			errors.append("Obroty nie mogą być ujemne")
	except ValueError:
		errors.append("Obroty muszą być liczbą")

	try:
		posuw_val = float(posuw) if posuw.strip() else None
		if posuw_val is not None and posuw_val < 0:
			errors.append("Posuw nie może być ujemny")
	except ValueError:
		errors.append("Posuw musi być liczbą")

	try:
		głębokość_skrawania_ap_val = (
			float(głębokość_skrawania_ap) if głębokość_skrawania_ap.strip() else None
		)
		if (
			głębokość_skrawania_ap_val is not None
			and głębokość_skrawania_ap_val < 0
		):
			errors.append("Głębokość skrawania nie może być ujemna")
	except ValueError:
		errors.append("Głębokość skrawania musi być liczbą")

	if errors:
		return templates.TemplateResponse(
			request,
			"tools/milling_heads_form.html",
			{
				"is_edit": False,
				"head": None,
				"errors": errors,
				"form_data": {
					"średnica_D_mm": średnica_D_mm,
					"symbol_narzędzia": symbol_narzędzia,
					"liczba_ostrzy": liczba_ostrzy,
					"producent": producent,
					"symbol_płytki": symbol_płytki,
					"materiał": materiał,
					"posuw_na_ząb_min": posuw_na_ząb_min,
					"posuw_na_ząb_max": posuw_na_ząb_max,
					"prędkość_skrawania_min": prędkość_skrawania_min,
					"prędkość_skrawania_max": prędkość_skrawania_max,
					"obroty": obroty,
					"posuw": posuw,
					"głębokość_skrawania_ap": głębokość_skrawania_ap,
					"uwagi": uwagi,
				},
			},
			status_code=status.HTTP_400_BAD_REQUEST,
		)

	# Create new record
	head = MillingHeads(
		średnica_D_mm=średnica_D_mm,
		symbol_narzędzia=symbol_narzędzia,
		liczba_ostrzy=liczba_ostrzy,
		producent=producent if producent.strip() else None,
		symbol_płytki=symbol_płytki if symbol_płytki.strip() else None,
		materiał=materiał if materiał.strip() else None,
		posuw_na_ząb_min=posuw_na_ząb_min_val,
		posuw_na_ząb_max=posuw_na_ząb_max_val,
		prędkość_skrawania_min=prędkość_skrawania_min_val,
		prędkość_skrawania_max=prędkość_skrawania_max_val,
		obroty=obroty_val,
		posuw=posuw_val,
		głębokość_skrawania_ap=głębokość_skrawania_ap_val,
		uwagi=uwagi if uwagi.strip() else None,
	)
	session.add(head)
	session.commit()
	session.refresh(head)

	return RedirectResponse(url="/tools/milling-heads", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/milling-heads/{head_id}", response_class=HTMLResponse, name="milling_heads_update")
async def milling_heads_update(
	request: Request,
	head_id: int,
	średnica_D_mm: float = Form(...),
	symbol_narzędzia: str = Form(...),
	liczba_ostrzy: int = Form(...),
	producent: str = Form(default=""),
	symbol_płytki: str = Form(default=""),
	materiał: str = Form(default=""),
	posuw_na_ząb_min: str = Form(default=""),
	posuw_na_ząb_max: str = Form(default=""),
	prędkość_skrawania_min: str = Form(default=""),
	prędkość_skrawania_max: str = Form(default=""),
	obroty: str = Form(default=""),
	posuw: str = Form(default=""),
	głębokość_skrawania_ap: str = Form(default=""),
	uwagi: str = Form(default=""),
	session: Session = Depends(get_session),
):
	"""Update an existing milling head."""
	head = session.get(MillingHeads, head_id)
	if not head:
		return templates.TemplateResponse(
			request,
			"tools/milling_heads_list.html",
			{"heads": [], "error": "Głowica nie znaleziona"},
			status_code=404,
		)

	errors: list[str] = []

	# Validate required fields
	if not symbol_narzędzia.strip():
		errors.append("Symbol narzędzia jest wymagany")
	if średnica_D_mm <= 0:
		errors.append("Średnica musi być większa od 0")
	if liczba_ostrzy <= 0:
		errors.append("Liczba ostrzy musi być większa od 0")

	# Validate optional numeric fields (same as create)
	try:
		posuw_na_ząb_min_val = (
			float(posuw_na_ząb_min) if posuw_na_ząb_min.strip() else None
		)
		if posuw_na_ząb_min_val is not None and posuw_na_ząb_min_val < 0:
			errors.append("Posuw na ząb (min) nie może być ujemny")
	except ValueError:
		errors.append("Posuw na ząb (min) musi być liczbą")

	try:
		posuw_na_ząb_max_val = (
			float(posuw_na_ząb_max) if posuw_na_ząb_max.strip() else None
		)
		if posuw_na_ząb_max_val is not None and posuw_na_ząb_max_val < 0:
			errors.append("Posuw na ząb (max) nie może być ujemny")
	except ValueError:
		errors.append("Posuw na ząb (max) musi być liczbą")

	try:
		prędkość_skrawania_min_val = (
			float(prędkość_skrawania_min) if prędkość_skrawania_min.strip() else None
		)
		if prędkość_skrawania_min_val is not None and prędkość_skrawania_min_val < 0:
			errors.append("Prędkość skrawania (min) nie może być ujemna")
	except ValueError:
		errors.append("Prędkość skrawania (min) musi być liczbą")

	try:
		prędkość_skrawania_max_val = (
			float(prędkość_skrawania_max) if prędkość_skrawania_max.strip() else None
		)
		if prędkość_skrawania_max_val is not None and prędkość_skrawania_max_val < 0:
			errors.append("Prędkość skrawania (max) nie może być ujemna")
	except ValueError:
		errors.append("Prędkość skrawania (max) musi być liczbą")

	try:
		obroty_val = float(obroty) if obroty.strip() else None
		if obroty_val is not None and obroty_val < 0:
			errors.append("Obroty nie mogą być ujemne")
	except ValueError:
		errors.append("Obroty muszą być liczbą")

	try:
		posuw_val = float(posuw) if posuw.strip() else None
		if posuw_val is not None and posuw_val < 0:
			errors.append("Posuw nie może być ujemny")
	except ValueError:
		errors.append("Posuw musi być liczbą")

	try:
		głębokość_skrawania_ap_val = (
			float(głębokość_skrawania_ap) if głębokość_skrawania_ap.strip() else None
		)
		if (
			głębokość_skrawania_ap_val is not None
			and głębokość_skrawania_ap_val < 0
		):
			errors.append("Głębokość skrawania nie może być ujemna")
	except ValueError:
		errors.append("Głębokość skrawania musi być liczbą")

	if errors:
		return templates.TemplateResponse(
			request,
			"tools/milling_heads_form.html",
			{
				"is_edit": True,
				"head": head,
				"errors": errors,
				"form_data": {
					"średnica_D_mm": średnica_D_mm,
					"symbol_narzędzia": symbol_narzędzia,
					"liczba_ostrzy": liczba_ostrzy,
					"producent": producent,
					"symbol_płytki": symbol_płytki,
					"materiał": materiał,
					"posuw_na_ząb_min": posuw_na_ząb_min,
					"posuw_na_ząb_max": posuw_na_ząb_max,
					"prędkość_skrawania_min": prędkość_skrawania_min,
					"prędkość_skrawania_max": prędkość_skrawania_max,
					"obroty": obroty,
					"posuw": posuw,
					"głębokość_skrawania_ap": głębokość_skrawania_ap,
					"uwagi": uwagi,
				},
			},
			status_code=status.HTTP_400_BAD_REQUEST,
		)

	# Update existing record
	head.średnica_D_mm = średnica_D_mm
	head.symbol_narzędzia = symbol_narzędzia
	head.liczba_ostrzy = liczba_ostrzy
	head.producent = producent if producent.strip() else None
	head.symbol_płytki = symbol_płytki if symbol_płytki.strip() else None
	head.materiał = materiał if materiał.strip() else None
	head.posuw_na_ząb_min = posuw_na_ząb_min_val
	head.posuw_na_ząb_max = posuw_na_ząb_max_val
	head.prędkość_skrawania_min = prędkość_skrawania_min_val
	head.prędkość_skrawania_max = prędkość_skrawania_max_val
	head.obroty = obroty_val
	head.posuw = posuw_val
	head.głębokość_skrawania_ap = głębokość_skrawania_ap_val
	head.uwagi = uwagi if uwagi.strip() else None

	session.add(head)
	session.commit()

	return RedirectResponse(url="/tools/milling-heads", status_code=status.HTTP_303_SEE_OTHER)


@router.delete("/milling-heads/{head_id}", name="milling_heads_delete")
async def milling_heads_delete(
	head_id: int,
	session: Session = Depends(get_session),
) -> RedirectResponse:
	"""Delete a milling head."""
	head = session.get(MillingHeads, head_id)
	if head:
		session.delete(head)
		session.commit()

	return RedirectResponse(url="/tools/milling-heads", status_code=status.HTTP_303_SEE_OTHER)


# ============================================================================
# MILLING CUTTERS ROUTES
# ============================================================================


@router.get("/milling-cutters", response_class=HTMLResponse, name="milling_cutters_list")
async def milling_cutters_list(
	request: Request,
	session: Session = Depends(get_session),
) -> HTMLResponse:
	"""Render milling cutters list page (sorted by diameter ascending)."""
	cutters = session.exec(
		select(MillingCutters).order_by(MillingCutters.średnica_D_mm.asc())
	).all()
	return templates.TemplateResponse(
		request,
		"tools/milling_cutters_list.html",
		{"cutters": cutters},
	)


@router.get("/milling-cutters/filter", response_class=HTMLResponse, name="milling_cutters_filter")
async def milling_cutters_filter(
	request: Request,
	search: str = "",
	session: Session = Depends(get_session),
) -> HTMLResponse:
	"""Filter milling cutters by diameter, symbol, or manufacturer (HTMX endpoint)."""
	from sqlalchemy import or_

	query = select(MillingCutters)

	# If search term provided, filter across three fields
	if search.strip():
		search_term = f"%{search.strip()}%"
		query = query.where(
			or_(
				MillingCutters.symbol_narzędzia.ilike(search_term),
				MillingCutters.producent.ilike(search_term),
			)
		)
		# Try to parse as float for diameter search
		try:
			diameter_val = float(search.strip())
			query = query.where(MillingCutters.średnica_D_mm == diameter_val)
		except ValueError:
			pass

	# Sort by diameter ascending
	query = query.order_by(MillingCutters.średnica_D_mm.asc())
	cutters = session.exec(query).all()
	return templates.TemplateResponse(
		request,
		"tools/partials/milling_cutters_table.html",
		{"cutters": cutters},
	)


@router.get("/milling-cutters/add", response_class=HTMLResponse, name="milling_cutters_add_form")
async def milling_cutters_add_form(request: Request) -> HTMLResponse:
	"""Render milling cutters add form page."""
	return templates.TemplateResponse(
		request,
		"tools/milling_cutters_form.html",
		{"is_edit": False, "cutter": None, "errors": []},
	)


@router.get("/milling-cutters/{cutter_id}/edit", response_class=HTMLResponse, name="milling_cutters_edit_form")
async def milling_cutters_edit_form(
	request: Request,
	cutter_id: int,
	session: Session = Depends(get_session),
) -> HTMLResponse:
	"""Render milling cutters edit form page."""
	cutter = session.get(MillingCutters, cutter_id)
	if not cutter:
		return templates.TemplateResponse(
			request,
			"tools/milling_cutters_list.html",
			{"cutters": [], "error": "Frez nie znaleziony"},
			status_code=404,
		)
	return templates.TemplateResponse(
		request,
		"tools/milling_cutters_form.html",
		{"is_edit": True, "cutter": cutter, "errors": []},
	)


@router.get("/milling-cutters/{cutter_id}/details", response_class=HTMLResponse, name="milling_cutters_details")
async def milling_cutters_details(
	request: Request,
	cutter_id: int,
	session: Session = Depends(get_session),
) -> HTMLResponse:
	"""Render milling cutter details page."""
	cutter = session.get(MillingCutters, cutter_id)
	if not cutter:
		return templates.TemplateResponse(
			request,
			"tools/milling_cutters_list.html",
			{"cutters": [], "error": "Frez nie znaleziony"},
			status_code=404,
		)
	return templates.TemplateResponse(
		request,
		"tools/milling_cutters_details.html",
		{"cutter": cutter},
	)


@router.post("/milling-cutters", response_class=HTMLResponse, name="milling_cutters_create")
async def milling_cutters_create(
	request: Request,
	średnica_D_mm: float = Form(...),
	symbol_narzędzia: str = Form(...),
	liczba_ostrzy: int = Form(...),
	producent: str = Form(default=""),
	materiał: str = Form(default=""),
	posuw_na_ząb_min: str = Form(default=""),
	posuw_na_ząb_max: str = Form(default=""),
	prędkość_skrawania_min: str = Form(default=""),
	prędkość_skrawania_max: str = Form(default=""),
	obroty: str = Form(default=""),
	posuw: str = Form(default=""),
	głębokość_skrawania_ap: str = Form(default=""),
	szerokość_skrawania_ae_procent: str = Form(default=""),
	uwagi: str = Form(default=""),
	session: Session = Depends(get_session),
):
	"""Create a new milling cutter."""
	errors: list[str] = []

	# Validate required fields
	if not symbol_narzędzia.strip():
		errors.append("Symbol narzędzia jest wymagany")
	if średnica_D_mm <= 0:
		errors.append("Średnica musi być większa od 0")
	if liczba_ostrzy <= 0:
		errors.append("Liczba ostrzy musi być większa od 0")

	# Validate optional numeric fields
	try:
		posuw_na_ząb_min_val = (
			float(posuw_na_ząb_min) if posuw_na_ząb_min.strip() else None
		)
		if posuw_na_ząb_min_val is not None and posuw_na_ząb_min_val < 0:
			errors.append("Posuw na ząb (min) nie może być ujemny")
	except ValueError:
		errors.append("Posuw na ząb (min) musi być liczbą")

	try:
		posuw_na_ząb_max_val = (
			float(posuw_na_ząb_max) if posuw_na_ząb_max.strip() else None
		)
		if posuw_na_ząb_max_val is not None and posuw_na_ząb_max_val < 0:
			errors.append("Posuw na ząb (max) nie może być ujemny")
	except ValueError:
		errors.append("Posuw na ząb (max) musi być liczbą")

	try:
		prędkość_skrawania_min_val = (
			float(prędkość_skrawania_min) if prędkość_skrawania_min.strip() else None
		)
		if prędkość_skrawania_min_val is not None and prędkość_skrawania_min_val < 0:
			errors.append("Prędkość skrawania (min) nie może być ujemna")
	except ValueError:
		errors.append("Prędkość skrawania (min) musi być liczbą")

	try:
		prędkość_skrawania_max_val = (
			float(prędkość_skrawania_max) if prędkość_skrawania_max.strip() else None
		)
		if prędkość_skrawania_max_val is not None and prędkość_skrawania_max_val < 0:
			errors.append("Prędkość skrawania (max) nie może być ujemna")
	except ValueError:
		errors.append("Prędkość skrawania (max) musi być liczbą")

	try:
		obroty_val = float(obroty) if obroty.strip() else None
		if obroty_val is not None and obroty_val < 0:
			errors.append("Obroty nie mogą być ujemne")
	except ValueError:
		errors.append("Obroty muszą być liczbą")

	try:
		posuw_val = float(posuw) if posuw.strip() else None
		if posuw_val is not None and posuw_val < 0:
			errors.append("Posuw nie może być ujemny")
	except ValueError:
		errors.append("Posuw musi być liczbą")

	try:
		głębokość_skrawania_ap_val = (
			float(głębokość_skrawania_ap) if głębokość_skrawania_ap.strip() else None
		)
		if (
			głębokość_skrawania_ap_val is not None
			and głębokość_skrawania_ap_val < 0
		):
			errors.append("Głębokość skrawania nie może być ujemna")
	except ValueError:
		errors.append("Głębokość skrawania musi być liczbą")

	try:
		szerokość_skrawania_ae_procent_val = (
			float(szerokość_skrawania_ae_procent) if szerokość_skrawania_ae_procent.strip() else None
		)
		if (
			szerokość_skrawania_ae_procent_val is not None
			and szerokość_skrawania_ae_procent_val < 0
		):
			errors.append("Szerokość skrawania nie może być ujemna")
	except ValueError:
		errors.append("Szerokość skrawania musi być liczbą")

	if errors:
		return templates.TemplateResponse(
			request,
			"tools/milling_cutters_form.html",
			{
				"is_edit": False,
				"cutter": None,
				"errors": errors,
				"form_data": {
					"średnica_D_mm": średnica_D_mm,
					"symbol_narzędzia": symbol_narzędzia,
					"liczba_ostrzy": liczba_ostrzy,
					"producent": producent,
					"materiał": materiał,
					"posuw_na_ząb_min": posuw_na_ząb_min,
					"posuw_na_ząb_max": posuw_na_ząb_max,
					"prędkość_skrawania_min": prędkość_skrawania_min,
					"prędkość_skrawania_max": prędkość_skrawania_max,
					"obroty": obroty,
					"posuw": posuw,
					"głębokość_skrawania_ap": głębokość_skrawania_ap,
					"szerokość_skrawania_ae_procent": szerokość_skrawania_ae_procent,
					"uwagi": uwagi,
				},
			},
			status_code=status.HTTP_400_BAD_REQUEST,
		)

	# Create new record
	cutter = MillingCutters(
		średnica_D_mm=średnica_D_mm,
		symbol_narzędzia=symbol_narzędzia,
		liczba_ostrzy=liczba_ostrzy,
		producent=producent if producent.strip() else None,
		materiał=materiał if materiał.strip() else None,
		posuw_na_ząb_min=posuw_na_ząb_min_val,
		posuw_na_ząb_max=posuw_na_ząb_max_val,
		prędkość_skrawania_min=prędkość_skrawania_min_val,
		prędkość_skrawania_max=prędkość_skrawania_max_val,
		obroty=obroty_val,
		posuw=posuw_val,
		głębokość_skrawania_ap=głębokość_skrawania_ap_val,
		szerokość_skrawania_ae_procent=szerokość_skrawania_ae_procent_val,
		uwagi=uwagi if uwagi.strip() else None,
	)
	session.add(cutter)
	session.commit()
	session.refresh(cutter)

	return RedirectResponse(url="/tools/milling-cutters", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/milling-cutters/{cutter_id}", response_class=HTMLResponse, name="milling_cutters_update")
async def milling_cutters_update(
	request: Request,
	cutter_id: int,
	średnica_D_mm: float = Form(...),
	symbol_narzędzia: str = Form(...),
	liczba_ostrzy: int = Form(...),
	producent: str = Form(default=""),
	materiał: str = Form(default=""),
	posuw_na_ząb_min: str = Form(default=""),
	posuw_na_ząb_max: str = Form(default=""),
	prędkość_skrawania_min: str = Form(default=""),
	prędkość_skrawania_max: str = Form(default=""),
	obroty: str = Form(default=""),
	posuw: str = Form(default=""),
	głębokość_skrawania_ap: str = Form(default=""),
	szerokość_skrawania_ae_procent: str = Form(default=""),
	uwagi: str = Form(default=""),
	session: Session = Depends(get_session),
):
	"""Update an existing milling cutter."""
	cutter = session.get(MillingCutters, cutter_id)
	if not cutter:
		return templates.TemplateResponse(
			request,
			"tools/milling_cutters_list.html",
			{"cutters": [], "error": "Frez nie znaleziony"},
			status_code=404,
		)

	errors: list[str] = []

	# Validate required fields
	if not symbol_narzędzia.strip():
		errors.append("Symbol narzędzia jest wymagany")
	if średnica_D_mm <= 0:
		errors.append("Średnica musi być większa od 0")
	if liczba_ostrzy <= 0:
		errors.append("Liczba ostrzy musi być większa od 0")

	# Validate optional numeric fields (same as create)
	try:
		posuw_na_ząb_min_val = (
			float(posuw_na_ząb_min) if posuw_na_ząb_min.strip() else None
		)
		if posuw_na_ząb_min_val is not None and posuw_na_ząb_min_val < 0:
			errors.append("Posuw na ząb (min) nie może być ujemny")
	except ValueError:
		errors.append("Posuw na ząb (min) musi być liczbą")

	try:
		posuw_na_ząb_max_val = (
			float(posuw_na_ząb_max) if posuw_na_ząb_max.strip() else None
		)
		if posuw_na_ząb_max_val is not None and posuw_na_ząb_max_val < 0:
			errors.append("Posuw na ząb (max) nie może być ujemny")
	except ValueError:
		errors.append("Posuw na ząb (max) musi być liczbą")

	try:
		prędkość_skrawania_min_val = (
			float(prędkość_skrawania_min) if prędkość_skrawania_min.strip() else None
		)
		if prędkość_skrawania_min_val is not None and prędkość_skrawania_min_val < 0:
			errors.append("Prędkość skrawania (min) nie może być ujemna")
	except ValueError:
		errors.append("Prędkość skrawania (min) musi być liczbą")

	try:
		prędkość_skrawania_max_val = (
			float(prędkość_skrawania_max) if prędkość_skrawania_max.strip() else None
		)
		if prędkość_skrawania_max_val is not None and prędkość_skrawania_max_val < 0:
			errors.append("Prędkość skrawania (max) nie może być ujemna")
	except ValueError:
		errors.append("Prędkość skrawania (max) musi być liczbą")

	try:
		obroty_val = float(obroty) if obroty.strip() else None
		if obroty_val is not None and obroty_val < 0:
			errors.append("Obroty nie mogą być ujemne")
	except ValueError:
		errors.append("Obroty muszą być liczbą")

	try:
		posuw_val = float(posuw) if posuw.strip() else None
		if posuw_val is not None and posuw_val < 0:
			errors.append("Posuw nie może być ujemny")
	except ValueError:
		errors.append("Posuw musi być liczbą")

	try:
		głębokość_skrawania_ap_val = (
			float(głębokość_skrawania_ap) if głębokość_skrawania_ap.strip() else None
		)
		if (
			głębokość_skrawania_ap_val is not None
			and głębokość_skrawania_ap_val < 0
		):
			errors.append("Głębokość skrawania nie może być ujemna")
	except ValueError:
		errors.append("Głębokość skrawania musi być liczbą")

	try:
		szerokość_skrawania_ae_procent_val = (
			float(szerokość_skrawania_ae_procent) if szerokość_skrawania_ae_procent.strip() else None
		)
		if (
			szerokość_skrawania_ae_procent_val is not None
			and szerokość_skrawania_ae_procent_val < 0
		):
			errors.append("Szerokość skrawania nie może być ujemna")
	except ValueError:
		errors.append("Szerokość skrawania musi być liczbą")

	if errors:
		return templates.TemplateResponse(
			request,
			"tools/milling_cutters_form.html",
			{
				"is_edit": True,
				"cutter": cutter,
				"errors": errors,
				"form_data": {
					"średnica_D_mm": średnica_D_mm,
					"symbol_narzędzia": symbol_narzędzia,
					"liczba_ostrzy": liczba_ostrzy,
					"producent": producent,
					"materiał": materiał,
					"posuw_na_ząb_min": posuw_na_ząb_min,
					"posuw_na_ząb_max": posuw_na_ząb_max,
					"prędkość_skrawania_min": prędkość_skrawania_min,
					"prędkość_skrawania_max": prędkość_skrawania_max,
					"obroty": obroty,
					"posuw": posuw,
					"głębokość_skrawania_ap": głębokość_skrawania_ap,
					"szerokość_skrawania_ae_procent": szerokość_skrawania_ae_procent,
					"uwagi": uwagi,
				},
			},
			status_code=status.HTTP_400_BAD_REQUEST,
		)

	# Update existing record
	cutter.średnica_D_mm = średnica_D_mm
	cutter.symbol_narzędzia = symbol_narzędzia
	cutter.liczba_ostrzy = liczba_ostrzy
	cutter.producent = producent if producent.strip() else None
	cutter.materiał = materiał if materiał.strip() else None
	cutter.posuw_na_ząb_min = posuw_na_ząb_min_val
	cutter.posuw_na_ząb_max = posuw_na_ząb_max_val
	cutter.prędkość_skrawania_min = prędkość_skrawania_min_val
	cutter.prędkość_skrawania_max = prędkość_skrawania_max_val
	cutter.obroty = obroty_val
	cutter.posuw = posuw_val
	cutter.głębokość_skrawania_ap = głębokość_skrawania_ap_val
	cutter.szerokość_skrawania_ae_procent = szerokość_skrawania_ae_procent_val
	cutter.uwagi = uwagi if uwagi.strip() else None

	session.add(cutter)
	session.commit()

	return RedirectResponse(url="/tools/milling-cutters", status_code=status.HTTP_303_SEE_OTHER)


@router.delete("/milling-cutters/{cutter_id}", name="milling_cutters_delete")
async def milling_cutters_delete(
	cutter_id: int,
	session: Session = Depends(get_session),
) -> RedirectResponse:
	"""Delete a milling cutter."""
	cutter = session.get(MillingCutters, cutter_id)
	if cutter:
		session.delete(cutter)
		session.commit()

	return RedirectResponse(url="/tools/milling-cutters", status_code=status.HTTP_303_SEE_OTHER)


# ============================================================================
# DRILLS ENDPOINTS
# ============================================================================


@router.get("/drills", response_class=HTMLResponse, name="drills_list")
async def drills_list(
	request: Request,
	session: Session = Depends(get_session),
) -> str:
	"""List all drills, sorted by diameter ascending."""
	drills = session.exec(select(Drills).order_by(Drills.średnica_D_mm.asc())).all()
	return templates.TemplateResponse(
		request,
		"tools/drills_list.html",
		{"drills": drills},
	)


@router.get("/drills/filter", response_class=HTMLResponse, name="drills_filter")
async def drills_filter(
	request: Request,
	search: str = "",
	session: Session = Depends(get_session),
) -> str:
	"""Filter drills by symbol, manufacturer, or diameter."""
	query = select(Drills)

	if search:
		from sqlalchemy import or_

		query = query.where(
			or_(
				Drills.symbol_narzędzia.ilike(f"%{search}%"),
				Drills.producent.ilike(f"%{search}%"),
			)
		)

	drills = session.exec(query.order_by(Drills.średnica_D_mm.asc())).all()
	return templates.TemplateResponse(
		request,
		"tools/partials/drills_table.html",
		{"drills": drills},
	)


@router.get("/drills/add", response_class=HTMLResponse, name="drills_add_form")
async def drills_add_form(request: Request) -> str:
	"""Get the add drill form."""
	return templates.TemplateResponse(
		request,
		"tools/drills_form.html",
		{"is_edit": False, "drill": None},
	)


@router.get("/drills/{drill_id}/edit", response_class=HTMLResponse, name="drills_edit_form")
async def drills_edit_form(
	request: Request,
	drill_id: int,
	session: Session = Depends(get_session),
) -> Any:
	"""Get the edit drill form."""
	drill = session.get(Drills, drill_id)
	if not drill:
		return templates.TemplateResponse(
			request,
			"tools/drills_list.html",
			{"drills": [], "error": "Wiertło nie znalezione"},
			status_code=404,
		)
	return templates.TemplateResponse(
		request,
		"tools/drills_form.html",
		{"is_edit": True, "drill": drill},
	)


@router.get("/drills/{drill_id}/details", response_class=HTMLResponse, name="drills_details")
async def drills_details(
	request: Request,
	drill_id: int,
	session: Session = Depends(get_session),
) -> Any:
	"""Get details for a specific drill."""
	drill = session.get(Drills, drill_id)
	if not drill:
		return templates.TemplateResponse(
			request,
			"tools/drills_list.html",
			{"drills": [], "error": "Wiertło nie znalezione"},
			status_code=404,
		)
	return templates.TemplateResponse(
		request,
		"tools/drills_details.html",
		{"drill": drill},
	)


@router.post("/drills", response_class=HTMLResponse, name="drills_create")
async def drills_create(
	request: Request,
	średnica_D_mm: float = Form(...),
	symbol_narzędzia: str = Form(...),
	rodzaj_wiertła: str = Form(...),
	producent: str = Form(default=""),
	symbol_płytki: str = Form(default=""),
	długość_robocza_mm: str = Form(default=""),
	liczba_ostrzy: str = Form(default=""),
	posuw_fn_min: str = Form(default=""),
	posuw_fn_max: str = Form(default=""),
	prędkość_skrawania_min: str = Form(default=""),
	prędkość_skrawania_max: str = Form(default=""),
	obroty: str = Form(default=""),
	posuw: str = Form(default=""),
	uwagi: str = Form(default=""),
	session: Session = Depends(get_session),
):
	"""Create a new drill."""
	errors: list[str] = []

	# Validate required fields
	if not symbol_narzędzia.strip():
		errors.append("Symbol narzędzia jest wymagany")
	if średnica_D_mm <= 0:
		errors.append("Średnica musi być większa od 0")
	if not rodzaj_wiertła.strip():
		errors.append("Rodzaj wiertła jest wymagany")

	# Validate optional numeric fields
	try:
		długość_robocza_mm_val = (
			float(długość_robocza_mm) if długość_robocza_mm.strip() else None
		)
		if długość_robocza_mm_val is not None and długość_robocza_mm_val < 0:
			errors.append("Długość robocza nie może być ujemna")
	except ValueError:
		errors.append("Długość robocza musi być liczbą")

	try:
		liczba_ostrzy_val = (
			int(liczba_ostrzy) if liczba_ostrzy.strip() else None
		)
		if liczba_ostrzy_val is not None and liczba_ostrzy_val < 0:
			errors.append("Liczba ostrzy nie może być ujemna")
	except ValueError:
		errors.append("Liczba ostrzy musi być liczbą całkowitą")

	try:
		posuw_fn_min_val = (
			float(posuw_fn_min) if posuw_fn_min.strip() else None
		)
		if posuw_fn_min_val is not None and posuw_fn_min_val < 0:
			errors.append("Posuw fn (min) nie może być ujemny")
	except ValueError:
		errors.append("Posuw fn (min) musi być liczbą")

	try:
		posuw_fn_max_val = (
			float(posuw_fn_max) if posuw_fn_max.strip() else None
		)
		if posuw_fn_max_val is not None and posuw_fn_max_val < 0:
			errors.append("Posuw fn (max) nie może być ujemny")
	except ValueError:
		errors.append("Posuw fn (max) musi być liczbą")

	try:
		prędkość_skrawania_min_val = (
			float(prędkość_skrawania_min) if prędkość_skrawania_min.strip() else None
		)
		if prędkość_skrawania_min_val is not None and prędkość_skrawania_min_val < 0:
			errors.append("Prędkość skrawania (min) nie może być ujemna")
	except ValueError:
		errors.append("Prędkość skrawania (min) musi być liczbą")

	try:
		prędkość_skrawania_max_val = (
			float(prędkość_skrawania_max) if prędkość_skrawania_max.strip() else None
		)
		if prędkość_skrawania_max_val is not None and prędkość_skrawania_max_val < 0:
			errors.append("Prędkość skrawania (max) nie może być ujemna")
	except ValueError:
		errors.append("Prędkość skrawania (max) musi być liczbą")

	try:
		obroty_val = float(obroty) if obroty.strip() else None
		if obroty_val is not None and obroty_val < 0:
			errors.append("Obroty nie mogą być ujemne")
	except ValueError:
		errors.append("Obroty muszą być liczbą")

	try:
		posuw_val = float(posuw) if posuw.strip() else None
		if posuw_val is not None and posuw_val < 0:
			errors.append("Posuw nie może być ujemny")
	except ValueError:
		errors.append("Posuw musi być liczbą")

	if errors:
		return templates.TemplateResponse(
			request,
			"tools/drills_form.html",
			{
				"is_edit": False,
				"drill": None,
				"errors": errors,
				"form_data": {
					"średnica_D_mm": średnica_D_mm,
					"symbol_narzędzia": symbol_narzędzia,
					"rodzaj_wiertła": rodzaj_wiertła,
					"producent": producent,
					"symbol_płytki": symbol_płytki,
					"długość_robocza_mm": długość_robocza_mm,
					"liczba_ostrzy": liczba_ostrzy,
					"posuw_fn_min": posuw_fn_min,
					"posuw_fn_max": posuw_fn_max,
					"prędkość_skrawania_min": prędkość_skrawania_min,
					"prędkość_skrawania_max": prędkość_skrawania_max,
					"obroty": obroty,
					"posuw": posuw,
					"uwagi": uwagi,
				},
			},
			status_code=status.HTTP_400_BAD_REQUEST,
		)

	# Create new record
	drill = Drills(
		średnica_D_mm=średnica_D_mm,
		symbol_narzędzia=symbol_narzędzia,
		rodzaj_wiertła=rodzaj_wiertła,
		producent=producent if producent.strip() else None,
		symbol_płytki=symbol_płytki if symbol_płytki.strip() else None,
		długość_robocza_mm=długość_robocza_mm_val,
		liczba_ostrzy=liczba_ostrzy_val,
		posuw_fn_min=posuw_fn_min_val,
		posuw_fn_max=posuw_fn_max_val,
		prędkość_skrawania_min=prędkość_skrawania_min_val,
		prędkość_skrawania_max=prędkość_skrawania_max_val,
		obroty=obroty_val,
		posuw=posuw_val,
		uwagi=uwagi if uwagi.strip() else None,
	)
	session.add(drill)
	session.commit()
	session.refresh(drill)

	return RedirectResponse(url="/tools/drills", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/drills/{drill_id}", response_class=HTMLResponse, name="drills_update")
async def drills_update(
	request: Request,
	drill_id: int,
	średnica_D_mm: float = Form(...),
	symbol_narzędzia: str = Form(...),
	rodzaj_wiertła: str = Form(...),
	producent: str = Form(default=""),
	symbol_płytki: str = Form(default=""),
	długość_robocza_mm: str = Form(default=""),
	liczba_ostrzy: str = Form(default=""),
	posuw_fn_min: str = Form(default=""),
	posuw_fn_max: str = Form(default=""),
	prędkość_skrawania_min: str = Form(default=""),
	prędkość_skrawania_max: str = Form(default=""),
	obroty: str = Form(default=""),
	posuw: str = Form(default=""),
	uwagi: str = Form(default=""),
	session: Session = Depends(get_session),
):
	"""Update an existing drill."""
	drill = session.get(Drills, drill_id)
	if not drill:
		return templates.TemplateResponse(
			request,
			"tools/drills_list.html",
			{"drills": [], "error": "Wiertło nie znalezione"},
			status_code=404,
		)

	errors: list[str] = []

	# Validate required fields
	if not symbol_narzędzia.strip():
		errors.append("Symbol narzędzia jest wymagany")
	if średnica_D_mm <= 0:
		errors.append("Średnica musi być większa od 0")
	if not rodzaj_wiertła.strip():
		errors.append("Rodzaj wiertła jest wymagany")

	# Validate optional numeric fields (same as create)
	try:
		długość_robocza_mm_val = (
			float(długość_robocza_mm) if długość_robocza_mm.strip() else None
		)
		if długość_robocza_mm_val is not None and długość_robocza_mm_val < 0:
			errors.append("Długość robocza nie może być ujemna")
	except ValueError:
		errors.append("Długość robocza musi być liczbą")

	try:
		liczba_ostrzy_val = (
			int(liczba_ostrzy) if liczba_ostrzy.strip() else None
		)
		if liczba_ostrzy_val is not None and liczba_ostrzy_val < 0:
			errors.append("Liczba ostrzy nie może być ujemna")
	except ValueError:
		errors.append("Liczba ostrzy musi być liczbą całkowitą")

	try:
		posuw_fn_min_val = (
			float(posuw_fn_min) if posuw_fn_min.strip() else None
		)
		if posuw_fn_min_val is not None and posuw_fn_min_val < 0:
			errors.append("Posuw fn (min) nie może być ujemny")
	except ValueError:
		errors.append("Posuw fn (min) musi być liczbą")

	try:
		posuw_fn_max_val = (
			float(posuw_fn_max) if posuw_fn_max.strip() else None
		)
		if posuw_fn_max_val is not None and posuw_fn_max_val < 0:
			errors.append("Posuw fn (max) nie może być ujemny")
	except ValueError:
		errors.append("Posuw fn (max) musi być liczbą")

	try:
		prędkość_skrawania_min_val = (
			float(prędkość_skrawania_min) if prędkość_skrawania_min.strip() else None
		)
		if prędkość_skrawania_min_val is not None and prędkość_skrawania_min_val < 0:
			errors.append("Prędkość skrawania (min) nie może być ujemna")
	except ValueError:
		errors.append("Prędkość skrawania (min) musi być liczbą")

	try:
		prędkość_skrawania_max_val = (
			float(prędkość_skrawania_max) if prędkość_skrawania_max.strip() else None
		)
		if prędkość_skrawania_max_val is not None and prędkość_skrawania_max_val < 0:
			errors.append("Prędkość skrawania (max) nie może być ujemna")
	except ValueError:
		errors.append("Prędkość skrawania (max) musi być liczbą")

	try:
		obroty_val = float(obroty) if obroty.strip() else None
		if obroty_val is not None and obroty_val < 0:
			errors.append("Obroty nie mogą być ujemne")
	except ValueError:
		errors.append("Obroty muszą być liczbą")

	try:
		posuw_val = float(posuw) if posuw.strip() else None
		if posuw_val is not None and posuw_val < 0:
			errors.append("Posuw nie może być ujemny")
	except ValueError:
		errors.append("Posuw musi być liczbą")

	if errors:
		return templates.TemplateResponse(
			request,
			"tools/drills_form.html",
			{
				"is_edit": True,
				"drill": drill,
				"errors": errors,
				"form_data": {
					"średnica_D_mm": średnica_D_mm,
					"symbol_narzędzia": symbol_narzędzia,
					"rodzaj_wiertła": rodzaj_wiertła,
					"producent": producent,
					"symbol_płytki": symbol_płytki,
					"długość_robocza_mm": długość_robocza_mm,
					"liczba_ostrzy": liczba_ostrzy,
					"posuw_fn_min": posuw_fn_min,
					"posuw_fn_max": posuw_fn_max,
					"prędkość_skrawania_min": prędkość_skrawania_min,
					"prędkość_skrawania_max": prędkość_skrawania_max,
					"obroty": obroty,
					"posuw": posuw,
					"uwagi": uwagi,
				},
			},
			status_code=status.HTTP_400_BAD_REQUEST,
		)

	# Update record
	drill.średnica_D_mm = średnica_D_mm
	drill.symbol_narzędzia = symbol_narzędzia
	drill.rodzaj_wiertła = rodzaj_wiertła
	drill.producent = producent if producent.strip() else None
	drill.symbol_płytki = symbol_płytki if symbol_płytki.strip() else None
	drill.długość_robocza_mm = długość_robocza_mm_val
	drill.liczba_ostrzy = liczba_ostrzy_val
	drill.posuw_fn_min = posuw_fn_min_val
	drill.posuw_fn_max = posuw_fn_max_val
	drill.prędkość_skrawania_min = prędkość_skrawania_min_val
	drill.prędkość_skrawania_max = prędkość_skrawania_max_val
	drill.obroty = obroty_val
	drill.posuw = posuw_val
	drill.uwagi = uwagi if uwagi.strip() else None

	session.add(drill)
	session.commit()

	return RedirectResponse(url="/tools/drills", status_code=status.HTTP_303_SEE_OTHER)


@router.delete("/drills/{drill_id}", response_class=HTMLResponse, name="drills_delete")
async def drills_delete(
	drill_id: int,
	session: Session = Depends(get_session),
) -> RedirectResponse:
	"""Delete a drill."""
	drill = session.get(Drills, drill_id)
	if drill:
		session.delete(drill)
		session.commit()

	return RedirectResponse(url="/tools/drills", status_code=status.HTTP_303_SEE_OTHER)
