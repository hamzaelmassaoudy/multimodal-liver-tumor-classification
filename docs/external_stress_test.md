# External HCC-only transportability stress test

## Scope

The external analysis used 103 retained patients from HCC-TACE-Seg, all with known HCC. No patient had all four phases required by the internal pipeline. The analysis therefore measures HCC sensitivity under a changed data and preprocessing pathway; it is not three-class external validation and does not yield an external multiclass AUC.

The external adapter differed from the internal workflow in source conversion, resampling, crop construction, phase availability, segmentation inputs, feature availability, and missing-phase handling. Degradation cannot be assigned to a single cause.

## Frozen branch results

| Branch or scenario | Correct HCC predictions | HCC sensitivity |
|---|---:|---:|
| W3 historical frozen inference | 5/103 | 0.049 |
| W4 historical frozen inference | 0/103 | 0.000 |
| Full fusion, historical external adapter, sex=0 | 2/103 | 0.019 |
| Full fusion, locked fold-median sex sensitivity analysis, sex=1 | 83/103 | 0.806 |

External age was missing and replaced by each locked fold-specific age median. External sex was unavailable. Historical code encoded missing sex as 0. The locked development-fold median was 1 in all folds, so the deterministic sensitivity analysis replaced 0 with 1 without fitting, retraining, recalibration, or using external labels to select a parameter.

The sex scenarios changed 82 of 103 predicted labels. The 0.806 value is not the historically implemented result, and sex=1 is not asserted to be the observed sex of every external patient. The large swing demonstrates that the full-fusion output was highly unstable under the missing-sex assumption and cannot establish robust external transportability.

## Radiomics imputation controls

| Condition | HCC sensitivity |
|---|---:|
| Real + imputed | 0.961 |
| Median-only | 1.000 |
| Strict overlap-only | 0.243 |
| Real-only with missing zero | 0.010 |
| Imputed-only with real zero | 0.971 |

The high median-only and imputed-only sensitivities, together with the much lower strict-overlap result, show that apparent external radiomics performance depended strongly on the imputation pathway. The real-plus-imputed value alone is not evidence of robust external radiomic signal.

No verified external CNN-plus-radiomics artifact exists, so this repository reports no result for that branch. Aggregate values are released in [`external_stress_test.csv`](../results/aggregate/external_stress_test.csv) and [`radiomics_imputation_controls.csv`](../results/aggregate/radiomics_imputation_controls.csv).
