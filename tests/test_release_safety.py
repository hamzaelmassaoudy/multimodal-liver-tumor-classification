from pathlib import Path

from liver_tumor_pipeline.validation import (
    markdown_link_issues,
    notebook_output_issues,
    notebook_syntax_issues,
    release_safety_issues,
)

ROOT = Path(__file__).resolve().parents[1]


def test_notebook_outputs_and_execution_counts_are_cleared():
    assert notebook_output_issues(ROOT) == []
    assert notebook_syntax_issues(ROOT) == []


def test_canonical_notebook_sequence_is_complete():
    expected = {
        "01_internal_cohort_and_splits.ipynb",
        "02_historical_independent_phase_preprocessing.ipynb",
        "03_single_phase_cnn.ipynb",
        "04_multiphase_cnn.ipynb",
        "05_radiomics_lightgbm.ipynb",
        "06_late_fusion_internal_evaluation.ipynb",
        "07_external_data_acquisition.ipynb",
        "08_external_dicom_to_nifti.ipynb",
        "09_external_tumor_mask_preprocessing.ipynb",
        "10_external_mask_density_qc.ipynb",
        "11_external_liver_mask_adapter.ipynb",
        "12_external_frozen_inference.ipynb",
        "13_radiomics_imputation_controls.ipynb",
        "14_explainability_and_aggregate_figures.ipynb",
    }
    actual = {path.name for path in (ROOT / "notebooks").rglob("*.ipynb")}
    assert actual == expected


def test_public_tree_has_no_local_paths_or_patient_file_types():
    assert release_safety_issues(ROOT) == []


def test_relative_markdown_links_resolve():
    assert markdown_link_issues(ROOT) == []
