from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class BatteryConfig:
    """Configuration de la batterie de stockage."""
    capacity_kwh: float = 10.0        # Capacité totale
    initial_soc: float = 0.5          # State-of-Charge initial (0-1)
    max_charge_rate_kw: float = 3.0   # Puissance max de charge
    max_discharge_rate_kw: float = 3.0
    charge_efficiency: float = 0.95
    discharge_efficiency: float = 0.95


@dataclass
class EnergyInput:
    """Données d'entrée par pas horaire."""
    timestamp: datetime
    base_load_kwh: float       # Charge de base non déplaçable
    flexible_load_kwh: float   # Charge flexible (décalable)
    solar_kwh: float           # Production solaire


@dataclass
class EnergyFlow:
    """Flux énergétiques calculés pour un pas horaire."""
    timestamp: datetime
    total_load_kwh: float
    solar_kwh: float
    battery_charge_kwh: float    # positif = charge, négatif = décharge
    grid_import_kwh: float       # énergie importée du réseau
    grid_export_kwh: float       # énergie exportée vers le réseau
    soc: float                   # State-of-Charge batterie (0-1)


@dataclass
class EnergyKPIs:
    """Indicateurs de performance énergétique agrégés sur la journée."""
    total_consumption_kwh: float
    total_solar_kwh: float
    grid_import_kwh: float
    grid_export_kwh: float
    self_consumption_rate: float   # part du solaire autoconsommée
    autonomy_rate: float           # part de la conso couverte hors réseau
    peak_grid_import_kwh: float    # pic horaire d'import réseau
    load_factor: float             # facteur de charge (moy / pic)
    battery_cycles: float          # cycles équivalents batterie
    net_energy_cost_eur: float
    grid_co2_kg: float
