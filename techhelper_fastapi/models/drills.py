"""SQLModel definitions for drills."""

from __future__ import annotations

from typing import Optional

from sqlmodel import Field, SQLModel


class Drills(SQLModel, table=True):
	"""Model for drill tools with specifications."""

	id: Optional[int] = Field(default=None, primary_key=True)
	# Required fields
	średnica_D_mm: float = Field(
		gt=0, description="Średnica wiertła w mm"
	)
	symbol_narzędzia: str = Field(
		min_length=1, description="Symbol katalogowy wiertła"
	)
	rodzaj_wiertła: str = Field(
		min_length=1, description="Rodzaj wiertła (HSS, VHM, na 1 płytkę, na 2 płytki)"
	)
	# Optional fields
	producent: Optional[str] = Field(default=None, description="Producent narzędzia")
	symbol_płytki: Optional[str] = Field(default=None, description="Symbol płytki (jeśli dotyczy)")
	długość_robocza_mm: Optional[float] = Field(default=None, ge=0, description="Długość robocza")
	liczba_ostrzy: Optional[int] = Field(default=None, ge=0, description="Liczba ostrzy")
	posuw_fn_min: Optional[float] = Field(default=None, ge=0, description="Minimalny posuw na obrót")
	posuw_fn_max: Optional[float] = Field(default=None, ge=0, description="Maksymalny posuw na obrót")
	prędkość_skrawania_min: Optional[float] = Field(default=None, ge=0, description="Minimalna prędkość")
	prędkość_skrawania_max: Optional[float] = Field(default=None, ge=0, description="Maksymalna prędkość")
	obroty: Optional[float] = Field(default=None, ge=0, description="Obroty (obr/min)")
	posuw: Optional[float] = Field(default=None, ge=0, description="Posuw (mm/min)")
	uwagi: Optional[str] = Field(default=None, description="Dodatkowe uwagi")
