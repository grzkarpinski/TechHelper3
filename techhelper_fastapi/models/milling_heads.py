"""SQLModel definitions for milling heads."""

from __future__ import annotations

from typing import Optional

from sqlmodel import Field, SQLModel


class MillingHeads(SQLModel, table=True):
	"""Model for milling head tools (Głowice Frezarskie)."""

	id: Optional[int] = Field(default=None, primary_key=True)

	# Required fields
	średnica_D_mm: float = Field(
		...,
		gt=0,
		description="Tool diameter in mm (must be > 0)",
	)
	symbol_narzędzia: str = Field(
		...,
		min_length=1,
		description="Catalog symbol/number",
	)
	liczba_ostrzy: int = Field(
		...,
		gt=0,
		description="Number of teeth (z) (must be > 0)",
	)

	# Optional fields
	producent: Optional[str] = Field(
		default=None,
		description="Manufacturer name",
	)
	symbol_płytki: Optional[str] = Field(
		default=None,
		description="Insert symbol and grade",
	)
	materiał: Optional[str] = Field(
		default=None,
		description="Work material",
	)
	posuw_na_ząb_min: Optional[float] = Field(
		default=None,
		ge=0,
		description="Minimum feed per tooth (fz) in mm/tooth",
	)
	posuw_na_ząb_max: Optional[float] = Field(
		default=None,
		ge=0,
		description="Maximum feed per tooth (fz) in mm/tooth",
	)
	prędkość_skrawania_min: Optional[float] = Field(
		default=None,
		ge=0,
		description="Minimum cutting speed (Vc) in m/min",
	)
	prędkość_skrawania_max: Optional[float] = Field(
		default=None,
		ge=0,
		description="Maximum cutting speed (Vc) in m/min",
	)
	obroty: Optional[float] = Field(
		default=None,
		ge=0,
		description="Spindle speed (n) in rev/min",
	)
	posuw: Optional[float] = Field(
		default=None,
		ge=0,
		description="Feed rate (F) in mm/min",
	)
	głębokość_skrawania_ap: Optional[float] = Field(
		default=None,
		ge=0,
		description="Cutting depth (ap) in mm",
	)
	uwagi: Optional[str] = Field(
		default=None,
		description="Additional notes",
	)
