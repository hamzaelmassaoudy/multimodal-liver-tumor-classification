# Revision notebooks (15–33)

The nineteen revision notebooks are the code that produced every result of the
[October 2026 revision](revision_2026-10.md). They ran on Google Colab, with a GPU for the CNN analyses,
against the private project folder, and are published with outputs cleared and with every
machine-specific location replaced by an environment variable.

## Notebooks

| No. | Notebook | Analysis ID | What it does |
|---:|---|---|---|
| 15 | [Reproduce submitted results; radiomics without shape](../notebooks/06_revision_internal_models_and_statistics/15_reproduce_submitted_results_and_noshape_radiomics.ipynb) | E1, E2 | Reproduces all 75 submitted values exactly, then refits radiomics without the 56 shape features |
| 16 | [Missing phases and phase-dropout CNN](../notebooks/06_revision_internal_models_and_statistics/16_missing_phases_and_phase_dropout_cnn.ipynb) | E3 | Missing-phase tests of the saved CNN; retrains with an inner validation split, with and without phase dropout |
| 17 | [HCC-TACE-Seg, repaired pipeline](../notebooks/07_revision_external_validation_and_mitigation/17_hcc_tace_seg_repaired_pipeline.ipynb) | E5 | Reproduces the submitted external result, then corrects the intensity window and links observed age and sex |
| 18 | [MCT-LTDiag download](../notebooks/07_revision_external_validation_and_mitigation/18_mct_ltdiag_download.ipynb) | E6a | Downloads the 103 HCC and 100 ICC cases and checks every file against its published checksum |
| 19 | [MCT-LTDiag external validation](../notebooks/07_revision_external_validation_and_mitigation/19_mct_ltdiag_external_validation.ipynb) | E6 | Frozen-model HCC-versus-ICC validation with pre-specified preprocessing variants |
| 20 | [HCC-TACE-Seg, axis corrected](../notebooks/07_revision_external_validation_and_mitigation/20_hcc_tace_seg_axis_corrected.ipynb) | E5c | Fixes the axis order of the external volumes and applies the internal geometry rules |
| 21 | [MCT-LTDiag, all 203, and radiomics mitigation](../notebooks/07_revision_external_validation_and_mitigation/21_mct_ltdiag_all_203_and_radiomics_mitigation.ipynb) | E8.0, E8a | Restores two excluded patients; ComBat and perturbation-robust radiomics |
| 22 | [Truncation, size, statistics, calibration](../notebooks/06_revision_internal_models_and_statistics/22_truncation_size_statistics_calibration.ipynb) | E47 | Crop truncation, size strata, calibration, optimism, and multiplicity-adjusted comparisons from saved predictions |
| 23 | [Repeated cross-validation](../notebooks/06_revision_internal_models_and_statistics/23_repeated_cross_validation.ipynb) | E7a | 5 × 5 repeated cross-validation (repeat 0 with the saved models; repeats 1–4 retrain the whole pipeline) |
| 24 | [CNN mitigation and models without non-contrast](../notebooks/07_revision_external_validation_and_mitigation/24_cnn_mitigation_and_models_without_noncontrast.ipynb) | E8b, E9, E8c | Test-time harmonization, scanner-variation training, models without the non-contrast phase, mitigated fusion |
| 25 | [Adaptive-crop CNN](../notebooks/06_revision_internal_models_and_statistics/25_adaptive_crop_cnn.ipynb) | E4d | Trains and evaluates the CNN on size-adaptive crops |
| 26 | [Dataset audit and counterfactual test](../notebooks/08_revision_dataset_audit_and_explainability/26_dataset_audit_and_counterfactual_test.ipynb) | E10 | File-level census of 1,112 scans and the slice-resampling counterfactual test |
| 27 | [Grad-CAM attribution and examples](../notebooks/08_revision_dataset_audit_and_explainability/27_gradcam_attribution_and_examples.ipynb) | F2 | Quantitative Grad-CAM enrichment and per-phase attribution |
| 28 | [Corrected-mask sensitivity analysis](../notebooks/08_revision_dataset_audit_and_explainability/28_corrected_mask_liver_union_tumour.ipynb) | E11 | Repeats the pipeline with liver ∪ tumor masks (all models retrained); internal, artifact test, and MCT-LTDiag versus the main models |
| 29 | [Equalized slice density](../notebooks/08_revision_dataset_audit_and_explainability/29_equalized_slice_density.ipynb) | E12 | Resamples every scan to one anatomical slice density before cropping (all models retrained); slice-count signal, internal, residual artifact, and MCT-LTDiag versus the main models |
| 30 | [Nested stacking](../notebooks/06_revision_internal_models_and_statistics/30_nested_stacking.ipynb) | E13 | Fully nested evaluation of the stacked fusions: inner four-fold cross-validation inside every outer fold of the five repeats (100 CNN trainings) |
| 31 | [Acquisition-matched test, frozen models](../notebooks/08_revision_dataset_audit_and_explainability/31_acquisition_matched_frozen_models.ipynb) | E14a | Gives every internal scan the slice spacing of MCT-LTDiag by averaging adjacent slices, with a blur-only control, and evaluates the frozen main models; also a thick non-contrast reconstruction |
| 32 | [Acquisition-matched retraining](../notebooks/08_revision_dataset_audit_and_explainability/32_acquisition_matched_retraining.ipynb) | E14b | Retrains every model with all scans at the slice spacing of MCT-LTDiag; slice-count signal, internal, residual artifact, and MCT-LTDiag versus the main models |
| 33 | [CNN training-seed variability](../notebooks/06_revision_internal_models_and_statistics/33_cnn_training_seed_variability.ipynb) | E15 | Retrains the main CNN with five further seeds and once with its own seed, and refits both fusions for each |

