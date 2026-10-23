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


def test_corrected_mask_analysis_values_are_locked():
    internal = row(read_csv("corrected_mask_internal_paired.csv"), model="CNN + radiomics")
    assert float(internal["heldout_difference_E11_minus_main"]) == pytest.approx(0.0112775)
    assert float(internal["boot_low"]) < 0 < float(internal["boot_high"])
    effects = read_csv("corrected_mask_counterfactual_effects.csv")
    for test in [
        "non-contrast artefact injected (HCC, ICC)",
        "non-contrast artefact repaired (cHCC-CCA)",
    ]:
        cnn = row(effects, model="CNN", test=test, subset="all 278")
        assert cnn["meets_rule"] == "True" and cnn["smoothing_control_ok"] == "True"
    external = row(read_csv("corrected_mask_external.csv"), pipeline="E11", model="CNN + radiomics")
    assert float(external["auc"]) == pytest.approx(0.570777, abs=1e-6)
    paired = row(read_csv("corrected_mask_external_paired.csv"), model="CNN + radiomics")
    assert float(paired["delong_p"]) > 0.05


def test_equalized_slice_density_values_are_locked():
    density = [
        r for r in read_csv("equalized_density_by_class.csv") if r["quantity"] == "ratio_after"
    ]
    assert len(density) == 4 and max(float(r["max_over_min"]) for r in density) <= 1.25
    counts = read_csv("equalized_density_slice_count_model.csv")
    assert float(row(counts, slices="n_before")["heldout_macro_auc"]) == pytest.approx(0.852975)
    assert float(row(counts, slices="n_after")["heldout_macro_auc"]) == pytest.approx(0.678046)
    internal = row(read_csv("equalized_density_internal_paired.csv"), model="CNN + radiomics")
    assert float(internal["boot_low"]) < 0 < float(internal["boot_high"])
    residual = row(
        read_csv("equalized_density_residual_artifact.csv"),
        model="CNN",
        test="non-contrast artifact injected before equalization (HCC, ICC)",
        subset="all 278",
    )
    assert residual["meets_E10_thresholds"] == "True"
    external = row(
        read_csv("equalized_density_external.csv"), pipeline="E12", model="CNN + radiomics"
    )
    assert float(external["auc"]) == pytest.approx(0.510, abs=5e-4)
    paired = read_csv("equalized_density_external_paired.csv")
    assert float(row(paired, model="CNN + radiomics")["delong_p"]) > 0.05
    radiomics = row(paired, model="radiomics")
    assert (
        float(radiomics["auc_difference_E12_minus_main"]) < 0
        and float(radiomics["delong_p"]) < 0.001
    )


def test_acquisition_matched_tests_are_locked():
    frozen = read_csv("acquisition_matched_frozen_hcc_vs_icc.csv")
    primary = row(frozen, model="CNN + radiomics", cohort="held-out", condition="mct")
    assert float(primary["auc"]) == pytest.approx(0.794737, abs=1e-6)
    assert float(primary["boot_high"]) < 0 and float(primary["auc"]) >= 0.763
    assert primary["plan_rule_reading"] == "explains part of the external loss"
    blur = row(frozen, model="CNN + radiomics", cohort="held-out", condition="mct_smooth")
    assert float(blur["boot_low"]) < 0 < float(blur["boot_high"])
    thick = row(
        read_csv("acquisition_matched_frozen_thick_noncontrast.csv"),
        model="CNN",
        subset="all HCC/ICC",
    )
    assert thick["meets_rule"] == "True" and thick["smoothing_control_ok"] == "True"
    paired = row(
        read_csv("acquisition_matched_retrained_internal_paired.csv"), model="CNN + radiomics"
    )
    assert float(paired["boot_low"]) < 0 < float(paired["boot_high"])
    external = row(
        read_csv("acquisition_matched_retrained_external.csv"),
        pipeline="E14b",
        model="CNN + radiomics",
    )
    assert float(external["auc"]) == pytest.approx(0.626699, abs=1e-6)
    ext_paired = row(
        read_csv("acquisition_matched_retrained_external_paired.csv"), model="CNN + radiomics"
    )
    assert float(ext_paired["delong_p"]) > 0.05


def test_training_seed_spread_is_locked():
    spread = row(read_csv("seed_variability_spread.csv"), model="CNN", metric="heldout_macro_auc")
    assert float(spread["range_plan_seeds"]) == pytest.approx(0.0217, abs=1e-4)
    assert float(spread["range_plan_seeds"]) >= 0.013
    fused = row(
        read_csv("seed_variability_spread.csv"), model="CNN + radiomics", metric="heldout_macro_auc"
    )
    assert float(fused["sd_all_seeds"]) < 0.005
    assert len(read_csv("seed_variability_per_seed.csv")) == 21


def test_nested_stacking_is_not_optimistic():
    for model in ["cnn_plus_radiomics", "full_fusion"]:
        summary = row(read_csv("nested_stacking_summary.csv"), model=model)
        assert int(summary["repeats"]) == 5
        assert float(summary["optimism_max"]) <= 0
        assert int(summary["repeats_nested_above_CNN"]) == 5
        assert int(summary["repeats_nested_above_radiomics"]) == 5
    assert len(read_csv("nested_stacking_per_repeat.csv")) == 10


def test_full_fusion_advantage_disappears_within_sex():
    rows = read_csv("external_mct_ltdiag_by_sex.csv")
    overall = row(rows, group="all", model="full fusion - CNN + radiomics")
    assert float(overall["paired_delong_p"]) < 0.01
    for group in ["men", "women"]:
        within = row(rows, group=group, model="full fusion - CNN + radiomics")
        assert abs(float(within["auc"])) < 0.01 and float(within["paired_delong_p"]) > 0.5
