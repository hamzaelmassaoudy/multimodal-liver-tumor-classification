# Model card

This card describes the models of the October 2026 revision (v2.0.0). The submitted models
(v1.1.0) are summarized at the end.

## System

The system classifies HCC, ICC, and cHCC-CCA on four-phase contrast-enhanced CT (non-contrast P,
arterial C1, portal-venous C2, delayed C3). Each phase is multiplied by its liver mask and cropped
to 96³ voxels around that phase's tumor.

| Component | Definition |
|---|---|
| Phase-dropout CNN (main) | Randomly initialized MONAI 3D ResNet-18, input `4 x 96 x 96 x 96`; random phases zeroed during training; checkpoint chosen on an inner validation split; per-fold class weights; five fold models |
| Radiomics | 372 intratumoral PyRadiomics features without shape features (107 per phase minus 56 shape features); per-fold variance and correlation filtering and top-30 ANOVA-F selection; LightGBM; five fold models |
| **CNN + radiomics (primary)** | Logistic late fusion of the six out-of-fold probabilities |
| Full fusion | CNN + radiomics plus age and sex (eight inputs) |

## Intended use

- Retrospective research on primary liver tumor classification.
- Methodological study of dataset artifacts and external transportability.

## Out-of-scope use

The models are not medical devices and must not be used for diagnosis, triage, treatment
selection, prognosis, or any clinical decision. They did not transport to an external hospital,
and the three-class task has no external validation.

## Training and evaluation data

PLC-CECT V4 (one hospital): 278 patients (94 HCC, 99 ICC, 85 cHCC-CCA), split into 222
development patients (five stratified folds) and 56 held-out patients. External validation:
MCT-LTDiag (103 HCC, 100 ICC). Stress test: HCC-TACE-Seg (89 HCC without mixed-scan inputs).

## Performance

| Model | PLC-CECT held-out macro-AUC (95% CI) | 5 × 5 repeated CV | MCT-LTDiag HCC-vs-ICC AUC (95% CI) |
|---|---:|---:|---:|
| Phase-dropout CNN | 0.919 (0.849–0.973) | 0.918 ± 0.018 | 0.528 (0.448–0.607) |
| Radiomics | 0.902 (0.826–0.960) | 0.918 ± 0.005 | 0.655 (0.579–0.731) |
| **CNN + radiomics** | **0.952 (0.906–0.985)** | **0.942 ± 0.011** | **0.578 (0.500–0.657)** |
| Full fusion | 0.951 (0.903–0.984) | 0.947 ± 0.011 | 0.690 (0.617–0.763); sex alone 0.663 |

Internally, CNN + radiomics had calibration slopes of 0.82–1.12. On MCT-LTDiag, calibration failed
for every model (intercepts −0.87 to −2.02), the models rarely predicted ICC, and many patients
were assigned to cHCC-CCA, a class absent from that cohort. Details are in the
[revision overview](revision_2026-10.md) and [external validation](external_validation_mct_ltdiag.md).

## Known failure modes and risks

- **Dataset shortcuts.** PLC-CECT acquisition differs by class. The CNN uses a non-contrast
  reconstruction artifact of the cHCC-CCA scans, and slice counts alone predict the class
  (held-out macro-AUC 0.853–0.872). Internal performance is therefore partly inflated by dataset
  artifacts ([dataset audit](plc_cect_dataset_audit.md)). Retraining with slice density equalized
  removed most of the slice-count signal but not the cue of thick reconstructions, and it did not
  improve external discrimination.
- **Masked tumor tissue.** In 52 of 99 ICC patients, less than 90% of the tumor lies inside the
  released liver mask, so part of the tumor is blanked in the model input. Retraining with the
  tumor preserved changed none of the conclusions (corrected-mask analysis).
- **Fixed crop.** The 96³ crop kept less than 90% of the portal-venous tumor in 37 of 94 HCC
  patients; an adaptive crop did not help.
- **Clinical inputs.** Age and sex added nothing internally; externally, full fusion's advantage
  came from sex (it disappeared within each sex), and on HCC-TACE-Seg its output depended strongly on how age and sex were supplied.
- **Missing phases.** Models need all four phases; phase dropout reduces but does not remove the
  dependence.
- **Small held-out set.** With 56 patients, confidence intervals are wide.

Clinical development would require multicenter data with all three tumor classes, acquisition
recorded and balanced by class, complete clinical variables, and prospective evaluation.

## Submitted models (v1.1.0)

The submitted system used the W4 multiphase CNN (outer-fold checkpoint selection), W5 radiomics
with shape features, and full fusion as the primary model (held-out macro-AUC 0.945, 95% CI
0.890–0.984). Its definitions and results are kept in [model architecture](model_architecture.md),
[results provenance](results_provenance.md), and [`results/aggregate`](../results/aggregate/).
