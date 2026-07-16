# Canonical notebook sequence

These 14 notebooks document the workflow that produced the reported study results and the
aggregate analyses that remain reproducible from released artifacts. Every committed notebook is
stored without outputs, execution counts, attachments, patient data, or machine-specific paths.

The historical internal preprocessing uses independent tumor-centroid crops for P, C1, C2, and
C3. It performs no explicit interphase registration. The external adapter is documented separately
because its resampling, crop construction, phase availability, segmentation, and missing-feature
handling differ from the internal workflow.

Create an untracked `configs/paths.yaml` from `configs/paths.example.yaml` only when a notebook
requires user-obtained datasets or private artifacts. Generated patient-linked files must remain
under the configured private roots and must not be committed.

| Order | Notebook | Classification |
|---:|---|---|
| 1 | [Internal cohort and splits](01_data_and_preprocessing/01_internal_cohort_and_splits.ipynb) | Public dataset plus configured private storage |
| 2 | [Historical independent-phase preprocessing](01_data_and_preprocessing/02_historical_independent_phase_preprocessing.ipynb) | Public dataset plus configured private storage |
| 3 | [W3 single-phase CNN](02_internal_models/03_single_phase_cnn.ipynb) | Historical workflow requiring private derived artifacts |
| 4 | [W4 multiphase CNN](02_internal_models/04_multiphase_cnn.ipynb) | Historical workflow requiring private derived artifacts |
| 5 | [W5 radiomics-LightGBM](02_internal_models/05_radiomics_lightgbm.ipynb) | Historical workflow requiring private derived artifacts |
| 6 | [Late fusion and internal evaluation](03_fusion_and_internal_results/06_late_fusion_internal_evaluation.ipynb) | Public aggregate reanalysis; private artifacts required for refitting |
| 7 | [External data acquisition](04_external_stress_test/07_external_data_acquisition.ipynb) | Public dataset acquisition into private storage |
| 8 | [External DICOM-to-NIfTI](04_external_stress_test/08_external_dicom_to_nifti.ipynb) | Public dataset plus configured private storage |
| 9 | [External tumor-mask preprocessing](04_external_stress_test/09_external_tumor_mask_preprocessing.ipynb) | Public dataset plus private SEG review |
| 10 | [External mask-density QC](04_external_stress_test/10_external_mask_density_qc.ipynb) | Historical workflow requiring private images and masks |
| 11 | [External liver-mask adapter](04_external_stress_test/11_external_liver_mask_adapter.ipynb) | Historical workflow requiring private images and masks |
| 12 | [External frozen inference](04_external_stress_test/12_external_frozen_inference.ipynb) | Public aggregate reanalysis; complete historical CNN inference unavailable |
| 13 | [Radiomics imputation controls](04_external_stress_test/13_radiomics_imputation_controls.ipynb) | Public aggregate reanalysis; private artifacts required for patient-level rerun |
| 14 | [Explainability and aggregate figures](05_figures_and_tables/14_explainability_and_aggregate_figures.ipynb) | Public aggregate figures; private artifacts required for case-level explanation |

## Scientific and reproducibility boundaries

- Patient identifiers, split assignments, images, masks, features, predictions, and model objects
  are intentionally excluded.
- W3 fold 1 and W4 fold 0 historical checkpoints were not retained.
- Source geometry and phase-specific historical crop coordinates needed for a complete four-phase
  retention audit were not retained.
- The public C2 crop-retention table applies only to C2.
- W5 is crop-restricted tumor radiomics, not guaranteed whole-lesion radiomics.
- The full-fusion model contains W4 probabilities, W5 probabilities, age, and sex; W3 is excluded.
- The external cohort contains 103 known-HCC cases and supports HCC-sensitivity stress testing,
  not multiclass external AUC or complete clinical validation.

For central limitations and artifact contracts, see
[reproducibility](../docs/reproducibility.md) and
[artifact contracts](../docs/artifact_contracts.md).
