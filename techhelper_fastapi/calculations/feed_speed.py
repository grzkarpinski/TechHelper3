"""Computation helpers for the speed and feed calculator."""

from __future__ import annotations

from dataclasses import dataclass
import math


class SpeedFeedCalculationError(ValueError):
	"""Raised when the provided inputs are insufficient or invalid."""


@dataclass
class SpeedFeedResult:
	cutting_speed: float  # Vc in m/min
	spindle_speed: float  # n in rev/min
	feed_rate: float  # F in mm/min
	feed_per_tooth: float  # Fz in mm/tooth


def calculate_speed_feed(
	*,
	diameter: float,
	teeth: int,
	cutting_speed: float | None = None,
	spindle_speed: float | None = None,
	feed_per_tooth: float | None = None,
	feed_rate: float | None = None,
) -> SpeedFeedResult:
	"""Calculate missing machining parameters based on the provided values.

	Exactly one value must be provided from each pair (cutting_speed, spindle_speed)
	and (feed_per_tooth, feed_rate). Diameter and teeth must always be positive.
	"""

	if diameter <= 0:
		raise SpeedFeedCalculationError("Średnica D musi być większa od zera.")
	if teeth <= 0:
		raise SpeedFeedCalculationError("Liczba ostrzy z musi być większa od zera.")

	# Determine spindle speed and cutting speed.
	n: float
	vc: float

	if spindle_speed is not None and spindle_speed > 0:
		n = spindle_speed
		vc = cutting_speed if cutting_speed is not None and cutting_speed > 0 else (
			math.pi * diameter * n / 1000
		)
	elif cutting_speed is not None and cutting_speed > 0:
		vc = cutting_speed
		n = (1000 * vc) / (math.pi * diameter)
	else:
		raise SpeedFeedCalculationError(
			"Podaj prędkość skrawania Vc lub obroty wrzeciona n."
		)

	# Determine feed rate and feed per tooth.
	feed: float
	fz: float

	if feed_rate is not None and feed_rate > 0:
		feed = feed_rate
		if feed_per_tooth is not None and feed_per_tooth > 0:
			fz = feed_per_tooth
		else:
			denominator = teeth * n
			if denominator <= 0:
				raise SpeedFeedCalculationError(
					"Nie można obliczyć posuwu na ząb dla podanych danych."
				)
			fz = feed / denominator
	elif feed_per_tooth is not None and feed_per_tooth > 0:
		fz = feed_per_tooth
		feed = fz * teeth * n
	else:
		raise SpeedFeedCalculationError("Podaj posuw na ząb Fz lub posuw F.")

	return SpeedFeedResult(
		cutting_speed=vc,
		spindle_speed=n,
		feed_rate=feed,
		feed_per_tooth=fz,
	)
