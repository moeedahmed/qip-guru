"""Run-chart analysis helpers for synthetic or de-identified QIP measures."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import math
from pathlib import Path
from statistics import median


_OUTPUT_FIELDS = (
    "qip_index",
    "qip_value",
    "qip_baseline_median",
    "qip_side",
    "qip_run_length",
    "qip_shift_signal",
    "qip_trend_direction",
    "qip_trend_length",
    "qip_trend_signal",
)


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
        reader = csv.reader(handle, strict=True)
        try:
            fieldnames = next(reader)
        except StopIteration as exc:
            raise ValueError("input CSV is missing a header row") from exc
        except csv.Error as exc:
            raise ValueError(f"malformed CSV header row: {exc}") from exc

        _validate_headers(fieldnames)
        rows: list[dict[str, str]] = []
        row_number = 2
        while True:
            try:
                values_in_row = next(reader)
            except StopIteration:
                break
            except csv.Error as exc:
                raise ValueError(f"malformed CSV row {row_number}: {exc}") from exc
            if len(values_in_row) != len(fieldnames):
                raise ValueError(
                    f"malformed CSV row {row_number}: expected {len(fieldnames)} fields, "
                    f"found {len(values_in_row)}"
                )
            rows.append(dict(zip(fieldnames, values_in_row, strict=True)))
            row_number += 1
    if not rows:
        raise ValueError("input CSV has no data rows")
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
    output_fields = fieldnames + list(_OUTPUT_FIELDS)
    with destination.open("x", newline="", encoding="utf-8") as handle:
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


def _validate_headers(fieldnames: list[str]) -> None:
    if not fieldnames:
        raise ValueError("input CSV header row is blank")
    for column_number, fieldname in enumerate(fieldnames, start=1):
        if not fieldname.strip():
            raise ValueError(f"input CSV has a blank header at column {column_number}")

    duplicate_headers = sorted({name for name in fieldnames if fieldnames.count(name) > 1})
    if duplicate_headers:
        raise ValueError(f"input CSV has duplicate header: {duplicate_headers[0]}")

    conflicting_headers = sorted(set(fieldnames).intersection(_OUTPUT_FIELDS))
    if conflicting_headers:
        raise ValueError(f"input CSV header conflicts with generated output column: {conflicting_headers[0]}")


def _parse_value(raw_value: str, row_number: int) -> float:
    if not raw_value.strip():
        raise ValueError(f"value column is blank at CSV row {row_number}")
    try:
        value = float(raw_value)
    except ValueError as exc:
        raise ValueError(f"value column contains non-numeric data at CSV row {row_number}") from exc
    if not math.isfinite(value):
        raise ValueError(f"value column contains a non-finite number at CSV row {row_number}")
    return value


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
