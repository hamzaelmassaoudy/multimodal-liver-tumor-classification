import csv
import json
from pathlib import Path

import pytest

from liver_tumor_pipeline.validation import validate_aggregate_directory

ROOT = Path(__file__).resolve().parents[1]
AGGREGATE = ROOT / "results" / "aggregate"


def test_aggregate_result_schemas_are_valid():
    assert validate_aggregate_directory(AGGREGATE) == []


def test_locked_internal_auc_values():
    with (AGGREGATE / "internal_performance.csv").open(newline="", encoding="utf-8") as stream:
        rows = {row["model"]: row for row in csv.DictReader(stream)}
    assert float(rows["W3 single-phase CNN"]["heldout_macro_auc"]) == pytest.approx(0.860)
    assert float(rows["W4 multiphase CNN"]["heldout_macro_auc"]) == pytest.approx(0.906)
    assert float(rows["W5 radiomics-LightGBM"]["heldout_macro_auc"]) == pytest.approx(0.938)
    assert float(rows["Full fusion"]["heldout_macro_auc"]) == pytest.approx(0.950)


def test_external_scenarios_are_locked():
    with (AGGREGATE / "external_stress_test.csv").open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    sex_zero = next(row for row in rows if "sex=0" in row["scenario"])
    sex_one = next(row for row in rows if "sex=1" in row["scenario"])
    assert float(sex_zero["hcc_sensitivity"]) == pytest.approx(0.019)
    assert float(sex_one["hcc_sensitivity"]) == pytest.approx(0.806)
    assert int(sex_one["changed_predictions_relative_to_historical"]) == 82


def test_reproducibility_boundary_is_explicit():
    status = json.loads((AGGREGATE / "reproducibility_status.json").read_text(encoding="utf-8"))
    assert status["exact_end_to_end_reconstruction"] is False
    assert status["patient_level_artifacts_public"] is False


def test_c2_crop_retention_values_are_locked():
    with (AGGREGATE / "c2_crop_retention.csv").open(newline="", encoding="utf-8") as stream:
        rows = {row["metric"]: row for row in csv.DictReader(stream)}
    assert int(rows["Exact retention"]["count"]) == 124
    assert int(rows["Some tumor loss"]["count"]) == 154
    assert int(rows["Retention below 90%"]["count"]) == 67
    assert int(rows["Empty crops"]["count"]) == 0
    assert float(rows["Median retention"]["percent"]) == pytest.approx(99.89)
    assert float(rows["Minimum retention"]["percent"]) == pytest.approx(15.64)
    assert float(rows["Volume-weighted retention"]["percent"]) == pytest.approx(61.46)


def test_radiomics_imputation_controls_are_locked():
    with (AGGREGATE / "radiomics_imputation_controls.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        values = [float(row["hcc_sensitivity"]) for row in csv.DictReader(stream)]
    assert values == pytest.approx([0.961, 1.000, 0.243, 0.010, 0.971])


def test_corrected_delong_attribution_is_locked():
    with (AGGREGATE / "delong_summary.csv").open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    minimum = min(rows, key=lambda row: float(row["reported_raw_p"]))
    assert minimum["comparison"] == "full_fusion vs multi_phase_cnn"
    assert minimum["class"] == "cHCC-CCA"
    assert float(minimum["reported_raw_p"]) == pytest.approx(0.0293)
    w5_combined = next(
        row
        for row in rows
        if row["comparison"] == "full_fusion vs radiomics" and row["class"] == "cHCC-CCA"
    )
    assert float(w5_combined["reported_raw_p"]) == pytest.approx(0.3457)
