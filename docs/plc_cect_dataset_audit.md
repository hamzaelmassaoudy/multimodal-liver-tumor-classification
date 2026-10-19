# PLC-CECT dataset audit

PLC-CECT V4 is, to our knowledge, the only public multiphase CT dataset that includes cHCC-CCA, which
makes it attractive for training. This audit shows that its acquisition is confounded with class. Anyone using
it should check whether a model has learned the class from the acquisition rather than the tumor.

The audit read all 1,112 scans (278 patients × 4 phases) directly from the released NIfTI files
(notebook 26). Class-level tables are in
[`results/revision_2026-10`](../results/revision_2026-10/README.md); the per-scan census stays
private.

## Findings

| Finding | Evidence |
|---|---|
| Patient numbers follow the class | Numbers were assigned in class blocks: all HCC first, then ICC, then cHCC-CCA |
| Spacing is not recorded | Every file is stored as 8-bit integers (0–255) with a nominal 1 mm spacing, so physical slice thickness and voxel size cannot be read from the files |
| Slice counts differ by class | Median portal-venous slices: HCC 93, ICC 195, cHCC-CCA 126; counts differ by class in every phase |
| The difference is slice thickness, not scan range | Liver slices per liver width (portal venous): HCC 0.31, ICC 0.70, cHCC-CCA 0.44, while the share of slices containing liver is similar (0.94–0.98) |
| cHCC-CCA non-contrast scans are thick | Median non-contrast / portal-venous slice ratio: cHCC-CCA 0.29, HCC 0.95, ICC 0.99 |
| Storage format follows the class | Three-channel files in 87 of 99 ICC patients, 3 of 85 cHCC-CCA patients, and no HCC patient |
| Some liver masks are empty | 13 scans of 4 ICC patients have an empty liver mask, so their liver-masked crops are black |
| Tumors extend beyond the liver mask (post hoc) | Tumors lie less than 90% inside the released liver mask in 52 of 99 ICC, 29 of 94 HCC, and 21 of 85 cHCC-CCA patients (portal venous) |

The slice-thickness reading follows a rule fixed before the census: class medians of the
liver-slices-per-width ratio differing more than 1.5-fold, with a similar share of slices containing
liver, indicate different slice thickness. It is an anatomical estimate, not a measurement. The
external cohort MCT-LTDiag has 5 mm slices in every scan of both classes.

Slice counts alone predict the class: a logistic model on slice counts alone reached a held-out
macro-AUC of 0.853 (random forest 0.872), and 0.922 for HCC versus ICC out of fold
([`acquisition_only_discrimination.csv`](../results/revision_2026-10/acquisition_only_discrimination.csv)).
Where slice counts are ambiguous (n = 76), CNN + radiomics still separated HCC from ICC with an AUC of
0.954, so the models are not using slice counts alone.

## Counterfactual test

Each internal scan's number of slices was changed by linear resampling along the slice axis, the
crops were rebuilt exactly as in training, and the frozen models predicted again. Each condition had
a matched smoothing control (resampled down and back to the original count), which separates
geometry from interpolation blur. Reliance was claimed only if both directions moved toward the
simulated class with CIs excluding zero and mean shifts of at least 0.05, and the smoothing control
moved the score by less than 0.05.

| Condition (CNN, all 278 patients) | Shift vs smoothing control (95% CI) | Predicted class change |
|---|---:|---|
| Non-contrast artifact injected into HCC and ICC scans, Δ p(cHCC-CCA) | +0.25 (0.21–0.30) | Predicted cHCC-CCA: 8 → 68 of 193 |
| Non-contrast artifact repaired in cHCC-CCA scans, Δ p(cHCC-CCA) | −0.50 (−0.58 to −0.42) | Predicted cHCC-CCA: 68 → 12 of 85 |
| HCC scans made ICC-like, Δ [p(ICC) − p(HCC)] | +0.92 (0.81–1.03) | Predicted ICC: 9 → 65 of 94 |
| ICC scans made HCC-like, Δ [p(ICC) − p(HCC)] | −0.57 (−0.66 to −0.49) | Predicted HCC: 14 → 31 of 99 |

- **Non-contrast artifact.** Both directions met every criterion (smoothing controls 0.04 and 0.02).
  The CNN uses the thick cHCC-CCA non-contrast reconstruction.
- **Slice density.** The shifts were five to eight times larger than the smoothing controls, but the
  controls moved the score by 0.12, above the pre-set limit. This is strong evidence, not a
  conclusive test.
- **Radiomics.** Slice-density shifts were barely larger than the controls, and the artifact test was
  positive in one direction only, so no reliance is claimed.
- **CNN + radiomics.** Same pattern as the CNN with smaller artifact effects (+0.19 and −0.41).

All conditions and models are in
[`counterfactual_effects.csv`](../results/revision_2026-10/counterfactual_effects.csv) and
[`counterfactual_predicted_classes.csv`](../results/revision_2026-10/counterfactual_predicted_classes.csv).

## Tumor inside the liver mask (post hoc)

The internal preprocessing multiplies each phase by its liver mask, so tumor voxels outside the mask
become zero. The census measured the share of each tumor mask inside the released liver mask
([`tumor_inside_liver_mask_by_class_phase.csv`](../results/revision_2026-10/tumor_inside_liver_mask_by_class_phase.csv)).
Median portal-venous shares were 0.96 (HCC), 0.88 (ICC), and 0.97 (cHCC-CCA); 11 ICC tumors lay
entirely outside. Out-of-fold CNN + radiomics macro-AUC was 0.967 when at least 90% of the tumor was
inside and 0.924 otherwise
([`performance_by_tumor_inside_liver_mask.csv`](../results/revision_2026-10/performance_by_tumor_inside_liver_mask.csv)).
The scripts
[`census_tumor_inside_liver_mask.py`](../scripts/revision/census_tumor_inside_liver_mask.py) and
[`summarize_tumor_inside_liver_mask.py`](../scripts/revision/summarize_tumor_inside_liver_mask.py)
reproduce the census and the summary from the downloaded dataset.

## Recommendations for PLC-CECT users

1. Do not interpret internal accuracy on PLC-CECT as evidence of tumor-specific learning without an
   acquisition check such as the counterfactual test above.
2. Report slice counts by class and test a slice-count-only baseline.
3. Avoid the non-contrast phase or harmonize slice thickness before training.
4. Check tumor coverage before masking the CT with the released liver mask.
5. Validate on a cohort with recorded and balanced acquisition, such as MCT-LTDiag for HCC versus ICC.
