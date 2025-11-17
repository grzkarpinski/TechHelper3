"""Router definitions for calculator endpoints."""

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..calculations.cost import (
	MAX_OPERATIONS,
	MACHINE_RATES,
	MachiningCostCalculationError,
	OperationInput,
	calculate_cost_summary,
)
from ..calculations.feed_speed import (
	SpeedFeedCalculationError,
	calculate_speed_feed,
)
from ..calculations.drilling_feed_speed import (
	DrillingSpeedFeedCalculationError,
	calculate_drilling_speed_feed,
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


def _render_drilling_speed_feed_partial(
	request: Request,
	*,
	result: dict[str, Any] | None = None,
	errors: list[str] | None = None,
	status_code: int = status.HTTP_200_OK,
) -> HTMLResponse:
	return templates.TemplateResponse(
		request,
		"calculators/partials/drilling_speed_feed_result.html",
		{
			"result": result,
			"errors": errors,
		},
		status_code=status_code,
	)


def _render_cost_partial(
	request: Request,
	*,
	result: Any | None = None,
	errors: list[str] | None = None,
	status_code: int = status.HTTP_200_OK,
) -> HTMLResponse:
	return templates.TemplateResponse(
		request,
		"calculators/partials/cost_result.html",
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


@router.get(
	"/drilling-speed-feed",
	response_class=HTMLResponse,
	name="calculators_drilling_speed_feed_form",
)
async def calculators_drilling_speed_feed_form(request: Request) -> HTMLResponse:
	"""Render the drilling speed and feed calculator page."""
	return templates.TemplateResponse(
		request,
		"calculators/drilling_speed_feed.html",
	)


@router.get(
	"/drilling-speed-feed/result",
	response_class=HTMLResponse,
	name="calculators_drilling_speed_feed_result_empty",
)
async def calculators_drilling_speed_feed_result_empty(
	request: Request,
) -> HTMLResponse:
	"""Return an empty result fragment for the drilling calculator."""
	return _render_drilling_speed_feed_partial(request)


@router.get(
	"/cost",
	response_class=HTMLResponse,
	name="calculators_cost_form",
)
async def calculators_cost_form(request: Request) -> HTMLResponse:
	"""Render the machining cost calculator page."""
	machine_rates = [
		{"group": group, "name": data["name"], "rate": data["rate"]}
		for group, data in MACHINE_RATES.items()
	]
	return templates.TemplateResponse(
		request,
		"calculators/cost.html",
		{
			"machine_rates": machine_rates,
			"max_operations": MAX_OPERATIONS,
		},
	)


@router.get(
	"/cost/result",
	response_class=HTMLResponse,
	name="calculators_cost_result_empty",
)
async def calculators_cost_result_empty(request: Request) -> HTMLResponse:
	"""Return an empty result fragment for the cost calculator."""
	return _render_cost_partial(request)


@router.post(
	"/drilling-speed-feed",
	response_class=HTMLResponse,
	name="calculators_drilling_speed_feed_calculate",
)
async def calculators_drilling_speed_feed_calculate(
	request: Request,
	cutting_speed: str = Form(""),
	spindle_speed: str = Form(""),
	feed_per_rev: str = Form(""),
	feed_rate: str = Form(""),
	diameter: str = Form(""),
) -> HTMLResponse:
	"""Process drilling form submission and return the result fragment."""

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

	diameter_value = _to_float(diameter, "Średnica D", required=True)
	cutting_speed_value = _to_float(
		cutting_speed,
		"Prędkość skrawania Vc",
		required=False,
	)
	spindle_speed_value = _to_float(
		spindle_speed,
		"Obroty wrzeciona n",
		required=False,
	)
	feed_per_rev_value = _to_float(
		feed_per_rev,
		"Posuw na obrót fn",
		required=False,
	)
	feed_rate_value = _to_float(
		feed_rate,
		"Posuw F",
		required=False,
	)

	if errors:
		return _render_drilling_speed_feed_partial(
			request,
			errors=errors,
			status_code=status.HTTP_400_BAD_REQUEST,
		)

	try:
		calculation = calculate_drilling_speed_feed(
			diameter=diameter_value or 0.0,
			cutting_speed=cutting_speed_value,
			spindle_speed=spindle_speed_value,
			feed_per_rev=feed_per_rev_value,
			feed_rate=feed_rate_value,
		)
	except DrillingSpeedFeedCalculationError as exc:
		return _render_drilling_speed_feed_partial(
			request,
			errors=[str(exc)],
			status_code=status.HTTP_400_BAD_REQUEST,
		)

	result_payload = {
		"cutting_speed": calculation.cutting_speed,
		"spindle_speed": calculation.spindle_speed,
		"feed_rate": calculation.feed_rate,
		"feed_per_rev": calculation.feed_per_rev,
	}

	return _render_drilling_speed_feed_partial(
		request,
		result=result_payload,
	)


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


@router.post(
	"/cost",
	response_class=HTMLResponse,
	name="calculators_cost_calculate",
)
async def calculators_cost_calculate(request: Request) -> HTMLResponse:
	"""Process machining cost form submission and return the result fragment."""

	form_data = await request.form()
	machine_groups = form_data.getlist("machine_group")
	tpz_values = form_data.getlist("tpz")
	tj_values = form_data.getlist("tj")

	errors: list[str] = []
	operations: list[OperationInput] = []
	row_count = max(len(machine_groups), len(tpz_values), len(tj_values))

	def _parse_machine_group(value: str, row_number: int) -> int | None:
		cleaned = value.strip()
		if not cleaned:
			errors.append(f"Wybierz grupę maszyny dla operacji {row_number}.")
			return None
		try:
			number = int(cleaned)
		except ValueError:
			errors.append(
				f"Pole grupa maszyny w operacji {row_number} musi być liczbą całkowitą."
			)
			return None
		return number

	def _parse_minutes(value: str, field_label: str, row_number: int) -> float | None:
		cleaned = value.strip()
		if not cleaned:
			return 0.0
		normalized = cleaned.replace(",", ".")
		try:
			numeric = float(normalized)
		except ValueError:
			errors.append(
				f"Pole {field_label} w operacji {row_number} musi być liczbą."
			)
			return None
		if numeric < 0:
			errors.append(
				f"Pole {field_label} w operacji {row_number} nie może być ujemne."
			)
			return None
		return numeric

	for index in range(row_count):
		group_raw = machine_groups[index] if index < len(machine_groups) else ""
		tpz_raw = tpz_values[index] if index < len(tpz_values) else ""
		tj_raw = tj_values[index] if index < len(tj_values) else ""

		if not group_raw and not tpz_raw and not tj_raw:
			continue

		row_number = index + 1
		machine_group = _parse_machine_group(group_raw, row_number)
		tpz_minutes = _parse_minutes(tpz_raw, "Tpz", row_number)
		tj_minutes = _parse_minutes(tj_raw, "Tj", row_number)

		if machine_group is None or tpz_minutes is None or tj_minutes is None:
			continue

		operations.append(
			OperationInput(
				machine_group=machine_group,
				tpz_minutes=tpz_minutes,
				tj_minutes=tj_minutes,
			)
		)

	if len(operations) > MAX_OPERATIONS:
		errors.append(
			f"Można obliczyć maksymalnie {MAX_OPERATIONS} operacji jednocześnie."
		)

	if not operations and not errors:
		errors.append("Dodaj przynajmniej jedną operację.")

	if errors:
		return _render_cost_partial(
			request,
			errors=errors,
			status_code=status.HTTP_400_BAD_REQUEST,
		)

	try:
		summary = calculate_cost_summary(operations=operations)
	except MachiningCostCalculationError as exc:
		return _render_cost_partial(
			request,
			errors=[str(exc)],
			status_code=status.HTTP_400_BAD_REQUEST,
		)

	return _render_cost_partial(
		request,
		result=summary,
	)
