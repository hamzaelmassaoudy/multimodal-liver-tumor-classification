# Model card

## Study system

The research system classifies three primary liver tumor categories on multiphase contrast-enhanced CT: HCC, ICC, and cHCC-CCA. It combines a multiphase CNN, crop-restricted radiomics-LightGBM probabilities, and age and sex through late fusion. W3 provides a single-phase comparator.

## Intended use

- Retrospective research on primary liver tumor classification.
- Aggregate analysis of the reported internal evaluation.
- Methodological inspection of lesion-centered multiphase modeling and transportability stress testing.

## Out-of-scope use

The system is not a medical device and is not intended for diagnosis, triage, treatment selection, prognosis, or autonomous clinical decision-making. The external cohort does not validate discrimination among all three tumor classes.

## Inputs and branches

- W3: C2-only `1 x 96 x 96 x 96` input to a randomly initialized MONAI 3D ResNet-18.
- W4: P/C1/C2/C3 `4 x 96 x 96 x 96` input to a randomly initialized MONAI 3D ResNet-18.
- W5: 428 candidate PyRadiomics features across four phases, with fold-specific feature selection and LightGBM.
- Full fusion: W4 and W5 three-class probability vectors, age, and sex, using fold-specific multinomial logistic regression.

Each W4 phase was independently centered on its own tumor-mask centroid. No explicit interphase registration was performed and voxelwise cross-channel anatomical correspondence was not guaranteed. W5 features characterize the tumor portion retained by each fixed crop.

## Evaluation data

The internal PLC-CECT V4 cohort contained 278 patients: 94 HCC, 99 ICC, and 85 cHCC-CCA. Development used 222 patients with five stratified folds; 56 patients formed an independent held-out evaluation cohort. The external stress test retained 103 known-HCC patients from HCC-TACE-Seg.

## Internal performance

Held-out macro one-versus-rest AUC was 0.630 for the clinical baseline, 0.860 for W3, 0.906 for W4, 0.938 for W5, 0.930 for CNN plus radiomics fusion, and 0.950 for full fusion. The full-fusion 95% CI was 0.896-0.988.

## External behavior

W3 and W4 HCC sensitivities were 0.049 and 0.000. Full-fusion HCC sensitivity was 0.019 under the historical missing-sex encoding of 0 and 0.806 under the deterministic locked fold-median sex=1 sensitivity analysis; 82/103 labels changed. The difference reveals instability to missing clinical-data handling, not validated improvement. External radiomics controls also showed strong dependence on imputation.

## Limitations and risks

- Independent phase centering does not guarantee anatomical correspondence across channels.
- Fixed `96 x 96 x 96` crops truncated some tumors; the verified C2 minimum retention was 15.64%.
- C2 retention findings cannot be generalized numerically to other phases from retained artifacts.
- Development CV and stacking estimates may be optimistic because outer validation folds informed checkpoint selection and development-wide labels informed class weights.
- Internal and external adapters differed materially, and no external case had all four required phases.
- Missing historical checkpoints prevent exact all-fold CNN inference reconstruction.
- Performance may differ across scanners, institutions, populations, acquisition protocols, and missing-data patterns.

Users must conduct independent validation, bias analysis, calibration assessment, and clinical governance before considering any translational application. See [scientific scope](scientific_scope.md), [external stress test](external_stress_test.md), and [reproducibility](reproducibility.md).
