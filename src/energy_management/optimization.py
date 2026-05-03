from __future__ import annotations

from .models import EnergyInput


def optimize_flexible_schedule(
    inputs: list[EnergyInput],
    max_relative_shift: float = 0.45,
) -> list[EnergyInput]:
    """Optimise la charge flexible pour maximiser l'autoconsommation solaire.

    Stratégie :
    - Pour chaque heure avec excédent solaire, on tire de la charge flexible
      depuis les heures où il n'y a pas de solaire.
    - Le paramètre ``max_relative_shift`` limite la part de charge flexible
      déplaçable (entre 0 et 1).
    """
    if not inputs:
        return []

    # Copie mutable des charges flexibles
    flex = [inp.flexible_load_kwh for inp in inputs]
    solar = [inp.solar_kwh for inp in inputs]
    base = [inp.base_load_kwh for inp in inputs]

    # Calcul des excédents / déficits solaires par rapport à la charge de base
    net_solar = [solar[h] - base[h] - flex[h] for h in range(len(inputs))]

    # Identifier les heures avec excédent solaire (receveurs) et sans (donneurs)
    surplus_hours = [h for h, net in enumerate(net_solar) if net > 0]
    deficit_hours = sorted(
        [h for h, net in enumerate(net_solar) if net <= 0],
        key=lambda h: net_solar[h],  # les plus déficitaires d'abord
    )

    for src in deficit_hours:
        if not surplus_hours:
            break
        max_move = flex[src] * max_relative_shift
        moved = 0.0
        for dst in surplus_hours:
            available = min(max_move - moved, net_solar[dst])
            if available <= 0:
                continue
            transfer = min(available, flex[src] - moved)
            flex[src] -= transfer
            flex[dst] += transfer
            net_solar[dst] -= transfer
            net_solar[src] += transfer
            moved += transfer
            if moved >= max_move:
                break

    return [
        EnergyInput(
            timestamp=inp.timestamp,
            base_load_kwh=inp.base_load_kwh,
            flexible_load_kwh=round(max(flex[h], 0.0), 6),
            solar_kwh=inp.solar_kwh,
        )
        for h, inp in enumerate(inputs)
    ]
