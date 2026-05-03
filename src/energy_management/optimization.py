from __future__ import annotations

from .models import EnergyInput


def optimize_flexible_schedule(
    points: list[EnergyInput],
    max_relative_shift: float = 0.45,
) -> list[EnergyInput]:
    if not points:
        return []

    base_loads = [point.base_load_kwh for point in points]
    flexible_loads = [point.flexible_load_kwh for point in points]
    solar = [point.solar_kwh for point in points]

    lower_bounds = [max(0.0, value * (1 - max_relative_shift)) for value in flexible_loads]
    upper_bounds = [value * (1 + max_relative_shift) for value in flexible_loads]

    total_flexible = sum(flexible_loads)
    optimized = lower_bounds[:]
    remaining = total_flexible - sum(optimized)

    priorities = sorted(
        range(len(points)),
        key=lambda index: (solar[index] - base_loads[index], solar[index]),
        reverse=True,
    )

    for index in priorities:
        if remaining <= 1e-9:
            break
        available = upper_bounds[index] - optimized[index]
        if available <= 0:
            continue
        add_energy = min(available, remaining)
        optimized[index] += add_energy
        remaining -= add_energy

    if remaining > 1e-9:
        for index in range(len(points)):
            if remaining <= 1e-9:
                break
            available = upper_bounds[index] - optimized[index]
            if available <= 0:
                continue
            add_energy = min(available, remaining)
            optimized[index] += add_energy
            remaining -= add_energy

    if remaining > 1e-9:
        total = sum(optimized)
        if total > 0:
            factor = total_flexible / total
            optimized = [value * factor for value in optimized]

    result: list[EnergyInput] = []
    for point, new_flexible in zip(points, optimized):
        result.append(
            EnergyInput(
                timestamp=point.timestamp,
                base_load_kwh=point.base_load_kwh,
                flexible_load_kwh=round(new_flexible, 3),
                solar_kwh=point.solar_kwh,
            )
        )

    return result
