from __future__ import annotations

import math
import random
from datetime import date, datetime, time, timedelta

from .models import EnergyInput


def _hourly_solar_profile(hour: int) -> float:
    if hour < 6 or hour > 19:
        return 0.0
    peak = 4.2
    x = (hour - 6) / 13 * math.pi
    return max(0.0, peak * math.sin(x))


def _hourly_base_load_profile(hour: int) -> float:
    night = 0.8
    morning_peak = 1.6 if 7 <= hour <= 9 else 0.0
    evening_peak = 2.1 if 18 <= hour <= 22 else 0.0
    workday = 1.0 if 10 <= hour <= 17 else 0.0
    return night + morning_peak + evening_peak + workday


def _hourly_flexible_load_profile(hour: int) -> float:
    if 6 <= hour <= 8:
        return 0.5
    if 12 <= hour <= 14:
        return 0.6
    if 19 <= hour <= 22:
        return 0.8
    return 0.2


def generate_synthetic_day(simulation_date: date, seed: int = 42) -> list[EnergyInput]:
    rng = random.Random(seed)
    start = datetime.combine(simulation_date, time(0, 0))
    points: list[EnergyInput] = []

    for index in range(24):
        timestamp = start + timedelta(hours=index)
        hour = timestamp.hour

        base = _hourly_base_load_profile(hour) * rng.uniform(0.9, 1.1)
        flexible = _hourly_flexible_load_profile(hour) * rng.uniform(0.8, 1.2)
        solar = _hourly_solar_profile(hour) * rng.uniform(0.82, 1.18)

        points.append(
            EnergyInput(
                timestamp=timestamp,
                base_load_kwh=round(base, 3),
                flexible_load_kwh=round(flexible, 3),
                solar_kwh=round(max(0.0, solar), 3),
            )
        )

    return points
