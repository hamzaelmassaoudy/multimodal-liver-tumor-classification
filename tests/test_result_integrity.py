import csv
import json
from pathlib import Path

import pytest

from liver_tumor_pipeline.validation import validate_aggregate_directory

ROOT = Path(__file__).resolve().parents[1]
AGGREGATE = ROOT / "results" / "aggregate"


def read_csv(name):
    with (AGGREGATE / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def test_aggregate_result_schemas_are_valid():
    assert validate_aggregate_directory(AGGREGATE) == []


def test_corrected_primary_internal_auc_values():
    rows = {row["model"]: row for row in read_csv("internal_performance.csv")}
    assert float(rows["Clinical baseline"]["heldout_macro_auc"]) == pytest.approx(0.614432)
    assert float(rows["W3 single-phase CNN"]["heldout_macro_auc"]) == pytest.approx(0.859849)
    assert float(rows["W4 multiphase CNN"]["heldout_macro_auc"]) == pytest.approx(0.906425)
    assert float(rows["W5 radiomics-LightGBM"]["heldout_macro_auc"]) == pytest.approx(0.938032)
    assert float(rows["Full fusion"]["heldout_macro_auc"]) == pytest.approx(0.945452)
    assert float(rows["Full fusion"]["heldout_accuracy"]) == pytest.approx(0.803571)


def test_internal_sex_provenance_and_sensitivity_are_locked():
    provenance = {row["metric"]: row for row in read_csv("internal_sex_provenance.csv")}
    assert int(provenance["Male"]["count"]) == 185
    assert int(provenance["Female"]["count"]) == 90
    assert int(provenance["Unresolved"]["count"]) == 3
    sensitivity = read_csv("internal_sex_sensitivity.csv")
    primary = next(
        row
        for row in sensitivity
        if row["model"] == "Full fusion" and row["scenario"].startswith("Corrected")
    )
    historical = next(
        row
        for row in sensitivity
        if row["model"] == "Full fusion" and row["scenario"].startswith("Historical")
    )
    assert float(primary["heldout_macro_auc"]) == pytest.approx(0.945452)
    assert float(historical["heldout_macro_auc"]) == pytest.approx(0.949675)
    assert int(primary["changed_heldout_predictions"]) == 1


def test_external_scenarios_are_locked_and_primary_is_explicit():
    rows = read_csv("external_stress_test.csv")
    primary = next(row for row in rows if row["scenario"] == "Missing sex, fold-local median")
    sex_zero = next(row for row in rows if row["scenario"] == "Encoded sex=0 sensitivity")
    assert float(primary["hcc_sensitivity"]) == pytest.approx(0.805825)
    assert (
        int(primary["predicted_hcc"]),
        int(primary["predicted_icc"]),
        int(primary["predicted_chcc"]),
    ) == (83, 7, 13)
    assert float(sex_zero["hcc_sensitivity"]) == pytest.approx(0.019417)
    assert int(sex_zero["changed_predictions_vs_primary"]) == 82


def test_reproducibility_boundary_is_explicit():
    status = json.loads((AGGREGATE / "reproducibility_status.json").read_text(encoding="utf-8"))
    assert status["corrected_internal_sex_analysis"] is True
    assert status["aggregate_external_adapter_qc_reporting"] is True
    assert status["exact_end_to_end_reconstruction"] is False
    assert status["patient_level_artifacts_public"] is False


def test_c2_crop_retention_values_are_locked():
    rows = {row["metric"]: row for row in read_csv("c2_crop_retention.csv")}
    assert int(rows["Exact retention"]["count"]) == 124
    assert int(rows["Some tumor loss"]["count"]) == 154
    assert int(rows["Retention below 90%"]["count"]) == 67
    assert int(rows["Empty crops"]["count"]) == 0
    assert float(rows["Median retention"]["percent"]) == pytest.approx(99.89)
    assert float(rows["Minimum retention"]["percent"]) == pytest.approx(15.64)
    assert float(rows["Volume-weighted retention"]["percent"]) == pytest.approx(61.46)


def test_radiomics_imputation_controls_are_locked():
    rows = read_csv("radiomics_imputation_controls.csv")
    values = [float(row["hcc_sensitivity"]) for row in rows]
    assert values == pytest.approx([0.961165, 1.000000, 0.242718, 0.009709, 0.970874])
    condition_c = next(row for row in rows if row["condition_code"] == "C")
    assert condition_c["model_status"] == "Internal diagnostic refit"


def test_corrected_delong_values_are_locked():
    rows = read_csv("delong_summary.csv")
    minimum = min(rows, key=lambda row: float(row["uncorrected_p"]))
    assert minimum["comparison"] == "full_fusion vs multi_phase_cnn"
    assert minimum["class"] == "cHCC-CCA"
    assert float(minimum["uncorrected_p"]) == pytest.approx(0.029347)
    assert float(minimum["bonferroni_p_9"]) == pytest.approx(0.264126)
    w5_combined = next(
        row
        for row in rows
        if row["comparison"] == "full_fusion vs radiomics" and row["class"] == "cHCC-CCA"
    )
    assert float(w5_combined["uncorrected_p"]) == pytest.approx(0.345737)


def test_corrected_confusion_matrix_is_locked():
    payload = json.loads(
        (AGGREGATE / "internal_confusion_matrices.json").read_text(encoding="utf-8")
    )
    assert payload["class_order"] == ["HCC", "ICC", "cHCC-CCA"]
    assert payload["matrices"]["Full fusion"] == [[17, 1, 1], [4, 15, 1], [3, 1, 13]]
