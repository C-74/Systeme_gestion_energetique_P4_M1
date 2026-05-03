from __future__ import annotations

from .models import BatteryConfig, EnergyFlow, EnergyKPIs

# Paramètres tarifaires / d'émissions
IMPORT_PRICE_EUR_KWH = 0.20   # prix d'achat réseau
EXPORT_PRICE_EUR_KWH = 0.06   # prix de revente
CO2_GRID_KG_KWH = 0.05        # intensité carbone du réseau


def compute_kpis(
    flows: list[EnergyFlow],
    battery: BatteryConfig | None = None,
) -> EnergyKPIs:
    """Calcule les indicateurs de performance énergétique."""
    bat = battery or BatteryConfig()

    total_load = sum(f.total_load_kwh for f in flows)
    total_solar = sum(f.solar_kwh for f in flows)
    grid_import = sum(f.grid_import_kwh for f in flows)
    grid_export = sum(f.grid_export_kwh for f in flows)

    # Autoconsommation solaire : part du solaire réellement utilisée localement
    solar_exported = grid_export
    solar_consumed_locally = max(0.0, total_solar - solar_exported)
    self_consumption_rate = solar_consumed_locally / total_solar if total_solar > 0 else 0.0

    # Autonomie : part de la conso couverte sans le réseau
    autonomy_rate = max(0.0, 1.0 - grid_import / total_load) if total_load > 0 else 1.0

    # Pic d'import réseau
    peak_import = max((f.grid_import_kwh for f in flows), default=0.0)

    # Facteur de charge
    loads = [f.total_load_kwh for f in flows]
    avg_load = total_load / len(flows) if flows else 0.0
    peak_load = max(loads, default=1.0)
    load_factor = avg_load / peak_load if peak_load > 0 else 0.0

    # Cycles batterie équivalents
    total_charged = sum(f.battery_charge_kwh for f in flows if f.battery_charge_kwh > 0)
    battery_cycles = total_charged / bat.capacity_kwh if bat.capacity_kwh > 0 else 0.0

    # Coût net
    net_cost = grid_import * IMPORT_PRICE_EUR_KWH - grid_export * EXPORT_PRICE_EUR_KWH

    # Émissions CO2
    co2_kg = grid_import * CO2_GRID_KG_KWH

    return EnergyKPIs(
        total_consumption_kwh=round(total_load, 4),
        total_solar_kwh=round(total_solar, 4),
        grid_import_kwh=round(grid_import, 4),
        grid_export_kwh=round(grid_export, 4),
        self_consumption_rate=round(self_consumption_rate, 6),
        autonomy_rate=round(autonomy_rate, 6),
        peak_grid_import_kwh=round(peak_import, 4),
        load_factor=round(load_factor, 6),
        battery_cycles=round(battery_cycles, 4),
        net_energy_cost_eur=round(net_cost, 4),
        grid_co2_kg=round(co2_kg, 4),
    )
