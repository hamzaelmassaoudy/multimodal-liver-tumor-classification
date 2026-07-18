# External HCC-only transportability stress test

## Scope

The external analysis used 103 retained HCC-TACE-Seg patients, all known HCC. No patient had all
four phases required by the internal pipeline. This is an HCC-sensitivity stress test under a
changed adapter, not three-class external validation, and it yields no external multiclass AUC.

The external adapter differed in conversion, resampling, crop construction, phase availability,
segmentation inputs, feature availability, and missing-data handling. Degradation cannot be
assigned to one cause.

## Results and model-defined covariates

| Branch or scenario | Correct HCC predictions | HCC sensitivity |
|---|---:|---:|
| W3 frozen inference | 5/103 | 0.049 |
| W4 frozen inference | 0/103 | 0.000 |
| W5 baseline real-plus-imputed handling | 99/103 | 0.961 |
| Full fusion, missing sex with fold-local median | 83/103 | 0.806 |
| Full fusion, encoded sex=0 sensitivity | 2/103 | 0.019 |

External age and sex were unavailable. The corrected primary scenario passed both as missing and
used each internally fitted model’s training-fold median; all sex medians were 1. The sex-zero
scenario was evaluated separately. Predicted HCC/ICC/cHCC-CCA counts were 83/7/13 and 2/68/33,
respectively, and 82/103 hard labels differed. Neither scenario represents observed sex.

For the primary and frozen-pathway analyses, no external value or label entered fitting,
selection, recalibration, or tuning. Corrected clinical and fusion logistic regressions were
refitted on internal data only. W3, W4, W5, CNN, radiomics, and LightGBM components were not
retrained. Condition C is the separately disclosed label-free availability-subset diagnostic.

## Adapter quality control

C2 referenced-series fallback occurred in 102/103 patients. Corrected-primary HCC sensitivity was
82/102 in that group and 1/1 in the nonfallback group. The single nonfallback patient prevents a
meaningful comparison. Phase-coverage and fallback counts are in
[`external_adapter_qc.csv`](../results/aggregate/external_adapter_qc.csv).

## Radiomics feature-handling controls

| Condition | HCC sensitivity | Model status |
|---|---:|---|
| A: Real + imputed | 0.961 | Frozen baseline pathway |
| B: Median-only | 1.000 | Frozen sensitivity pathway |
| C: Strict overlap-only | 0.243 | Internal diagnostic refit |
| D1: Real-only, unavailable zeroed | 0.010 | Frozen sensitivity pathway |
| D2: Imputed-only, real zeroed | 0.971 | Frozen sensitivity pathway |

Condition C identified features available for all external patients without using labels, then
refitted classifiers on the internal development cohort using that availability subset and the
original fold structure. It is not frozen-model external validation. The controls show that
apparent external radiomics sensitivity depended strongly on internal-median substitution.

No verified external CNN-plus-radiomics artifact exists. Aggregate values are released in
[`external_stress_test.csv`](../results/aggregate/external_stress_test.csv) and
[`radiomics_imputation_controls.csv`](../results/aggregate/radiomics_imputation_controls.csv).
