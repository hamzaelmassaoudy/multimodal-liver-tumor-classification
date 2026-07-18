# Artifact contracts

These contracts protect the scientific definitions used by released utilities. Patient-level
artifacts described here are local inputs and are not public repository contents.

## Immutable conventions

| Convention | Value |
|---|---|
| Class order | HCC, ICC, cHCC-CCA |
| Encoded labels | 0, 1, 2 in class order |
| Phase order | P, C1, C2, C3 |
| Crop shape | `96 x 96 x 96` |
| W3 phase | C2 |
| Full-fusion width | 8 |

## Preprocessed arrays

Authorized patient artifacts use leading phase order P, C1, C2, C3 and spatial shape
`96 x 96 x 96`. The internal constructor returns CT, tumor-mask, liver-mask, and four
phase-specific centers. It does not promise cross-phase grid equality or retained source geometry.

## Prediction and fusion tables

The metric utility requires integer labels and three finite probability columns ordered HCC, ICC,
cHCC-CCA. Rows must sum to one. Prediction tables remain private.

Fusion columns are W4 HCC/ICC/cHCC-CCA probabilities, W5 probabilities in the same order, age,
and sex. W3 is not accepted. Unresolved internal sex must remain missing for corrected-primary
fitting; historical non-male-to-zero encoding is a separate sensitivity path.

## C2 retention inputs

The local audit aligns private metadata and radiomics tables one-to-one by patient. The only
publishable output is the aggregate summary; aligned rows remain private.

## External scenario inputs

The scenario utility consumes aligned private integer predictions for corrected missing-sex
fold-median and encoded-sex-zero conditions. It returns counts, sensitivities, and changed-label
count without exposing case-level changes.

## Released aggregate schemas

- `internal_performance.csv`: corrected model performance, held-out CIs, classification metrics.
- `internal_sex_provenance.csv`: aggregate sex-token counts and partition location of unresolved entries.
- `internal_sex_sensitivity.csv`: corrected-primary versus historical aggregate performance.
- `internal_per_class.csv`: corrected class support, AUC, correct count, recall, and precision.
- `internal_confusion_matrices.json`: aggregate confusion counts and class order.
- `internal_paired_tests.csv`: paired-fold t-test and exact Wilcoxon outputs.
- `delong_summary.csv`: corrected AUCs, z statistics, exact raw and adjusted p-values.
- `external_stress_test.csv`: branch and model-defined HCC sensitivities.
- `external_adapter_qc.csv`: aggregate phase coverage and C2 fallback findings.
- `radiomics_imputation_controls.csv`: feature-handling conditions and model status.
- `c2_crop_retention.csv`: C2-only crop-retention summary.
- `reproducibility_status.json`: supported analyses and reconstruction limits.

Run `python scripts/validate_aggregate_results.py` to validate public schemas.
