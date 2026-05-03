from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from .models import EnergyInput


def load_inputs_from_csv(path: str | Path, tzinfo=None) -> list[EnergyInput]:
    """Load energy inputs from a CSV file.

    Expected columns: timestamp, base_load_kwh, flexible_load_kwh, solar_kwh
    Timestamp must be ISO-8601 (e.g. 2026-03-24T14:00:00). Optionally attach
    a timezone with ``tzinfo``.
    """

    filepath = Path(path)
    rows: list[EnergyInput] = []

    with filepath.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)

        required_cols = {"timestamp", "base_load_kwh", "flexible_load_kwh", "solar_kwh"}
        missing = required_cols - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing columns in {filepath}: {', '.join(sorted(missing))}")

        for line_num, row in enumerate(reader, start=2):  # header is line 1
            try:
                ts = datetime.fromisoformat(row["timestamp"])
                if tzinfo:
                    ts = ts.replace(tzinfo=tzinfo)

                rows.append(
                    EnergyInput(
                        timestamp=ts,
                        base_load_kwh=float(row["base_load_kwh"]),
                        flexible_load_kwh=float(row["flexible_load_kwh"]),
                        solar_kwh=float(row["solar_kwh"]),
                    )
                )
            except Exception as exc:  # pylint: disable=broad-except
                raise ValueError(f"Invalid row {line_num} in {filepath}: {exc}") from exc

    return rows
