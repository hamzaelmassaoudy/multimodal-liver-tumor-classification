# Results provenance

## Public aggregate artifacts

Files under [`results/aggregate`](../results/aggregate/) contain cohort-level values only. They
were transcribed from or deterministically recalculated against verified retained outputs. They
contain no patient identifiers, probability rows, labels, or split membership.

| Artifact | Provenance and interpretation |
|---|---|
| [`internal_performance.csv`](../results/aggregate/internal_performance.csv) | Corrected six-model CV and 56-patient held-out summaries. |
| [`internal_sex_provenance.csv`](../results/aggregate/internal_sex_provenance.csv) | Aggregate audit of 185 male, 90 female, and 3 unresolved entries. |
| [`internal_sex_sensitivity.csv`](../results/aggregate/internal_sex_sensitivity.csv) | Corrected-primary and historical clinical/full-fusion comparisons. |
| [`internal_per_class.csv`](../results/aggregate/internal_per_class.csv) | Corrected full-fusion class-level metrics. |
| [`internal_confusion_matrices.json`](../results/aggregate/internal_confusion_matrices.json) | Aggregate confusion counts for all six configurations. |
| [`internal_paired_tests.csv`](../results/aggregate/internal_paired_tests.csv) | Five paired-fold t-test and exact Wilcoxon comparisons. |
| [`delong_summary.csv`](../results/aggregate/delong_summary.csv) | Nine corrected DeLong tests and exact-p multiplicity adjustments. |
| [`external_stress_test.csv`](../results/aggregate/external_stress_test.csv) | HCC-only branch and missing-covariate scenario summaries. |
| [`external_adapter_qc.csv`](../results/aggregate/external_adapter_qc.csv) | Aggregate phase-coverage and C2 fallback findings. |
| [`radiomics_imputation_controls.csv`](../results/aggregate/radiomics_imputation_controls.csv) | External feature-handling controls with Condition C identified as an internal refit. |
| [`c2_crop_retention.csv`](../results/aggregate/c2_crop_retention.csv) | Original-versus-retained C2 tumor voxel-count summary. |

## Corrected internal performance

| Model | CV macro-AUC | Held-out macro-AUC |
|---|---:|---:|
| Clinical baseline | 0.649 ± 0.073 | 0.614 |
| W3 single-phase CNN | 0.912 ± 0.048 | 0.860 |
| W4 multiphase CNN | 0.951 ± 0.040 | 0.906 |
| W5 radiomics-LightGBM | 0.922 ± 0.044 | 0.938 |
| CNN plus radiomics fusion | 0.955 ± 0.034 | 0.930 |
| Full fusion | 0.955 ± 0.033 | 0.945 |
| Tumor-size-only baseline | 0.633 ± 0.080 | Not evaluated |

Full fusion classified 45/56 correctly. Its held-out CI was 0.890–0.984. Historical
non-male-to-zero full-fusion AUC 0.950 is retained only in the sensitivity artifact.

## Statistical provenance

Corrected DeLong values were computed from aligned authentic 56-patient prediction artifacts after
the approved missing-sex correction. Adjustments used the exact corrected p-value family, not
four-decimal display values. No comparison remained significant after either adjustment.

The five paired-fold t-test and exact Wilcoxon values are aggregate outputs from the corrected
internal refit. Their small sample size makes them exploratory.

## Reanalysis levels

- Released aggregate tables support schema and statistical consistency checks.
- Metric recalculation from prediction rows requires authorized local patient-level artifacts.
- The C2 audit and external scenario aggregation require authorized local inputs and emit only
  aggregate summaries.
- Exact all-fold CNN inference is unavailable because two historical checkpoints were not retained.

See [artifact contracts](artifact_contracts.md), [reproducibility](reproducibility.md), and
[`results/README.md`](../results/README.md).
