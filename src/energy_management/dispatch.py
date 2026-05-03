from __future__ import annotations

from .models import BatteryConfig, EnergyFlow, EnergyInput


def run_dispatch(
    inputs: list[EnergyInput],
    battery: BatteryConfig | None = None,
) -> list[EnergyFlow]:
    """Calcule les flux énergétiques pour chaque pas horaire.

    Stratégie :
    1. Le solaire couvre d'abord la charge totale.
    2. L'excédent solaire charge la batterie (si place disponible).
    3. Si la charge n'est pas couverte, on décharge la batterie.
    4. Le réseau compense le déficit restant (import).
    5. Si la batterie est pleine et qu'il reste du solaire, on exporte.
    """
    bat = battery or BatteryConfig()
    soc = bat.initial_soc  # state of charge courant (fraction 0-1)
    flows: list[EnergyFlow] = []

    for inp in inputs:
        total_load = inp.base_load_kwh + inp.flexible_load_kwh
        net = inp.solar_kwh - total_load  # positif = excédent solaire

        battery_delta = 0.0  # kWh échangés avec la batterie
        grid_import = 0.0
        grid_export = 0.0

        if net >= 0:
            # Excédent solaire → charger la batterie
            available_capacity = (1.0 - soc) * bat.capacity_kwh
            charge = min(net, bat.max_charge_rate_kw, available_capacity)
            charge_stored = charge * bat.charge_efficiency
            soc = min(1.0, soc + charge_stored / bat.capacity_kwh)
            battery_delta = charge

            # Surplus inutilisé → export réseau
            leftover = net - charge
            grid_export = max(0.0, leftover)
        else:
            # Déficit → décharger la batterie
            deficit = -net
            available_energy = soc * bat.capacity_kwh
            discharge = min(deficit, bat.max_discharge_rate_kw, available_energy)
            discharge_delivered = discharge * bat.discharge_efficiency
            soc = max(0.0, soc - discharge / bat.capacity_kwh)
            battery_delta = -discharge

            # Déficit résiduel → import réseau
            remaining_deficit = deficit - discharge_delivered
            grid_import = max(0.0, remaining_deficit)

        flows.append(
            EnergyFlow(
                timestamp=inp.timestamp,
                total_load_kwh=round(total_load, 6),
                solar_kwh=round(inp.solar_kwh, 6),
                battery_charge_kwh=round(battery_delta, 6),
                grid_import_kwh=round(grid_import, 6),
                grid_export_kwh=round(grid_export, 6),
                soc=round(soc, 6),
            )
        )

    return flows
