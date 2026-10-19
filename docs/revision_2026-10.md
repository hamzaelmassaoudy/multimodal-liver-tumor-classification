# October 2026 revision

Version 2.0.0 adds the analyses run during peer review of the manuscript (17–19 October 2026).
Each analysis was planned in a dated analysis log before it was run; analyses decided after seeing
data are labelled *post hoc*. All values below are in
[`results/revision_2026-10`](../results/revision_2026-10/README.md), and every notebook is listed in
the [revision notebook guide](revision_notebooks.md).

## What changed from v1.1.0

| Component | v1.1.0 (as submitted) | v2.0.0 (revision) |
|---|---|---|
| Main CNN | W4 four-phase 3D ResNet-18; checkpoint chosen on the outer validation fold; class weights from all 222 development patients | Same architecture trained with **phase dropout**, an inner validation split for checkpoint choice, and per-fold class weights |
| Radiomics | 428 candidate features including shape | **Shape features removed** (372 kept), because the released files carry no physical voxel spacing |
| Primary model | Full fusion (CNN + radiomics + age + sex) | **CNN + radiomics**; age and sex added nothing internally and only sex separated the external classes |
| Internal statistics | One held-out set; per-class DeLong tests | Adds 5 × 5 repeated cross-validation, Harrell optimism correction, Benjamini–Hochberg adjustment across 18 DeLong tests, and calibration |
| External evaluation | HCC-TACE-Seg (HCC only, sensitivity) | **MCT-LTDiag** (103 HCC, 100 ICC; observed age and sex) as the external validation; HCC-TACE-Seg repaired and kept as a stress test |
| New analyses | — | Missing-phase tests, crop truncation and size strata, adaptive crop, dataset audit, counterfactual test, tumor-inside-liver-mask census (post hoc), quantitative Grad-CAM |

The main CNN was chosen on 17 October 2026, after the internal held-out results of all CNN variants
were known and before any external evaluation of the new models. The original CNN is reported
alongside it throughout.

## Internal performance (PLC-CECT)

Held-out macro-AUC on 56 patients with 95% bootstrap CIs, and the mean ± SD of pooled out-of-fold
macro-AUC over five repeats of five-fold cross-validation (the whole pipeline retrained per repeat):

| Model | Held-out | Repeated CV | Accuracy | Macro-F1 |
|---|---:|---:|---:|---:|
| Clinical (age, sex) | 0.614 (0.499–0.721) | — | 0.429 | 0.418 |
| Single-phase CNN | 0.860 (0.784–0.928) | — | 0.696 | 0.685 |
| Original four-phase CNN | 0.906 (0.829–0.971) | — | 0.821 | 0.818 |
| Phase-dropout CNN (main) | 0.919 (0.849–0.973) | 0.918 ± 0.018 | 0.786 | 0.791 |
| Radiomics (no shape) | 0.902 (0.826–0.960) | 0.918 ± 0.005 | 0.768 | 0.769 |
| **CNN + radiomics (primary)** | **0.952 (0.906–0.985)** | **0.942 ± 0.011** | 0.786 | 0.788 |
| Full fusion (+ age, sex) | 0.951 (0.903–0.984) | 0.947 ± 0.011 | 0.786 | 0.787 |

- **Comparisons.** CNN + radiomics exceeded radiomics by 0.050 (0.008–0.102) and the CNN by 0.033
  (−0.002 to 0.074) on the held-out set, and was higher in all five repeats for both. Adding age and
  sex changed the held-out AUC by −0.001 (−0.016 to 0.016). No per-class DeLong test remained
  significant after Benjamini–Hochberg adjustment across 18 tests (smallest adjusted p = 0.13).
- **Optimism.** Harrell's bootstrap optimism was 0.007 for both fusions (corrected AUC 0.962 for
  CNN + radiomics and 0.966 for full fusion).
- **Calibration.** CNN + radiomics had one-versus-rest calibration slopes of 0.82–1.12 and
  intercepts of −0.50 to 0.35 on the held-out set.
