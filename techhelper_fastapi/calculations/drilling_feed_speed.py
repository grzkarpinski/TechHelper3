"""Computation helpers for the drilling speed and feed calculator."""

from __future__ import annotations

from dataclasses import dataclass
import math


class DrillingSpeedFeedCalculationError(ValueError):
	"""Raised when drilling calculator inputs are insufficient or invalid."""


@dataclass
class DrillingSpeedFeedResult:
	cutting_speed: float  # Vc in m/min
	spindle_speed: float  # n in rev/min
	feed_rate: float  # F in mm/min
	feed_per_rev: float  # fn in mm/rev


def calculate_drilling_speed_feed(
	*,
	diameter: float,
	cutting_speed: float | None = None,
	spindle_speed: float | None = None,
	feed_per_rev: float | None = None,
	feed_rate: float | None = None,
) -> DrillingSpeedFeedResult:
	"""Calculate missing drilling machining parameters."""

	if diameter <= 0:
		raise DrillingSpeedFeedCalculationError(
			"Średnica D musi być większa od zera."
		)

	# Determine spindle speed and cutting speed.
	n: float
	vc: float

	if spindle_speed is not None and spindle_speed > 0:
		n = spindle_speed
		vc = (
			cutting_speed
			if cutting_speed is not None and cutting_speed > 0
			else math.pi * diameter * n / 1000
		)
	elif cutting_speed is not None and cutting_speed > 0:
		vc = cutting_speed
		n = (1000 * vc) / (math.pi * diameter)
	else:
		raise DrillingSpeedFeedCalculationError(
			"Podaj prędkość skrawania Vc lub obroty wrzeciona n."
		)

	# Determine feed rate and feed per revolution.
	feed: float
	fn: float

	if feed_rate is not None and feed_rate > 0:
		feed = feed_rate
		if feed_per_rev is not None and feed_per_rev > 0:
			fn = feed_per_rev
		else:
			if n <= 0:
				raise DrillingSpeedFeedCalculationError(
					"Nie można obliczyć posuwu na obrót dla podanych danych."
				)
			fn = feed / n
	elif feed_per_rev is not None and feed_per_rev > 0:
		fn = feed_per_rev
		feed = fn * n
	else:
		raise DrillingSpeedFeedCalculationError(
			"Podaj posuw na obrót fn lub posuw F."
		)

	return DrillingSpeedFeedResult(
		cutting_speed=vc,
		spindle_speed=n,
		feed_rate=feed,
		feed_per_rev=fn,
	)
