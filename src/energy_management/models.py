from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime


@dataclass(slots=True)
class BatteryConfig:
    capacity_kwh: float = 20.0
    max_charge_kw: float = 6.0
    max_discharge_kw: float = 6.0
    initial_soc_kwh: float = 8.0
    round_trip_efficiency: float = 0.92


@dataclass(slots=True)
class EnergyInput:
    timestamp: datetime
    base_load_kwh: float
    flexible_load_kwh: float
    solar_kwh: float

    @property
    def total_load_kwh(self) -> float:
        return self.base_load_kwh + self.flexible_load_kwh


@dataclass(slots=True)
class EnergyFlow:
    timestamp: datetime
    load_kwh: float
    solar_kwh: float
    solar_used_for_load_kwh: float
    battery_charge_kwh: float
    battery_discharge_kwh: float
    battery_soc_kwh: float
    grid_import_kwh: float
    grid_export_kwh: float


@dataclass(slots=True)
class KPIResult:
    total_consumption_kwh: float
    total_solar_kwh: float
    grid_import_kwh: float
    grid_export_kwh: float
    self_consumption_rate: float
    autonomy_rate: float
    peak_grid_import_kwh: float
    load_factor: float
    equivalent_battery_cycles: float
    net_energy_cost_eur: float
    grid_co2_kg: float

    def to_dict(self) -> dict:
        return asdict(self)