- **Missing phases.** With phases zeroed as in the original external pipeline, the original CNN
  fell to 0.861 without the delayed phase and 0.626 with the portal-venous phase alone, and its HCC
  recall collapsed (0.21 and 0.05). The phase-dropout CNN kept 0.901 and 0.775, with HCC recall 0.79
  without the delayed phase.

## Tumor size, crop truncation, and adaptive crops

The fixed 96³ crop kept less than 90% of the portal-venous tumor in 37 of 94 HCC, 12 of 99 ICC, and
18 of 85 cHCC-CCA patients; 16 HCC tumors were larger than the crop. An adaptive crop (side
max(96, 1.2 × the largest tumor extent), resampled to 96³) did not help: held-out CNN macro-AUC
0.872 against 0.919 (difference −0.047, −0.109 to 0.000), and on MCT-LTDiag 0.532 against 0.528
(DeLong p = 0.93). Size-stratified results are in `tumor_size_strata_out_of_fold.csv` and
`adaptive_crop_size_strata.csv`.

## Dataset audit and counterfactual test

The audit of all 1,112 PLC-CECT scans found class-dependent acquisition, and a counterfactual
resampling test showed that the CNN uses a non-contrast reconstruction artifact of the cHCC-CCA
scans. A post hoc census showed that tumors of 52 of 99 ICC patients lie less than 90% inside the
released liver mask, so part of the tumor is blanked in the model input. Details are in the
[dataset audit](plc_cect_dataset_audit.md).

## External validation

On MCT-LTDiag the primary CNN + radiomics model reached an HCC-versus-ICC AUC of 0.578
(0.500–0.657); calibration failed for every model, and none of 26 mitigation comparisons was
significant after Benjamini–Hochberg adjustment. On HCC-TACE-Seg, correcting the intensity window,
the axis order, and the preprocessing raised the phase-dropout CNN from 1 to 47 of 89 HCC recognized. Details are in the
[external validation page](external_validation_mct_ltdiag.md).

## Attention maps

Grad-CAM attention of the main CNN fell on the tumor more than expected by chance in held-out HCC
(median enrichment 1.21–1.29 across phases) and cHCC-CCA (1.17–1.27) and in MCT-LTDiag (HCC 1.44,
ICC 1.35), but not in held-out ICC (0.67–0.73). The non-contrast channel received the largest share
of |gradient × input| in HCC and ICC (0.33–0.34) and the smallest in cHCC-CCA (0.18). Attribution size does
not measure reliance; the counterfactual test addresses that directly. Patient example images are not
published here.

## Corrections to v1.1.0 statements

| v1.1.0 statement | Correction |
|---|---|
| W3 fold 1 and W4 fold 0 checkpoints were not retained | All five fold checkpoints of both CNNs were retained in private storage. The revision reran them: the four-phase CNN reproduces its saved predictions (largest probability difference 6 × 10⁻⁴, macro-AUC identical), and both CNNs reproduce the submitted external predictions (6 × 10⁻⁵). |
| External age and sex were unavailable | The TCIA clinical file links to all 103 HCC-TACE-Seg patients; age and sex were observed for 103 of 103 and are used in the revision. |
| The external CNN results reflect domain shift | The submitted external pipeline passed HCC-TACE-Seg volumes to the CNN with the slice axis and the first in-plane axis swapped, and used a different intensity window. Both were corrected (notebooks 17 and 20). |
| Radiomics shape features | Shape features were computed on a unit-spacing grid and are not physical measurements; they are removed from all revised models. |

The v1.1.0 tables in [`results/aggregate`](../results/aggregate/) are unchanged and remain the
record of the submitted analysis.

## What the repository cannot show

Patient-level predictions, splits, crops, masks, clinical rows, and checkpoints stay private
([privacy boundary](privacy_and_data_boundary.md)). The released tables are therefore checked for
internal consistency and against the manuscript, but recomputing them requires the source datasets
and the private run outputs.
