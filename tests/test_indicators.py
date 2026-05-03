from datetime import datetime, timedelta

from energy_management.indicators import compute_kpis
from energy_management.models import BatteryConfig, EnergyFlow


def test_compute_kpis_with_known_values() -> None:
    start = datetime(2026, 3, 24, 0, 0)
    flows = [
        EnergyFlow(
            timestamp=start,
            load_kwh=10.0,
            solar_kwh=6.0,
            solar_used_for_load_kwh=6.0,
            battery_charge_kwh=1.0,
            battery_discharge_kwh=0.0,
            battery_soc_kwh=9.0,
            grid_import_kwh=4.0,
            grid_export_kwh=0.0,
        ),
        EnergyFlow(
            timestamp=start + timedelta(hours=1),
            load_kwh=8.0,
            solar_kwh=2.0,
            solar_used_for_load_kwh=2.0,
            battery_charge_kwh=0.0,
            battery_discharge_kwh=2.0,
            battery_soc_kwh=7.0,
            grid_import_kwh=4.0,
            grid_export_kwh=0.0,
        ),
    ]

    battery = BatteryConfig(capacity_kwh=20.0)
    kpis = compute_kpis(flows, battery=battery, import_tariff_eur_per_kwh=0.2, export_tariff_eur_per_kwh=0.1)

    assert kpis.total_consumption_kwh == 18.0
    assert kpis.total_solar_kwh == 8.0
    assert kpis.grid_import_kwh == 8.0
    assert kpis.grid_export_kwh == 0.0
    assert kpis.self_consumption_rate == 1.0
    assert round(kpis.autonomy_rate, 4) == round((18 - 8) / 18, 4)
    assert kpis.peak_grid_import_kwh == 4.0
    assert round(kpis.load_factor, 4) == round((9.0 / 10.0), 4)
    assert round(kpis.equivalent_battery_cycles, 4) == round((1 + 2) / (2 * 20), 4)
    assert kpis.net_energy_cost_eur == 1.6
