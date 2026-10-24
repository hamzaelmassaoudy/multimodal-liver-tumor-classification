# Scientific scope

## Research questions

The revised study (v2.0.0) asks three questions:

1. How well do a 3D CNN, radiomics, and their late fusion distinguish HCC, ICC, and cHCC-CCA on
   PLC-CECT under robust internal evaluation, and do age and sex add value?
2. Does PLC-CECT contain class-dependent acquisition artifacts, and do the models use them?
3. Do the models transfer to another hospital, and which factors explain the external result?

## Design

- **Internal:** PLC-CECT V4, 278 patients (94 HCC, 99 ICC, 85 cHCC-CCA); 222 development patients
  in five stratified folds and 56 held-out patients never used for fitting (their results were known when the main CNN was chosen); five repeats
  of five-fold cross-validation (repeats 1–4 with the whole pipeline retrained).
- **Dataset audit:** a file-level census of all 1,112 scans and a counterfactual slice-resampling
  test with matched smoothing controls.
- **External validation:** MCT-LTDiag (103 HCC, 100 ICC) with observed age and sex; frozen models,
  no fitting, threshold tuning, or recalibration on external data; the only parameters estimated from
  external data were the ComBat feature adjustments of one mitigation analysis (unlabeled MCT-LTDiag features).
- **Stress test:** HCC-TACE-Seg (HCC only), traced through each pipeline correction.

Each analysis was planned in a dated analysis log before it was run; post hoc analyses are labelled
as such. The [revision overview](revision_2026-10.md) gives the results.

## Appropriate interpretation

- Internal discrimination is high (CNN + radiomics held-out macro-AUC 0.952), but it is partly
  inflated by dataset artifacts; no per-class advantage survived multiplicity adjustment.
- The CNN uses a non-contrast reconstruction artifact of the cHCC-CCA scans, and slice counts alone
  predict the class.
- Externally, the imaging models separated HCC from ICC barely better than chance, calibration
  failed, and no mitigation strategy changed this.
- cHCC-CCA could not be validated externally because no public external cohort contains it.

The results do not establish clinical readiness or transportability. Their value lies in showing
how internal metrics on a public dataset can mislead, and how a file-level audit and a direct
counterfactual test can reveal this.

## Submitted analysis (v1.1.0)

The submitted study evaluated full fusion as the primary model (held-out macro-AUC 0.945,
95% CI 0.890–0.984) and an HCC-only external stress test. Its scope, definitions, and results are
kept in [analysis alignment](manuscript_repository_alignment.md),
[external stress test](external_stress_test.md), and [results provenance](results_provenance.md).

See [preprocessing](preprocessing.md), [model card](model_card.md), and
[dataset audit](plc_cect_dataset_audit.md).
