from __future__ import annotations

import math
import random
from datetime import date, datetime, timedelta

from .models import EnergyInput


def generate_synthetic_day(
    simulation_date: date,
    seed: int = 42,
) -> list[EnergyInput]:
    """Génère 24 points horaires de données énergétiques synthétiques.

    La charge de base suit un profil résidentiel typique avec des pics
    le matin (7h-9h) et le soir (18h-22h). La production solaire suit
    une courbe en cloche centrée sur midi. La charge flexible représente
    ~20-35 % de la charge totale.
    """
    rng = random.Random(seed)
    start = datetime(simulation_date.year, simulation_date.month, simulation_date.day)
    points: list[EnergyInput] = []

    for h in range(24):
        ts = start + timedelta(hours=h)

        # Profil de charge de base : creux la nuit, pics matin/soir
        morning_peak = math.exp(-0.5 * ((h - 8) / 1.5) ** 2)
        evening_peak = math.exp(-0.5 * ((h - 20) / 2.0) ** 2)
        night_base = 0.3
        base = night_base + 1.2 * morning_peak + 1.8 * evening_peak
        base *= 1.0 + rng.uniform(-0.05, 0.05)  # bruit ±5 %

        # Charge flexible : actif principalement en journée
        daytime = math.exp(-0.5 * ((h - 14) / 4.0) ** 2)
        flex = 0.4 * daytime * (1.0 + rng.uniform(-0.1, 0.1))

        # Production solaire : cloche centrée sur 13h
        if 6 <= h <= 20:
            solar_raw = math.exp(-0.5 * ((h - 13) / 3.5) ** 2)
            solar = 3.5 * solar_raw * (1.0 + rng.uniform(-0.08, 0.08))
        else:
            solar = 0.0

        points.append(
            EnergyInput(
                timestamp=ts,
                base_load_kwh=round(max(base, 0.05), 4),
                flexible_load_kwh=round(max(flex, 0.0), 4),
                solar_kwh=round(max(solar, 0.0), 4),
            )
        )

    return points
