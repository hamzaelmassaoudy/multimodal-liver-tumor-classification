# Aggregate figures

The three PNG files in this directory are generated only from privacy-safe tables in
[`results/aggregate`](../aggregate/):

- `internal_performance.png` compares corrected cross-validation and held-out macro-AUC.
- `external_stress_test.png` distinguishes W3, W4, W5 baseline, corrected missing-sex primary,
  and encoded-sex-zero sensitivity results.
- `c2_crop_retention.png` summarizes verified C2 fixed-crop truncation thresholds.

Regenerate them from the repository root with:

```bash
python scripts/generate_aggregate_figures.py
```

They contain no images, masks, identifiers, or patient-level values.
