# Aggregate results

This directory publishes privacy-safe cohort-level results. It contains no patient identifiers,
patient rows, probabilities, split membership, imaging, masks, or feature matrices.

## Released files

| File | Contents |
|---|---|
| [`aggregate/internal_performance.csv`](aggregate/internal_performance.csv) | Corrected six-model internal performance and the development-only size baseline. |
| [`aggregate/internal_sex_provenance.csv`](aggregate/internal_sex_provenance.csv) | Aggregate sex-token audit for all 278 internal patients. |
| [`aggregate/internal_sex_sensitivity.csv`](aggregate/internal_sex_sensitivity.csv) | Corrected-primary versus historical clinical/full-fusion summaries. |
| [`aggregate/internal_per_class.csv`](aggregate/internal_per_class.csv) | Corrected full-fusion class support, AUC, recall, and precision. |
| [`aggregate/internal_confusion_matrices.json`](aggregate/internal_confusion_matrices.json) | Corrected aggregate 3 × 3 confusion counts for six configurations. |
| [`aggregate/internal_paired_tests.csv`](aggregate/internal_paired_tests.csv) | Exploratory paired-fold t-test and exact Wilcoxon results. |
| [`aggregate/delong_summary.csv`](aggregate/delong_summary.csv) | Nine corrected per-class DeLong comparisons and exact-value adjustments. |
| [`aggregate/external_stress_test.csv`](aggregate/external_stress_test.csv) | HCC-only branch results and full-fusion missing-sex scenarios. |
| [`aggregate/external_adapter_qc.csv`](aggregate/external_adapter_qc.csv) | External phase-coverage and C2 fallback aggregate counts. |
| [`aggregate/radiomics_imputation_controls.csv`](aggregate/radiomics_imputation_controls.csv) | External radiomics feature-handling controls. |
| [`aggregate/c2_crop_retention.csv`](aggregate/c2_crop_retention.csv) | C2-only crop-retention summary across 278 internal patients. |
| [`aggregate/reproducibility_status.json`](aggregate/reproducibility_status.json) | Supported analyses and retained-artifact limits. |

## Key interpretation constraints

- Corrected full-fusion held-out macro-AUC was 0.945 (95% CI 0.890–0.984), with
  45/56 correct, accuracy 0.804, and macro-F1 0.805.
- Historical full-fusion AUC 0.950 is a provenance sensitivity result, not the primary value.
- The smallest raw DeLong p-value was 0.029347 for full fusion versus W4 in cHCC-CCA;
  no comparison survived either nine-test adjustment.
- The external cohort contained only known HCC, so reported values are sensitivities.
- Missing external sex with fold-local median imputation yielded 0.806; encoded sex=0 yielded
  0.019; 82/103 labels differed. Both are model-defined because external sex was unavailable.
- Condition C is an internal diagnostic refit using an externally defined availability subset.
- Crop-retention findings apply only to C2 and show that a subset of lesions was truncated.

## Validation

```bash
python scripts/validate_aggregate_results.py
python scripts/recalculate_delong_summary.py results/aggregate/delong_summary.csv
```

Metric recalculation from patient-level prediction tables requires authorized local artifacts and
is intentionally separate from the public aggregate release. Detailed provenance is in
[`docs/results_provenance.md`](../docs/results_provenance.md).
