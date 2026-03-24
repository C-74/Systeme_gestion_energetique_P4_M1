from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import date

from .dispatch import run_dispatch
from .indicators import compute_kpis
from .models import BatteryConfig
from .optimization import optimize_flexible_schedule
from .simulator import generate_synthetic_day


def _parse_date(value: str) -> date:
    year, month, day = map(int, value.split("-"))
    return date(year, month, day)


def _format_percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Système de gestion énergétique intelligent")
    parser.add_argument("--seed", type=int, default=42, help="Graine aléatoire")
    parser.add_argument("--date", type=_parse_date, default=date.today(), help="Date AAAA-MM-JJ")
    parser.add_argument("--json", action="store_true", help="Sortie JSON")
    parser.add_argument(
        "--max-relative-shift",
        type=float,
        default=0.45,
        help="Amplitude max de déplacement de charge flexible",
    )
    return parser


def run_scenarios(simulation_date: date, seed: int, max_relative_shift: float) -> dict:
    battery = BatteryConfig()
    baseline_inputs = generate_synthetic_day(simulation_date=simulation_date, seed=seed)
    optimized_inputs = optimize_flexible_schedule(baseline_inputs, max_relative_shift=max_relative_shift)

    baseline_flows = run_dispatch(baseline_inputs, battery=battery)
    optimized_flows = run_dispatch(optimized_inputs, battery=battery)

    baseline_kpis = compute_kpis(baseline_flows, battery=battery)
    optimized_kpis = compute_kpis(optimized_flows, battery=battery)

    return {
        "baseline": asdict(baseline_kpis),
        "optimized": asdict(optimized_kpis),
    }


def print_summary(result: dict) -> None:
    baseline = result["baseline"]
    optimized = result["optimized"]

    print("=== Résultats KPI ===")
    print(f"Import réseau (kWh): {baseline['grid_import_kwh']:.3f} -> {optimized['grid_import_kwh']:.3f}")
    print(f"Export réseau (kWh): {baseline['grid_export_kwh']:.3f} -> {optimized['grid_export_kwh']:.3f}")
    print(
        "Autonomie: "
        f"{_format_percent(baseline['autonomy_rate'])} -> {_format_percent(optimized['autonomy_rate'])}"
    )
    print(
        "Autoconsommation solaire: "
        f"{_format_percent(baseline['self_consumption_rate'])} -> "
        f"{_format_percent(optimized['self_consumption_rate'])}"
    )
    print(f"Pic import (kWh): {baseline['peak_grid_import_kwh']:.3f} -> {optimized['peak_grid_import_kwh']:.3f}")
    print(f"Coût net (€): {baseline['net_energy_cost_eur']:.3f} -> {optimized['net_energy_cost_eur']:.3f}")
    print(f"CO2 réseau (kg): {baseline['grid_co2_kg']:.3f} -> {optimized['grid_co2_kg']:.3f}")


def main() -> None:
    args = build_parser().parse_args()
    result = run_scenarios(args.date, args.seed, args.max_relative_shift)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    print_summary(result)


if __name__ == "__main__":
    main()
