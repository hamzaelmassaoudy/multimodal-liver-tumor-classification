# Model card

## Study system

The system classifies HCC, ICC, and cHCC-CCA on multiphase contrast-enhanced CT. It combines
multiphase CNN probabilities, crop-restricted radiomics-LightGBM probabilities, age, and sex
through late fusion. W3 is a single-phase comparator.

## Intended use

- Retrospective research on primary liver tumor classification.
- Aggregate analysis of the reported internal evaluation.
- Methodological inspection of lesion-centered multiphase modeling and transportability stress.

## Out-of-scope use

The system is not a medical device and is not intended for diagnosis, triage, treatment selection,
prognosis, or autonomous clinical decision-making. The external cohort does not validate
discrimination among all three tumor classes.

## Inputs and branches

- W3: C2-only `1 x 96 x 96 x 96` input to a randomly initialized MONAI 3D ResNet-18.
- W4: P/C1/C2/C3 `4 x 96 x 96 x 96` input to a randomly initialized MONAI 3D ResNet-18.
- W5: 428 candidate crop-restricted PyRadiomics features and fold-specific LightGBM.
- Full fusion: W4 and W5 probability triplets, age, and sex, using multinomial logistic regression.

Each W4 phase was independently centered on its own tumor-mask centroid. No explicit interphase
registration was performed. Cached W5 arrays lacked source spacing and geometry; shape outputs
are not verified physical-unit measurements.

## Evaluation data

PLC-CECT V4 contributed 278 patients: 94 HCC, 99 ICC, and 85 cHCC-CCA. Development used
222 patients in five folds; 56 patients formed an independent evaluation cohort. Sex provenance
was 185 male, 90 female, and 3 unresolved. HCC-TACE-Seg supplied 103 known-HCC patients.

## Corrected internal performance

Unresolved sex was treated as missing with fold-local median imputation. Held-out macro-AUCs were
0.614 for the clinical baseline, 0.860 for W3, 0.906 for W4, 0.938 for W5, 0.930 for
CNN-plus-radiomics, and 0.945 for full fusion. The full-fusion CI was 0.890–0.984; accuracy
was 0.804 and macro-F1 was 0.805. Historical full-fusion AUC 0.950 is a sensitivity result.

## External behavior

W3 and W4 HCC sensitivities were 0.049 and 0.000. Missing external sex with fold-local median
imputation yielded full-fusion sensitivity 0.806, whereas encoded sex=0 yielded 0.019; 82/103
labels changed. Both are model-defined because external sex was unavailable. C2 fallback was used
for 102/103 patients. Radiomics controls showed strong dependence on imputation; Condition C was
an internal diagnostic refit rather than frozen external validation.

## Limitations and risks

- Independent phase centering does not guarantee anatomical correspondence across channels.
- Fixed crops truncated some tumors; verified C2 minimum retention was 15.64%.
- C2 retention values cannot be generalized numerically to other phases.
- Historical radiomics shape outputs use crop-grid/unit-spacing geometry.
- CV and stacking estimates may be optimistic because of checkpoint and class-weight decisions.
- Internal and external adapters differed materially, and no external patient had all four phases.
- Missing checkpoints prevent exact all-fold CNN inference reconstruction.
- External age and sex were unavailable and the external cohort contained only HCC.

Independent validation, bias analysis, calibration assessment, and clinical governance are
required before any translational use. See [scientific scope](scientific_scope.md),
[external stress test](external_stress_test.md), and [reproducibility](reproducibility.md).
