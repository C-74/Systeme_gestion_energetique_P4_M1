from __future__ import annotations

from .models import BatteryConfig, EnergyFlow, EnergyInput


def run_dispatch(inputs: list[EnergyInput], battery: BatteryConfig | None = None) -> list[EnergyFlow]:
    battery = battery or BatteryConfig()
    soc = min(max(0.0, battery.initial_soc_kwh), battery.capacity_kwh)
    charge_efficiency = battery.round_trip_efficiency**0.5
    discharge_efficiency = battery.round_trip_efficiency**0.5

    flows: list[EnergyFlow] = []

    for point in inputs:
        load = point.total_load_kwh
        solar = point.solar_kwh
        solar_to_load = min(load, solar)
        residual_load = load - solar_to_load
        solar_surplus = solar - solar_to_load

        max_discharge_by_power = battery.max_discharge_kw
        max_discharge_by_soc = soc * discharge_efficiency
        battery_discharge = min(residual_load, max_discharge_by_power, max_discharge_by_soc)
        if battery_discharge > 0:
            soc -= battery_discharge / discharge_efficiency

        residual_load -= battery_discharge
        grid_import = max(0.0, residual_load)

        max_charge_by_power = battery.max_charge_kw
        max_charge_by_capacity = (battery.capacity_kwh - soc) / charge_efficiency
        battery_charge = min(solar_surplus, max_charge_by_power, max_charge_by_capacity)
        if battery_charge > 0:
            soc += battery_charge * charge_efficiency

        solar_surplus -= battery_charge
        grid_export = max(0.0, solar_surplus)

        flows.append(
            EnergyFlow(
                timestamp=point.timestamp,
                load_kwh=load,
                solar_kwh=solar,
                solar_used_for_load_kwh=solar_to_load,
                battery_charge_kwh=battery_charge,
                battery_discharge_kwh=battery_discharge,
                battery_soc_kwh=min(max(0.0, soc), battery.capacity_kwh),
                grid_import_kwh=grid_import,
                grid_export_kwh=grid_export,
            )
        )

    return flows
