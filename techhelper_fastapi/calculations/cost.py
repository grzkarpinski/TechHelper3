"""Computation helpers for the machining cost calculator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


class MachiningCostCalculationError(ValueError):
	"""Raised when machining cost data is missing or invalid."""


# Hourly rates expressed in PLN/h for each machine group available in the UI.
MACHINE_RATES: dict[int, dict[str, float | str]] = {
	1: {"name": "Frezarka konwencjonalna do 600 mm", "rate": 110.0},
	2: {"name": "Frezarka konwencjonalna powyżej 600 mm", "rate": 120.0},
	4: {"name": "Tokarka CNC", "rate": 120.0},
	5: {"name": "Frezarka CNC stara", "rate": 120.0},
	6: {"name": "Frezarka CNC nowa", "rate": 140.0},
	7: {"name": "Frezarka CNC z głowicą skrętną", "rate": 180.0},
	9: {"name": "Frezarka CNC nowa pozioma", "rate": 140.0},
	10: {"name": "Wytaczarka CNC ponad 2000 mm", "rate": 220.0},
	16: {"name": "Frezarka bramowa CNC", "rate": 220.0},
	17: {"name": "Obróbka ślusarska", "rate": 90.0},
}

MAX_OPERATIONS = 10


@dataclass
class OperationInput:
	machine_group: int
	tpz_minutes: float
	tj_minutes: float


@dataclass
class OperationCost:
	machine_group: int
	machine_name: str
	rate_pln_per_hour: float
	tpz_minutes: float
	tj_minutes: float
	tpz_cost: float
	tj_cost: float
	total_cost: float


@dataclass
class CostSummary:
	operations: list[OperationCost]
	total_cost: float


def calculate_cost_summary(*, operations: Iterable[OperationInput]) -> CostSummary:
	"""Aggregate machining cost for supplied operations.

	Each operation must reference one of the predefined machine groups and provide
	non-negative durations (in minutes) for the setup phase (Tpz) and the unit
	phase (Tj). Up to ``MAX_OPERATIONS`` operations may be processed at once.
	"""

	items = list(operations)
	if not items:
		raise MachiningCostCalculationError(
			"Dodaj przynajmniej jedną operację do obliczeń."
		)
	if len(items) > MAX_OPERATIONS:
		raise MachiningCostCalculationError(
			f"Można obliczyć maksymalnie {MAX_OPERATIONS} operacji jednocześnie."
		)

	operation_results: list[OperationCost] = []
	grand_total = 0.0

	for index, op in enumerate(items, start=1):
		if op.tpz_minutes < 0:
			raise MachiningCostCalculationError(
				f"Czas Tpz dla operacji {index} nie może być ujemny."
			)
		if op.tj_minutes < 0:
			raise MachiningCostCalculationError(
				f"Czas Tj dla operacji {index} nie może być ujemny."
			)

		rate_info = MACHINE_RATES.get(op.machine_group)
		if rate_info is None:
			raise MachiningCostCalculationError(
				f"Nieznana grupa maszyny dla operacji {index}."
			)

		rate = float(rate_info["rate"])
		machine_name = str(rate_info["name"])
		tpz_cost = (op.tpz_minutes / 60.0) * rate
		tj_cost = (op.tj_minutes / 60.0) * rate
		total_cost = tpz_cost + tj_cost

		operation_results.append(
			OperationCost(
				machine_group=op.machine_group,
				machine_name=machine_name,
				rate_pln_per_hour=rate,
				tpz_minutes=op.tpz_minutes,
				tj_minutes=op.tj_minutes,
				tpz_cost=tpz_cost,
				tj_cost=tj_cost,
				total_cost=total_cost,
			)
		)
		grand_total += total_cost

	return CostSummary(operations=operation_results, total_cost=grand_total)
