# Notebooks

The 27 notebooks document the original study workflow (01–14) and the October 2026 revision
analyses (15–27). Every committed notebook has no outputs, execution counts, attachments, patient
data, or machine-specific paths.

Create ignored `configs/paths.yaml` from `configs/paths.example.yaml` only when user-obtained data
or authorized local artifacts are available. Patient-linked outputs must remain outside Git.

## Original workflow (01–14)

Internal preprocessing independently centers P, C1, C2, and C3 crops and performs no explicit
interphase registration. The corrected primary clinical/fusion analysis retains unresolved sex as
missing and uses fold-local medians. The historical non-male-to-zero rule is sensitivity-only.

| Order | Notebook | Classification |
|---:|---|---|
| 1 | [Internal cohort and splits](01_data_and_preprocessing/01_internal_cohort_and_splits.ipynb) | Public dataset plus configured private storage |
| 2 | [Independent-phase preprocessing and sex provenance](01_data_and_preprocessing/02_historical_independent_phase_preprocessing.ipynb) | Public dataset plus configured private storage |
| 3 | [W3 single-phase CNN](02_internal_models/03_single_phase_cnn.ipynb) | Historical workflow requiring private artifacts |
| 4 | [W4 multiphase CNN](02_internal_models/04_multiphase_cnn.ipynb) | Historical workflow requiring private artifacts |
| 5 | [W5 radiomics-LightGBM](02_internal_models/05_radiomics_lightgbm.ipynb) | Historical workflow requiring private artifacts |
| 6 | [Late fusion and internal evaluation](03_fusion_and_internal_results/06_late_fusion_internal_evaluation.ipynb) | Public aggregate reanalysis; private artifacts required for refitting |
| 7 | [External data acquisition](04_external_stress_test/07_external_data_acquisition.ipynb) | Public acquisition into private storage |
| 8 | [External DICOM-to-NIfTI](04_external_stress_test/08_external_dicom_to_nifti.ipynb) | Public dataset plus configured private storage |
| 9 | [External tumor-mask preprocessing](04_external_stress_test/09_external_tumor_mask_preprocessing.ipynb) | Public dataset plus operator-controlled private review |
| 10 | [External mask-density QC](04_external_stress_test/10_external_mask_density_qc.ipynb) | Historical workflow requiring private images and masks |
| 11 | [External liver-mask adapter](04_external_stress_test/11_external_liver_mask_adapter.ipynb) | Historical per-case method interface |
| 12 | [External frozen inference](04_external_stress_test/12_external_frozen_inference.ipynb) | Public aggregate reanalysis; CNN inference requires private checkpoints |
| 13 | [Radiomics imputation controls](04_external_stress_test/13_radiomics_imputation_controls.ipynb) | Public aggregate reanalysis; private artifacts required for rerun |
| 14 | [Explainability and aggregate figures](05_figures_and_tables/14_explainability_and_aggregate_figures.ipynb) | Public aggregate figure generation; private artifacts required for case-level explainability |

## Revision analyses (15–27)

These notebooks produced every result of the [revision](../docs/revision_2026-10.md). Each analysis
notebook stops unless it first reproduces the saved results it builds on; the download notebook (18)
checks every file against its published checksum instead. The
[revision notebook guide](../docs/revision_notebooks.md) describes each notebook and its
environment variables.

| Folder | Notebooks |
|---|---|
| [`06_revision_internal_models_and_statistics`](06_revision_internal_models_and_statistics) | 15 reproduction and radiomics without shape · 16 missing phases and phase-dropout CNN · 22 truncation, size, calibration, statistics · 23 repeated cross-validation · 25 adaptive-crop CNN |
| [`07_revision_external_validation_and_mitigation`](07_revision_external_validation_and_mitigation) | 17 HCC-TACE-Seg repaired · 18 MCT-LTDiag download · 19 MCT-LTDiag validation · 20 HCC-TACE-Seg axis corrected · 21 all 203 patients and radiomics mitigation · 24 CNN mitigation and models without non-contrast |
| [`08_revision_dataset_audit_and_explainability`](08_revision_dataset_audit_and_explainability) | 26 dataset audit and counterfactual test · 27 Grad-CAM attribution |

Numbers follow the order in which the analyses ran.

## Boundaries

- Fold checkpoints of all CNNs are retained privately and are not distributed. (v1.1.0 stated
  that W3 fold 1 and W4 fold 0 were not retained; that was wrong.)
- The released PLC-CECT files carry no physical spacing; radiomics shape features were therefore
  removed in the revision.
- External values in notebooks 07–13 are HCC sensitivities of the submitted analysis; the
  revised external analysis is in notebooks 17–21 and 24.
- Exact full fusion contains CNN and radiomics probability triplets, age, and sex; W3 is excluded.

See [reproducibility](../docs/reproducibility.md) and
[artifact contracts](../docs/artifact_contracts.md).
