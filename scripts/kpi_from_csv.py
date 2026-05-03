from __future__ import annotations

import argparse
from pathlib import Path

from energy_management.cli import run_scenarios
from energy_management.data_sources import load_inputs_from_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Calcule les KPI à partir d'un CSV")
    parser.add_argument("csv", type=Path, help="Fichier CSV d'entrées")
    parser.add_argument("--max-relative-shift", type=float, default=0.45, help="Amplitude déplacement flexible")
    parser.add_argument("--json", action="store_true", help="Affiche le JSON complet")
    args = parser.parse_args()

    inputs = load_inputs_from_csv(args.csv)
    result = run_scenarios(
        simulation_date=inputs[0].timestamp.date(),
        seed=0,
        max_relative_shift=args.max_relative_shift,
        inputs=inputs,
    )

    if args.json:
        import json

        print(json.dumps({"baseline": result["baseline"], "optimized": result["optimized"]}, indent=2, ensure_ascii=False))
    else:
        baseline = result["baseline"]
        optimized = result["optimized"]
        print("=== KPI ===")
        print(f"Import réseau: {baseline['grid_import_kwh']:.3f} -> {optimized['grid_import_kwh']:.3f}")
        print(f"Autonomie: {baseline['autonomy_rate']:.2%} -> {optimized['autonomy_rate']:.2%}")
        print(f"Autoconsommation: {baseline['self_consumption_rate']:.2%} -> {optimized['self_consumption_rate']:.2%}")
        print(f"Coût net (€): {baseline['net_energy_cost_eur']:.3f} -> {optimized['net_energy_cost_eur']:.3f}")


if __name__ == "__main__":
    main()
