# Results provenance

## Public aggregate artifacts

All files under [`results/aggregate`](../results/aggregate/) contain cohort-level values only. They were transcribed from, or deterministically recalculated against, verified retained scientific artifacts. They contain no patient identifiers, probabilities, labels, or split membership.

| Artifact | Provenance and interpretation |
|---|---|
| [`internal_performance.csv`](../results/aggregate/internal_performance.csv) | Verified five-fold development CV and held-out 56-patient evaluation summaries. The full-fusion held-out CI is included. |
| [`delong_summary.csv`](../results/aggregate/delong_summary.csv) | Nine exploratory per-class DeLong comparisons and deterministic nine-test multiplicity adjustments. |
| [`external_stress_test.csv`](../results/aggregate/external_stress_test.csv) | Aggregate HCC counts and sensitivities for frozen W3/W4 inference and the two full-fusion missing-sex scenarios. |
| [`radiomics_imputation_controls.csv`](../results/aggregate/radiomics_imputation_controls.csv) | Verified external radiomics pathway controls. |
| [`c2_crop_retention.csv`](../results/aggregate/c2_crop_retention.csv) | Aggregate comparison of original and crop-retained C2 tumor voxel counts across 278 internal patients. |
| [`reproducibility_status.json`](../results/aggregate/reproducibility_status.json) | Machine-readable statement of supported analyses and unavailable reconstruction inputs. |

## Internal performance

| Model | CV macro-AUC | Held-out macro-AUC |
|---|---:|---:|
| Clinical baseline | 0.650 +/- 0.073 | 0.630 |
| W3 single-phase CNN | 0.912 +/- 0.048 | 0.860 |
| W4 multiphase CNN | 0.951 +/- 0.040 | 0.906 |
| W5 radiomics-LightGBM | 0.922 +/- 0.044 | 0.938 |
| CNN plus radiomics fusion | 0.955 +/- 0.034 | 0.930 |
| Full fusion | 0.955 +/- 0.033 | 0.950 |
| Tumor-size-only baseline | 0.633 +/- 0.080 | Not evaluated |

The full-fusion held-out 95% confidence interval was 0.896-0.988. CV checkpoint selection and class-weight decisions can make development estimates optimistic; the independent held-out result is emphasized.

## DeLong interpretation

Nine raw two-sided per-class comparisons were exploratory. The smallest raw p-value was 0.0293 for full fusion versus W4 multiphase CNN in cHCC-CCA. Full fusion versus W5 radiomics in cHCC-CCA had p=0.3457. Bonferroni and Benjamini-Hochberg values were calculated across the nine reported four-decimal raw p-values, matching the finalized reporting table. No comparison remained significant after either adjustment.

The aggregate multiplicity calculations can be checked with:

```bash
python scripts/recalculate_delong_summary.py results/aggregate/delong_summary.csv
```

## Reanalysis levels

- Released aggregate tables support schema and statistical consistency checks.
- Metric recalculation from prediction rows requires authorized local patient-level artifacts supplied by the user.
- The C2 retention audit requires authorized local metadata and radiomics artifacts; it emits aggregate values only.
- Exact all-fold CNN inference is unavailable because two historical checkpoints were not retained.

See [artifact contracts](artifact_contracts.md), [reproducibility](reproducibility.md), and [`results/README.md`](../results/README.md).
