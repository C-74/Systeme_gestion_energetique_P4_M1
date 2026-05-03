from datetime import date

from energy_management.dispatch import run_dispatch
from energy_management.models import BatteryConfig
from energy_management.optimization import optimize_flexible_schedule
from energy_management.simulator import generate_synthetic_day


def test_optimization_preserves_total_flexible_energy() -> None:
    points = generate_synthetic_day(date(2026, 3, 24), seed=12)
    optimized = optimize_flexible_schedule(points, max_relative_shift=0.4)

    total_original = round(sum(point.flexible_load_kwh for point in points), 3)
    total_optimized = round(sum(point.flexible_load_kwh for point in optimized), 3)

    assert total_original == total_optimized


def test_optimization_reduces_grid_import_for_typical_day() -> None:
    battery = BatteryConfig()
    points = generate_synthetic_day(date(2026, 3, 24), seed=21)
    optimized = optimize_flexible_schedule(points, max_relative_shift=0.45)

    baseline_flows = run_dispatch(points, battery=battery)
    optimized_flows = run_dispatch(optimized, battery=battery)

    baseline_import = sum(point.grid_import_kwh for point in baseline_flows)
    optimized_import = sum(point.grid_import_kwh for point in optimized_flows)

    assert optimized_import <= baseline_import
