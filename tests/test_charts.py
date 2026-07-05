import csv

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
