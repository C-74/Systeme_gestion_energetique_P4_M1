from __future__ import annotations

from .models import BatteryConfig, EnergyFlow, KPIResult


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def compute_kpis(
    flows: list[EnergyFlow],
    battery: BatteryConfig | None = None,
    import_tariff_eur_per_kwh: float = 0.22,
    export_tariff_eur_per_kwh: float = 0.10,
    grid_co2_kg_per_kwh: float = 0.055,
) -> KPIResult:
    battery = battery or BatteryConfig()

    total_consumption = sum(sample.load_kwh for sample in flows)
    total_solar = sum(sample.solar_kwh for sample in flows)
    total_grid_import = sum(sample.grid_import_kwh for sample in flows)
    total_grid_export = sum(sample.grid_export_kwh for sample in flows)
    solar_used_for_load = sum(sample.solar_used_for_load_kwh for sample in flows)
    peak_grid_import = max((sample.grid_import_kwh for sample in flows), default=0.0)
    peak_load = max((sample.load_kwh for sample in flows), default=0.0)
    avg_load = _safe_ratio(total_consumption, len(flows))

    total_charge = sum(sample.battery_charge_kwh for sample in flows)
    total_discharge = sum(sample.battery_discharge_kwh for sample in flows)
    battery_cycles = _safe_ratio(total_charge + total_discharge, 2 * battery.capacity_kwh)

    self_consumption_rate = _safe_ratio(solar_used_for_load, total_solar)
    autonomy_rate = _safe_ratio(total_consumption - total_grid_import, total_consumption)
    load_factor = _safe_ratio(avg_load, peak_load)

    net_cost = total_grid_import * import_tariff_eur_per_kwh - total_grid_export * export_tariff_eur_per_kwh
    grid_co2 = total_grid_import * grid_co2_kg_per_kwh

    return KPIResult(
        total_consumption_kwh=round(total_consumption, 3),
        total_solar_kwh=round(total_solar, 3),
        grid_import_kwh=round(total_grid_import, 3),
        grid_export_kwh=round(total_grid_export, 3),
        self_consumption_rate=round(self_consumption_rate, 4),
        autonomy_rate=round(autonomy_rate, 4),
        peak_grid_import_kwh=round(peak_grid_import, 3),
        load_factor=round(load_factor, 4),
        equivalent_battery_cycles=round(battery_cycles, 4),
        net_energy_cost_eur=round(net_cost, 3),
        grid_co2_kg=round(grid_co2, 3),
    )
