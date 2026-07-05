#!/usr/bin/env python3
"""QIP Guru command line interface."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from qip_guru.charts import analyse_run_chart_csv
from qip_guru.deid import redact_file, scan_file
from qip_guru.scaffold import create_project
from qip_guru.sources import format_profile, list_profiles, load_profile


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "new":
        return _run_new(args.project_name, args.profile)
    if args.command == "deid" and args.deid_command == "scan":
        return _run_scan(args.path)
    if args.command == "deid" and args.deid_command == "redact":
        return _run_redact(args.input_path, args.output_path)
    if args.command == "sources" and args.sources_command == "list":
        return _run_sources_list()
    if args.command == "sources" and args.sources_command == "show":
        return _run_sources_show(args.profile)
    if args.command == "charts" and args.charts_command == "run-chart":
        return _run_run_chart(
            args.input_path,
            args.output_path,
            args.value_column,
            args.date_column,
            args.baseline_points,
            args.run_length,
            args.trend_length,
        )

    parser.print_help(sys.stderr)
    return 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="qip",
        description="Public-safe QIP scaffold and deterministic assistive de-id helper.",
    )
    subparsers = parser.add_subparsers(dest="command")

    new_parser = subparsers.add_parser("new", help="create a new QIP project scaffold")
    new_parser.add_argument("project_name", help="folder name for the project scaffold")
    new_parser.add_argument(
        "--profile",
        default="global",
        help="source profile to attach to the scaffold, such as global, uk, us, canada, or australia",
    )

    deid_parser = subparsers.add_parser("deid", help="scan or redact supported identifiers")
    deid_subparsers = deid_parser.add_subparsers(dest="deid_command")

    scan_parser = deid_subparsers.add_parser("scan", help="scan a UTF-8 CSV or text file")
    scan_parser.add_argument("path", help="input .csv or .txt file")

    redact_parser = deid_subparsers.add_parser("redact", help="write a redacted copy of a file")
    redact_parser.add_argument("input_path", help="input .csv or .txt file")
    redact_parser.add_argument("--out", required=True, dest="output_path", help="new output file path")

    sources_parser = subparsers.add_parser("sources", help="list or show source profiles")
    sources_subparsers = sources_parser.add_subparsers(dest="sources_command")

    sources_subparsers.add_parser("list", help="list available source profiles")
    show_parser = sources_subparsers.add_parser("show", help="show one source profile")
    show_parser.add_argument("profile", help="profile id, such as global, uk, us, canada, or australia")

    charts_parser = subparsers.add_parser("charts", help="analyse QIP measurement CSV files")
    charts_subparsers = charts_parser.add_subparsers(dest="charts_command")
    run_chart_parser = charts_subparsers.add_parser("run-chart", help="write annotated run-chart CSV output")
    run_chart_parser.add_argument("input_path", help="input CSV with one measure column")
    run_chart_parser.add_argument("--out", required=True, dest="output_path", help="new annotated output CSV path")
    run_chart_parser.add_argument("--value-column", required=True, help="numeric measure column to analyse")
    run_chart_parser.add_argument("--date-column", help="optional date/week column for readability")
    run_chart_parser.add_argument("--baseline-points", type=int, help="use the first N rows to calculate the median")
    run_chart_parser.add_argument("--run-length", type=int, default=6, help="points on one side of median for shift signal")
    run_chart_parser.add_argument("--trend-length", type=int, default=5, help="consecutive increasing/decreasing points for trend signal")

    return parser


def _run_new(project_name: str, profile: str) -> int:
    try:
        created = create_project(Path(project_name), Path(project_name).name, profile_id=profile)
    except (FileExistsError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    for path in created:
        print(path)
    return 0


def _run_scan(path: str) -> int:
    findings = scan_file(path)
    for finding in findings:
        print(f"{finding.line}:{finding.column}\t{finding.finding_type}\t{finding.preview}")
    if not findings:
        print("No supported identifier patterns found.")
        return 0
    return 1


def _run_redact(input_path: str, output_path: str) -> int:
    try:
        destination = redact_file(input_path, output_path)
    except (FileExistsError, ValueError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(destination)
    return 0


def _run_sources_list() -> int:
    for profile in list_profiles():
        print(f"{profile['id']}\t{profile['name']}")
    return 0


def _run_sources_show(profile: str) -> int:
    try:
        print(format_profile(load_profile(profile)))
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    return 0


def _run_run_chart(
    input_path: str,
    output_path: str,
    value_column: str,
    date_column: str | None,
    baseline_points: int | None,
    run_length: int,
    trend_length: int,
) -> int:
    try:
        result = analyse_run_chart_csv(
            input_path,
            output_path,
            value_column=value_column,
            date_column=date_column,
            baseline_points=baseline_points,
            run_length=run_length,
            trend_length=trend_length,
        )
    except (FileExistsError, ValueError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(
        f"{result.output_path}\trows={result.row_count}\tmedian={result.baseline_median:g}"
        f"\tshifts={result.shift_signals}\ttrends={result.trend_signals}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
