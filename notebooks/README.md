# Canonical notebook sequence

These 14 notebooks document the study workflow and aggregate analyses. Every committed notebook
has no outputs, execution counts, attachments, patient data, or machine-specific paths.

Internal preprocessing independently centers P, C1, C2, and C3 crops and performs no explicit
interphase registration. The corrected primary clinical/fusion analysis retains unresolved sex as
missing and uses fold-local medians. The historical non-male-to-zero rule is sensitivity-only.

Create ignored `configs/paths.yaml` from `configs/paths.example.yaml` only when user-obtained data
or authorized local artifacts are available. Patient-linked outputs must remain outside Git.

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
| 12 | [External frozen inference](04_external_stress_test/12_external_frozen_inference.ipynb) | Public aggregate reanalysis; complete historical CNN inference unavailable |
| 13 | [Radiomics imputation controls](04_external_stress_test/13_radiomics_imputation_controls.ipynb) | Public aggregate reanalysis; private artifacts required for rerun |
| 14 | [Explainability and aggregate figures](05_figures_and_tables/14_explainability_and_aggregate_figures.ipynb) | Public aggregate figure generation; private artifacts required for case-level explainability |

## Boundaries

- W3 fold 1 and W4 fold 0 checkpoints were not retained.
- Source geometry, spacing, and phase-specific crop coordinates were not retained.
- Public C2 crop-retention findings apply only to C2.
- W5 is crop-restricted radiomics and its shape outputs are not verified physical-unit measures.
- Exact full fusion contains W4 and W5 probability triplets, age, and sex; W3 is excluded.
- External values are HCC sensitivities under model-defined unavailable-covariate scenarios.

See [reproducibility](../docs/reproducibility.md) and
[artifact contracts](../docs/artifact_contracts.md).
