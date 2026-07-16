# Aggregate results

This directory publishes privacy-safe cohort-level results. It contains no patient identifiers, rows, probabilities, labels, split membership, imaging, masks, or feature matrices.

## Released files

| File | Contents |
|---|---|
| [`aggregate/internal_performance.csv`](aggregate/internal_performance.csv) | Verified five-fold development CV and held-out internal macro-AUC summaries. |
| [`aggregate/delong_summary.csv`](aggregate/delong_summary.csv) | Nine exploratory per-class DeLong comparisons with Bonferroni and Benjamini-Hochberg adjustments. |
| [`aggregate/external_stress_test.csv`](aggregate/external_stress_test.csv) | HCC-only frozen-branch sensitivities and both full-fusion sex scenarios. |
| [`aggregate/radiomics_imputation_controls.csv`](aggregate/radiomics_imputation_controls.csv) | External radiomics pathway-control sensitivities. |
| [`aggregate/c2_crop_retention.csv`](aggregate/c2_crop_retention.csv) | C2-only crop-retention summary across 278 internal patients. |
| [`aggregate/reproducibility_status.json`](aggregate/reproducibility_status.json) | Supported analyses and retained-artifact limits. |

## Key interpretation constraints

- Held-out full-fusion macro-AUC was 0.950, with 95% CI 0.896-0.988.
- The smallest raw DeLong p-value was 0.0293 for full fusion versus W4 in cHCC-CCA; no comparison survived either nine-test adjustment.
- The external cohort contained only known HCC, so its reported values are sensitivities rather than multiclass AUCs.
- Historical full-fusion external sensitivity was 0.019 with missing sex encoded as 0. The locked fold-median sex=1 sensitivity analysis produced 0.806 and changed 82/103 labels.
- External radiomics results were strongly influenced by the imputation pathway.
- Crop-retention results apply only to C2 and show that a subset of lesions was truncated.

## Validation

From the repository root:

```bash
python scripts/validate_aggregate_results.py
python scripts/recalculate_delong_summary.py results/aggregate/delong_summary.csv
```

Metric recalculation from patient-level prediction tables requires authorized local artifacts and is intentionally separate from the public aggregate release. Detailed provenance is in [`docs/results_provenance.md`](../docs/results_provenance.md).
