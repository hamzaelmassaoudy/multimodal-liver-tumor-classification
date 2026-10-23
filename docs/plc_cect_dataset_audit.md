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
| The difference is slice spacing, not scan range | Liver slices per liver width (portal venous): HCC 0.31, ICC 0.70, cHCC-CCA 0.44, while the share of slices containing liver is similar (0.94–0.98); the curators had already kept only the slices containing liver |
| cHCC-CCA non-contrast scans have far fewer slices | Median non-contrast / portal-venous slice ratio: cHCC-CCA 0.29, HCC 0.95, ICC 0.99, consistent with a much thicker reconstruction |
| Storage format follows the class | Three-channel files in 87 of 99 ICC patients, 3 of 85 cHCC-CCA patients, and no HCC patient |
| Some liver masks are empty | 13 scans of 4 ICC patients have an empty liver mask, so their liver-masked crops are black |
| Tumors extend beyond the liver mask (post hoc) | Tumors lie less than 90% inside the released liver mask in 52 of 99 ICC, 29 of 94 HCC, and 21 of 85 cHCC-CCA patients (portal venous) |

The slice-spacing reading follows a rule fixed before the census: class medians of the
liver-slices-per-width ratio differing more than 1.5-fold, with a similar share of slices containing
liver, indicate different slice spacing. It is an anatomical estimate, not a measurement. The source publication states that only the slices
containing liver were kept, so the scan range was already restricted to the liver, which supports this reading. The
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

- **Non-contrast artifact.** Both directions met every criterion, each judged against its own matched
  smoothing control (0.04 and 0.02). The CNN responds strongly to this non-contrast reconstruction
  artifact of the cHCC-CCA scans. The response replicated after retraining with the tumor preserved
  (+0.25 and −0.42; controls 0.03 and 0.01), for injection after equalized retraining (+0.087), and
  with a thick reconstruction simulated by averaging adjacent slices (+0.281, blur-only control 0.040;
  notebook 31).
- **Slice density.** The shifts were five to eight times larger than the smoothing controls, but the
  controls moved the score by 0.12, above the pre-set limit, so reliance on slice density is not
  claimed.
- **Radiomics.** Slice-density shifts were barely larger than the controls, and the artifact test was
  positive in one direction only, so no reliance is claimed.
- **CNN + radiomics.** Same pattern as the CNN with smaller artifact effects (+0.19 and −0.41).
- **Two readings of the rule.** The plan did not say whether the smoothing-control limit applies per
  condition or to all conditions of a model together. The implementation notes, written before the run,
  compared each condition with its own matched control (the reading above); the notebook's verdict, also
  written before the run, applied the limit to all four conditions of a model at once and returned "not
  interpretable" for every model, because the slice-density controls exceeded 0.05. The manuscript
  reports both readings (Supplementary Table S6). The test shows that the CNN responds to the artifact;
  it does not measure how much of the internal AUC depends on it.

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

Preserving the tumor changed none of the conclusions. Retrained on crops masked by the union of the
liver and tumor masks (notebook 28), CNN + radiomics reached a held-out macro-AUC of 0.963 (main
pipeline 0.952), the CNN still met every criterion of the non-contrast artifact test, and MCT-LTDiag
performance was unchanged (0.571 vs. 0.578). Radiomics improved where tissue had been removed
([`corrected_mask_by_tumor_inside_liver.csv`](../results/revision_2026-10/corrected_mask_by_tumor_inside_liver.csv)).

Equalizing slice density is not enough. Retrained after every scan was resampled to one anatomical
slice density (notebook 29), the models kept their held-out performance (CNN + radiomics 0.934 vs.
0.952) although slice counts alone lost most of their signal (held-out macro-AUC 0.853 to 0.678). A
non-contrast series made thick before equalization still raised the CNN's cHCC-CCA probability
(+0.087), and external discrimination did not improve (MCT-LTDiag 0.510 vs. 0.578): resampling
equalizes the number of slices, not the blur of a thick reconstruction
([`equalized_density_residual_artifact.csv`](../results/revision_2026-10/equalized_density_residual_artifact.csv)).

## Acquisition-matched tests

Giving every internal scan the slice spacing of MCT-LTDiag (5 mm slices) by averaging adjacent slices
(notebook 31) lowered the held-out HCC-versus-ICC AUC of the frozen CNN + radiomics from 0.947 to
0.795, and only 15 of 99 ICC patients were still called ICC, the class pattern seen on MCT-LTDiag; a
blur-only control changed little (0.932). Retraining every model at that spacing (notebook 32) kept
CNN + radiomics at 0.929 internally but did not restore external discrimination (MCT-LTDiag 0.627, not
better than the main model, p = 0.30). Acquisition therefore explains part of the external failure,
not most of it ([revision overview](revision_2026-10.md#acquisition-matched-tests)).

## Recommendations for PLC-CECT users

1. Do not interpret internal accuracy on PLC-CECT as evidence of tumor-specific learning without an
   acquisition check such as the counterfactual test above.
2. Report slice counts by class and test a slice-count-only baseline.
3. Avoid the non-contrast phase. Resampling the scans to one slice density did not remove the
   acquisition cue, and retraining at the external slice spacing did not restore external
   discrimination, so prefer data with acquisition balanced across classes.
4. Check tumor coverage before masking the CT with the released liver mask; masking with the union
   of the liver and tumor masks keeps the tumor tissue.
5. Validate on a cohort with recorded and balanced acquisition, such as MCT-LTDiag for HCC versus ICC.
