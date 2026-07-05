"""Run-chart analysis helpers for synthetic or de-identified QIP measures."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from statistics import median


@dataclass(frozen=True)
class RunChartResult:
    """Summary of a run-chart analysis."""

    output_path: Path
    row_count: int
    baseline_median: float
    shift_signals: int
    trend_signals: int


def analyse_run_chart_csv(
    input_path: str | Path,
    output_path: str | Path,
    *,
    value_column: str,
    date_column: str | None = None,
    baseline_points: int | None = None,
    run_length: int = 6,
    trend_length: int = 5,
) -> RunChartResult:
    """Analyse a CSV run chart and write annotated rows to a new CSV file."""

    source = Path(input_path)
    destination = Path(output_path)
    if destination.exists():
        raise FileExistsError(f"output file already exists: {destination}")
    if source.resolve() == destination.resolve():
        raise ValueError("output path must be different from input path")
    if baseline_points is not None and baseline_points < 2:
        raise ValueError("baseline-points must be at least 2 when provided")
    if run_length < 2:
        raise ValueError("run-length must be at least 2")
    if trend_length < 2:
        raise ValueError("trend-length must be at least 2")

    with source.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("input CSV has no data rows")
    fieldnames = list(rows[0].keys())
    if value_column not in fieldnames:
        raise ValueError(f"value column not found: {value_column}")
    if date_column and date_column not in fieldnames:
        raise ValueError(f"date column not found: {date_column}")

    values = [_parse_value(row[value_column], index + 2) for index, row in enumerate(rows)]
    baseline_values = values[:baseline_points] if baseline_points else values
    if baseline_points and len(baseline_values) < baseline_points:
        raise ValueError("input CSV has fewer rows than baseline-points")
    baseline_median = float(median(baseline_values))

    annotated = _annotate_rows(rows, values, baseline_median, run_length, trend_length)
    output_fields = fieldnames + [
        "qip_index",
        "qip_value",
        "qip_baseline_median",
        "qip_side",
        "qip_run_length",
        "qip_shift_signal",
        "qip_trend_direction",
        "qip_trend_length",
        "qip_trend_signal",
    ]
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(annotated)

    return RunChartResult(
        output_path=destination,
        row_count=len(rows),
        baseline_median=baseline_median,
        shift_signals=sum(row["qip_shift_signal"] == "yes" for row in annotated),
        trend_signals=sum(row["qip_trend_signal"] == "yes" for row in annotated),
    )


def _parse_value(raw_value: str, row_number: int) -> float:
    try:
        return float(raw_value)
    except ValueError as exc:
        raise ValueError(f"value column contains non-numeric data at CSV row {row_number}") from exc


def _annotate_rows(
    rows: list[dict[str, str]],
    values: list[float],
    baseline_median: float,
    run_length: int,
    trend_length: int,
) -> list[dict[str, str]]:
    annotated: list[dict[str, str]] = []
    current_side = ""
    current_side_count = 0
    trend_direction = ""
    trend_count = 1
    previous_value: float | None = None

    for index, (row, value) in enumerate(zip(rows, values, strict=True), start=1):
        side = _side(value, baseline_median)
        if side == "on_median":
            current_side = ""
            current_side_count = 0
        elif side == current_side:
            current_side_count += 1
        else:
            current_side = side
            current_side_count = 1

        if previous_value is None or value == previous_value:
            trend_direction = ""
            trend_count = 1
        else:
            direction = "up" if value > previous_value else "down"
            if direction == trend_direction:
                trend_count += 1
            else:
                trend_direction = direction
                trend_count = 2
        previous_value = value

        annotated_row = dict(row)
        annotated_row.update(
            {
                "qip_index": str(index),
                "qip_value": _format_number(value),
                "qip_baseline_median": _format_number(baseline_median),
                "qip_side": side,
                "qip_run_length": str(current_side_count),
                "qip_shift_signal": "yes" if current_side_count >= run_length else "no",
                "qip_trend_direction": trend_direction,
                "qip_trend_length": str(trend_count),
                "qip_trend_signal": "yes" if trend_count >= trend_length else "no",
            }
        )
        annotated.append(annotated_row)
    return annotated


def _side(value: float, baseline_median: float) -> str:
    if value > baseline_median:
        return "above"
    if value < baseline_median:
        return "below"
    return "on_median"


def _format_number(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return f"{value:.6g}"
