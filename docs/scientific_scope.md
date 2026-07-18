# Scientific scope

## Research question

The study evaluates multimodal classification of HCC, ICC, and cHCC-CCA on multiphase CT and
then subjects the system to an HCC-only external transportability stress test.

## Internal design

PLC-CECT V4 contributed 278 patients: 94 HCC, 99 ICC, and 85 cHCC-CCA. A patient-level
split assigned 222 patients to development and 56 to independent evaluation. Development used
five stratified folds. Sex provenance was 185 male, 90 female, and three unresolved entries.

The corrected primary analysis retained unresolved sex as missing and used training-fold median
imputation. Evaluated configurations were the clinical baseline, W3, W4, W5, CNN-plus-radiomics,
exact eight-feature full fusion, and a development-only tumor-size baseline.

Corrected full fusion achieved CV macro-AUC `0.955 ± 0.033` and held-out macro-AUC 0.945
(95% CI 0.890–0.984). Historical full-fusion AUC 0.950 is a sensitivity result.

## External scope

HCC-TACE-Seg supplied 103 known-HCC patients. This supports HCC sensitivity under changed
acquisition and adapter conditions, not multiclass external validation. Missing external sex with
fold-local median yielded 0.806 and encoded sex=0 yielded 0.019; both are model-defined.

## Appropriate interpretation

The internal results support proof-of-concept discrimination within the evaluated cohorts. No
multiplicity-adjusted DeLong advantage was established. External findings demonstrate sensitivity
to domain shift, phase availability, adapter differences, feature overlap, and unavailable clinical
variables. They do not establish clinical readiness or robust transportability.

See [preprocessing](preprocessing.md), [fusion definition](fusion_definition.md),
[external stress test](external_stress_test.md), and [model card](model_card.md).
