# Artifact contracts

These contracts protect the scientific definitions used by the released utilities. Patient-level artifacts described here are local inputs and are not part of the public repository.

## Immutable conventions

| Convention | Value |
|---|---|
| Class order | HCC, ICC, cHCC-CCA |
| Encoded labels | 0, 1, 2 in class order |
| Phase order | P, C1, C2, C3 |
| Crop shape | `96 x 96 x 96` |
| W3 phase | C2 |
| Full-fusion width | 8 |

`CHCC` is accepted only as a compatibility token for the displayed class cHCC-CCA.

## Preprocessed arrays

For an authorized local patient artifact, CT, tumor-mask, and liver-mask arrays have leading phase order P, C1, C2, C3 and spatial size `96 x 96 x 96`. The historical constructor returns CT, tumor mask, liver mask, and four phase-specific centers. It does not promise cross-phase source-grid equality.

## Prediction tables

The metric reanalysis utility requires an integer `label` column and three finite probability columns ordered HCC, ICC, cHCC-CCA. Its compatibility defaults are `prob_HCC`, `prob_ICC`, and `prob_CHCC`. Every probability must be within `[0, 1]`, and each row must sum to one within numerical tolerance. Prediction tables remain private because rows correspond to patients.

## Fusion matrices

The first three columns are W4 probabilities in class order, the next three are W5 probabilities in class order, followed by age and sex. W3 is not permitted in the full-fusion constructor. See [fusion definition](fusion_definition.md).

## C2 retention inputs

The local retention audit aligns a private metadata table containing unique `patient_id` and original C2 `tumor_vol` with a private radiomics table containing unique `patient_id` and cropped `C2_original_shape_VoxelVolume`. Membership must match one-to-one. The only publishable output is the aggregate summary; aligned patient rows must remain private.

## External sex-scenario inputs

The scenario utility consumes two aligned private integer prediction vectors: historical sex=0 and deterministic locked-median sex=1. It returns cohort size, HCC counts and sensitivities, and the number of changed labels. It does not expose case-level changes.

## Released aggregate schemas

- `internal_performance.csv`: model, CV macro-AUC mean and SD, held-out macro-AUC, optional held-out CI, scope.
- `delong_summary.csv`: class, comparison, comparator AUCs, difference, raw two-sided p-value, nine-test Bonferroni and Benjamini-Hochberg adjusted p-values, interpretation.
- `external_stress_test.csv`: branch, scenario, cases, HCC-correct count, sensitivity, interpretation.
- `radiomics_imputation_controls.csv`: condition, HCC sensitivity, interpretation.
- `c2_crop_retention.csv`: aggregate metric, optional count and denominator, percentage, C2-only scope.
- `reproducibility_status.json`: supported reanalyses and explicit reconstruction limits.

Run `python scripts/validate_aggregate_results.py` from the repository root to validate required public schemas.
