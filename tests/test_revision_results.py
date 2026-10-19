import csv
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REVISION = ROOT / "results" / "revision_2026-10"
IDENTIFIER_COLUMNS = {"patient_id", "case_id", "subject_id", "accession_number", "dicom_uid"}


def read_csv(name):
    with (REVISION / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def row(rows, **match):
    hits = [r for r in rows if all(r[key] == value for key, value in match.items())]
    assert len(hits) == 1, match
    return hits[0]


def test_every_revision_file_is_documented_and_present():
    readme = (REVISION / "README.md").read_text(encoding="utf-8")
    documented = set(re.findall(r"\]\(((?:figures/)?[\w.-]+\.(?:csv|png))\)", readme))
    on_disk = {p.relative_to(REVISION).as_posix() for p in REVISION.rglob("*") if p.is_file()}
    assert documented == on_disk - {"README.md"}


def test_revision_tables_are_cohort_level():
    for path in REVISION.glob("*.csv"):
        rows = read_csv(path.name)
        assert rows, path.name
        assert not set(rows[0]) & IDENTIFIER_COLUMNS, path.name


def test_patient_image_figures_are_not_published():
    names = {p.name for p in (REVISION / "figures").glob("*")}
    assert names == {
        "figure1_study_design.png",
        "figure3_internal_performance.png",
        "figure4_size_truncation.png",
        "figure5_dataset_artifacts.png",
        "figure7_external_validation.png",
    }


def test_internal_headline_values_are_locked():
    models = read_csv("internal_models.csv")
    primary = row(models, model="CNN + radiomics")
    assert float(primary["heldout_macro_auc"]) == pytest.approx(0.952114)
    assert float(primary["heldout_ci_low"]) == pytest.approx(0.905916)
    assert float(primary["heldout_ci_high"]) == pytest.approx(0.98461)
    assert float(primary["repeated_cv_oof_mean"]) == pytest.approx(0.941697)
    cnn = row(models, model="phase-dropout CNN (main)")
    assert float(cnn["heldout_macro_auc"]) == pytest.approx(0.919178)
    comparison = row(
        read_csv("internal_comparisons.csv"), comparison="full fusion - CNN + radiomics"
    )
    assert float(comparison["heldout_difference"]) == pytest.approx(-0.000714483)
    assert float(comparison["smallest_bh_delong_p"]) > 0.05


def test_dataset_audit_values_are_locked():
    audit = read_csv("dataset_audit_by_class.csv")
    files = sum(int(r["value"]) for r in audit if r["measure"] == "files")
    assert files == 1112
    slices = {
        r["class"]: float(r["value"])
        for r in audit
        if r["phase"] == "C2" and r["measure"] == "median_slices"
    }
    assert slices == {"HCC": 93.0, "ICC": 195.0, "cHCC-CCA": 126.0}
    effects = read_csv("counterfactual_effects.csv")
    injected = row(
        effects,
        model="CNN",
        test="non-contrast artefact injected (HCC, ICC)",
        subset="all 278",
    )
    assert float(injected["mean_shift_vs_smoothing_control"]) == pytest.approx(0.253744)
    assert injected["meets_rule"] == "True"
    inside = row(
        read_csv("tumor_inside_liver_mask_by_class_phase.csv"), **{"class": "ICC"}, phase="C2"
    )
    assert int(inside["n_lt_0.9"]) == 52


def test_external_headline_values_are_locked():
    mct = read_csv("external_mct_ltdiag.csv")
    primary = row(
        mct, model="cnn_plus_radiomics [phase_dropout_CNN]", variant="primary", subset="all"
    )
    assert (int(primary["n_HCC"]), int(primary["n_ICC"])) == (103, 100)
    assert float(primary["auc"]) == pytest.approx(0.578252)
    comparisons = read_csv("external_mct_ltdiag_mitigation_comparisons.csv")
    assert len(comparisons) == 26
    assert min(float(r["bh_adjusted_p"]) for r in comparisons) > 0.05
    tace = row(
        read_csv("external_hcc_tace_seg.csv"),
        model="phase_dropout_CNN",
        variant="axis_fixed_E6rules",
        subset="clean_89",
    )
    assert int(tace["hcc_correct"]) == 47