Numbers follow the order in which the analyses ran; the folders group them by topic. The analysis IDs
refer to the dated analysis log in which each analysis was planned and approved before it was run;
notebook text that cites "00 log" sections refers to that log. Its plan sections are published as the
[analysis plans](analysis_plans.md); the rest is kept with the private project records.

## Safeguards built into the notebooks

- **Reproduction gates.** Each analysis notebook first checks that it reproduces the saved results
  it builds on (for example, the frozen models must reproduce their saved predictions) and stops
  otherwise. The download notebook (18) checks every file against its published checksum.
- **Input fingerprints.** Inputs are checked against recorded checksums before use.
- **Run folders.** Every run writes to its own time-stamped folder, so earlier results are not
  overwritten.
- **Resumable training.** The training notebooks reuse folds already trained after an interruption.

## Environment variables

| Variable | Used by | Meaning |
|---|---|---|
| `COLAB_DRIVE_MOUNT` | all except 18 | Mount point passed to `google.colab.drive.mount` |
| `LIVER_PROJECT_ROOT` | all except 18 | Folder that contains `liver_project/` (run outputs) and `liver_data/` (PLC-CECT) |
| `LIVER_HISTORICAL_PREFIX` | 17, 20, 24, 25 | Folder prefix stored inside older run manifests; it is replaced by the current project location when those manifests are read |
| `LIVER_DRIVE_PROJECT_FOLDER_ID`, `LIVER_DRIVE_EXTERNAL_FOLDER_ID` | 18 | Drive folder identifiers of the project and of its external-data folder, used by the Drive API upload |

Variables ending in `_TEST_ROOT`, `_TEST_PROCESSED`, `_TEST_WORK`, `_TEST_TMP`, `_TEST_GLOSSARY`, `_TEST_E`,
`_TEST_OFFSETS`, or `_TEST_EPOCHS`
are read only outside Colab, by the local synthetic-data test harness used to check each notebook
before it ran on real data.

## Running them

The notebooks need the source datasets ([PLC-CECT](datasets.md), MCT-LTDiag, HCC-TACE-Seg) and the
private outputs of the original workflow (notebooks 01–14), including the fold checkpoints. Without
those, they serve as an exact record of what was run. The tables they produced are summarized,
without patient-level rows, by
[`scripts/revision/export_revision_aggregates.py`](../scripts/revision/export_revision_aggregates.py),
and the manuscript figures are drawn by
[`scripts/revision/make_revision_figures.py`](../scripts/revision/make_revision_figures.py).
