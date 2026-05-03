from __future__ import annotations

import argparse
import csv
import json
from datetime import date, timedelta
from pathlib import Path

from energy_management.cli import run_scenarios


def _parse_date(value: str) -> date:
    year, month, day = map(int, value.split("-"))
    return date(year, month, day)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic days and KPIs")
    parser.add_argument("--start-date", type=_parse_date, required=True, help="Date AAAA-MM-JJ du premier jour")
    parser.add_argument("--days", type=int, default=7, help="Nombre de jours à générer")
    parser.add_argument("--seed", type=int, default=42, help="Graine aléatoire de base")
    parser.add_argument("--output", type=Path, default=Path("outputs"), help="Dossier de sortie")
    parser.add_argument("--max-relative-shift", type=float, default=0.45, help="Amplitude de déplacement flexible")
    parser.add_argument("--json", action="store_true", help="Sauvegarder aussi les KPI en JSON")
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)

    all_rows: list[list] = []
    kpi_results: dict[str, dict] = {}

    for offset in range(args.days):
        current_date = args.start_date + timedelta(days=offset)
        day_seed = args.seed + offset
        result = run_scenarios(current_date, day_seed, args.max_relative_shift, include_inputs=True)

        # flatten hourly inputs (baseline) as table rows
        for point in result["baseline_inputs"]:
            all_rows.append(
                [
                    point.timestamp.isoformat(),
                    point.base_load_kwh,
                    point.flexible_load_kwh,
                    point.solar_kwh,
                    "baseline",
                ]
            )
        for point in result["optimized_inputs"]:
            all_rows.append(
                [
                    point.timestamp.isoformat(),
                    point.base_load_kwh,
                    point.flexible_load_kwh,
                    point.solar_kwh,
                    "optimized",
                ]
            )

        kpi_results[current_date.isoformat()] = result["kpis"]

    # write inputs
    inputs_csv = args.output / "synthetic_inputs.csv"
    with inputs_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["timestamp", "base_load_kwh", "flexible_load_kwh", "solar_kwh", "scenario"])
        writer.writerows(all_rows)

    if args.json:
        kpi_json = args.output / "kpis.json"
        with kpi_json.open("w", encoding="utf-8") as handle:
            json.dump(kpi_results, handle, indent=2, ensure_ascii=False)

    print(f"✅ Généré: {inputs_csv}")
    if args.json:
        print(f"✅ KPI: {kpi_json}")


if __name__ == "__main__":
    main()
