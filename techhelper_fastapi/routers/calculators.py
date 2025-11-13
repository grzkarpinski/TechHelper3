"""Router definitions for calculator endpoints."""

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..calculations.feed_speed import (
	SpeedFeedCalculationError,
	calculate_speed_feed,
)

templates = Jinja2Templates(
	directory=str(Path(__file__).resolve().parent.parent / "templates")
)

router = APIRouter(prefix="/calculators", tags=["calculators"])


@router.get("/", response_class=HTMLResponse, name="calculators_home")
async def calculators_home(request: Request) -> HTMLResponse:
	"""Render calculators overview page."""
	return templates.TemplateResponse(request, "calculators/index.html")


@router.get(
	"/speed-feed",
	response_class=HTMLResponse,
	name="calculators_speed_feed_form",
)
async def calculators_speed_feed_form(request: Request) -> HTMLResponse:
	"""Render the speed and feed calculator page."""
	return templates.TemplateResponse(
		request,
		"calculators/speed_feed.html",
	)


def _render_speed_feed_partial(
	request: Request,
	*,
	result: dict[str, Any] | None = None,
	errors: list[str] | None = None,
	status_code: int = status.HTTP_200_OK,
) -> HTMLResponse:
	return templates.TemplateResponse(
		request,
		"calculators/partials/speed_feed_result.html",
		{
			"result": result,
			"errors": errors,
		},
		status_code=status_code,
	)


@router.get(
	"/speed-feed/result",
	response_class=HTMLResponse,
	name="calculators_speed_feed_result_empty",
)
async def calculators_speed_feed_result_empty(request: Request) -> HTMLResponse:
	"""Return an empty result fragment (used when clearing the form)."""
	return _render_speed_feed_partial(request)


@router.post(
	"/speed-feed",
	response_class=HTMLResponse,
	name="calculators_speed_feed_calculate",
)
async def calculators_speed_feed_calculate(
	request: Request,
	cutting_speed: str = Form(""),
	spindle_speed: str = Form(""),
	feed_per_tooth: str = Form(""),
	feed_rate: str = Form(""),
	diameter: str = Form(""),
	teeth: str = Form(""),
) -> HTMLResponse:
	"""Process form submission and return the result fragment."""

	errors: list[str] = []

	def _to_float(value: str, field_label: str, *, required: bool) -> float | None:
		cleaned = value.strip()
		if not cleaned:
			if required:
				errors.append(f"Pole {field_label} jest wymagane.")
			return None
		normalized = cleaned.replace(",", ".")
		try:
			numeric = float(normalized)
		except ValueError:
			errors.append(f"Pole {field_label} musi być liczbą.")
			return None
		if numeric <= 0:
			errors.append(f"Pole {field_label} musi być większe od zera.")
			return None
		return numeric

	def _to_int(value: str, field_label: str) -> int | None:
		number = _to_float(value, field_label, required=True)
		if number is None:
			return None
		if not number.is_integer():
			errors.append(f"Pole {field_label} musi być liczbą całkowitą.")
			return None
		return int(number)

	diameter_value = _to_float(diameter, "Średnica D", required=True)
	teeth_value = _to_int(teeth, "Liczba ostrzy z")

	cutting_speed_value = _to_float(cutting_speed, "Prędkość skrawania Vc", required=False)
	spindle_speed_value = _to_float(spindle_speed, "Obroty wrzeciona n", required=False)
	feed_per_tooth_value = _to_float(feed_per_tooth, "Posuw na ząb Fz", required=False)
	feed_rate_value = _to_float(feed_rate, "Posuw F", required=False)

	if errors:
		return _render_speed_feed_partial(
			request,
			errors=errors,
			status_code=status.HTTP_400_BAD_REQUEST,
		)

	try:
		calculation = calculate_speed_feed(
			diameter=diameter_value or 0.0,
			teeth=teeth_value or 0,
			cutting_speed=cutting_speed_value,
			spindle_speed=spindle_speed_value,
			feed_per_tooth=feed_per_tooth_value,
			feed_rate=feed_rate_value,
		)
	except SpeedFeedCalculationError as exc:
		return _render_speed_feed_partial(
			request,
			errors=[str(exc)],
			status_code=status.HTTP_400_BAD_REQUEST,
		)

	result_payload = {
		"cutting_speed": calculation.cutting_speed,
		"spindle_speed": calculation.spindle_speed,
		"feed_rate": calculation.feed_rate,
		"feed_per_tooth": calculation.feed_per_tooth,
	}

	return _render_speed_feed_partial(
		request,
		result=result_payload,
	)
