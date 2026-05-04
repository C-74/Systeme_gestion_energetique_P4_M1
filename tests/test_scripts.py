from __future__ import annotations

import csv
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from energy_management.cli import run_scenarios
from energy_management.data_sources import load_inputs_from_csv


def test_load_inputs_from_csv_parses_rows(tmp_path: Path) -> None:
    csv_path = tmp_path / "inputs.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["timestamp", "base_load_kwh", "flexible_load_kwh", "solar_kwh"])
        writer.writerow(["2026-03-24T00:00:00", "1.0", "0.5", "0.2"])
        writer.writerow(["2026-03-24T01:00:00", "1.2", "0.4", "0.0"])

    points = load_inputs_from_csv(csv_path)

    assert len(points) == 2
    assert points[0].base_load_kwh == 1.0
    assert points[1].solar_kwh == 0.0


def test_load_inputs_from_csv_missing_column_raises(tmp_path: Path) -> None:
    bad_csv = tmp_path / "bad.csv"
    with bad_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["timestamp", "base_load_kwh", "solar_kwh"])  # missing flexible_load_kwh
        writer.writerow(["2026-03-24T00:00:00", "1.0", "0.2"])

    try:
        load_inputs_from_csv(bad_csv)
        raised = False
    except ValueError:
        raised = True

    assert raised, "Expected ValueError for missing columns"


def test_run_scenarios_include_inputs() -> None:
    result = run_scenarios(
        simulation_date=datetime(2026, 3, 24).date(),
        seed=7,
        max_relative_shift=0.45,
        include_inputs=True,
    )

    assert "baseline_inputs" in result and "optimized_inputs" in result
    assert "baseline_flows" in result and "optimized_flows" in result
    assert len(result["baseline_inputs"]) == 24
    assert len(result["optimized_inputs"]) == 24
    assert len(result["baseline_flows"]) == 24
    assert len(result["optimized_flows"]) == 24


def test_simulate_days_script_outputs(tmp_path: Path) -> None:
    script = Path(__file__).resolve().parents[1] / "scripts" / "simulate_days.py"
    output_dir = tmp_path / "out"

    subprocess.run(
        [sys.executable, script, "--start-date", "2026-04-14", "--days", "1", "--json", "--output", str(output_dir)],
        check=True,
    )

    inputs_csv = output_dir / "synthetic_inputs.csv"
    kpis_json = output_dir / "kpis.json"

    assert inputs_csv.exists()
    assert kpis_json.exists()

    with inputs_csv.open() as handle:
        rows = list(csv.reader(handle))
    assert rows[0] == ["timestamp", "base_load_kwh", "flexible_load_kwh", "solar_kwh", "scenario"]
    assert len(rows) == 1 + 48  # 24h baseline + 24h optimized

    with kpis_json.open() as handle:
        data = json.load(handle)
    assert "2026-04-14" in data
    assert "baseline" in data["2026-04-14"]


def test_kpi_from_csv_script_runs(tmp_path: Path) -> None:
    # Build a tiny CSV
    csv_path = tmp_path / "inputs.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["timestamp", "base_load_kwh", "flexible_load_kwh", "solar_kwh"])
        writer.writerow(["2026-03-24T00:00:00", "1.0", "0.3", "0.1"])
        writer.writerow(["2026-03-24T01:00:00", "1.1", "0.2", "0.0"])

    script = Path(__file__).resolve().parents[1] / "scripts" / "kpi_from_csv.py"
    output = subprocess.check_output([sys.executable, script, str(csv_path), "--json"], text=True)

    assert "baseline" in output
    assert "optimized" in output
