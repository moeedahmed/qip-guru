import csv

import pytest

from qip_guru.charts import analyse_run_chart_csv


def test_run_chart_analysis_writes_annotated_csv(tmp_path):
    output_path = tmp_path / "ed_flow_run_chart.csv"

    result = analyse_run_chart_csv(
        "examples/synthetic_ed_flow_qip.csv",
        output_path,
        value_column="median_time_to_initial_assessment_minutes",
        date_column="week",
        baseline_points=4,
    )

    assert result.output_path == output_path
    assert result.row_count == 12
    assert result.baseline_median == 41.5
    assert result.shift_signals >= 1
    assert result.trend_signals >= 1

    with output_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert rows[0]["qip_baseline_median"] == "41.5"
    assert rows[-1]["qip_shift_signal"] == "yes"
    assert rows[-1]["qip_trend_signal"] == "yes"


def test_run_chart_rejects_missing_value_column(tmp_path):
    output_path = tmp_path / "missing.csv"

    try:
        analyse_run_chart_csv(
            "examples/synthetic_ed_flow_qip.csv",
            output_path,
            value_column="not_a_column",
        )
    except ValueError as exc:
        assert "value column not found" in str(exc)
    else:
        raise AssertionError("missing value column should raise ValueError")


def _write_csv(path, contents):
    path.write_text(contents, encoding="utf-8")
    return path


@pytest.mark.parametrize(
    ("contents", "message"),
    [
        ("", "missing a header row"),
        ("value\n", "no data rows"),
        ("value,other\n1\n", "malformed CSV row 2: expected 2 fields, found 1"),
        ("value\n1,unexpected\n", "malformed CSV row 2: expected 1 fields, found 2"),
        ("value\n\n", "malformed CSV row 2"),
        ('value\n"unterminated\n', "malformed CSV row 2"),
    ],
)
def test_run_chart_rejects_missing_or_malformed_rows(tmp_path, contents, message):
    input_path = _write_csv(tmp_path / "input.csv", contents)

    with pytest.raises(ValueError, match=message):
        analyse_run_chart_csv(input_path, tmp_path / "output.csv", value_column="value")


@pytest.mark.parametrize(
    ("raw_value", "message"),
    [
        (" ", "blank at CSV row 2"),
        ("not-a-number", "non-numeric data at CSV row 2"),
        ("NaN", "non-finite number at CSV row 2"),
        ("inf", "non-finite number at CSV row 2"),
        ("-Infinity", "non-finite number at CSV row 2"),
    ],
)
def test_run_chart_rejects_invalid_values(tmp_path, raw_value, message):
    input_path = _write_csv(tmp_path / "input.csv", f"value\n{raw_value}\n")

    with pytest.raises(ValueError, match=message):
        analyse_run_chart_csv(input_path, tmp_path / "output.csv", value_column="value")


@pytest.mark.parametrize(
    ("header", "message"),
    [
        ("value, ", "blank header at column 2"),
        ("value,value", "duplicate header: value"),
        ("value,qip_index", "conflicts with generated output column: qip_index"),
    ],
)
def test_run_chart_rejects_invalid_headers(tmp_path, header, message):
    input_path = _write_csv(tmp_path / "input.csv", f"{header}\n1,2\n")

    with pytest.raises(ValueError, match=message):
        analyse_run_chart_csv(input_path, tmp_path / "output.csv", value_column="value")


def test_run_chart_refuses_to_overwrite_existing_output(tmp_path):
    input_path = _write_csv(tmp_path / "input.csv", "value\n1\n2\n")
    output_path = _write_csv(tmp_path / "output.csv", "keep me\n")

    with pytest.raises(FileExistsError, match="output file already exists"):
        analyse_run_chart_csv(input_path, output_path, value_column="value")

    assert output_path.read_text(encoding="utf-8") == "keep me\n"
