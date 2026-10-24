# October 2026 revision

Versions 2.0.0 to 2.4.0 add the analyses run during peer review of the manuscript (17–23 October
2026); version 2.4.1 exports the values of the revised manuscript that no other table contained.
Each analysis was planned in a dated analysis log before it was run (its plan sections are published
as the [analysis plans](analysis_plans.md)); analyses decided after seeing data are labelled
*post hoc*. All values below are in
[`results/revision_2026-10`](../results/revision_2026-10/README.md) (those that no other table contains
in `manuscript_values.csv`), and every notebook is listed in
the [revision notebook guide](revision_notebooks.md).

## What changed from v1.1.0

| Component | v1.1.0 (as submitted) | v2.0.0 (revision) |
|---|---|---|
| Main CNN | W4 four-phase 3D ResNet-18; checkpoint chosen on the outer validation fold; class weights from all 222 development patients | Same architecture trained with **phase dropout**, an inner validation split for checkpoint choice, and per-fold class weights |
| Radiomics | 428 candidate features including shape | **Shape features removed** (372 kept), because the released files carry no physical voxel spacing |
| Primary model | Full fusion (CNN + radiomics + age + sex) | **CNN + radiomics**; age and sex added nothing internally and only sex separated the external classes |
| Internal statistics | One held-out set; per-class DeLong tests | Adds 5 × 5 repeated cross-validation, Harrell optimism correction, Benjamini–Hochberg adjustment across 18 DeLong tests, and calibration |
| External evaluation | HCC-TACE-Seg (HCC only, sensitivity) | **MCT-LTDiag** (103 HCC, 100 ICC; observed age and sex) as the external validation; HCC-TACE-Seg repaired and kept as a stress test |
| New analyses | — | Missing-phase tests, crop truncation and size strata, adaptive crop, dataset audit, counterfactual test, tumor-inside-liver-mask census and corrected-mask analysis (post hoc), quantitative Grad-CAM, within-sex external comparison (post hoc), retraining with equalized slice density, nested stacking, acquisition-matched tests, training-seed variability |

The main CNN was chosen on 17 October 2026, after the internal held-out results of all CNN variants
were known and before any external evaluation of the new models. The original CNN is reported
alongside it throughout.

## Internal performance (PLC-CECT)

Held-out macro-AUC on 56 patients with 95% bootstrap CIs, and the mean ± SD of pooled out-of-fold
macro-AUC over five repeats of five-fold cross-validation (repeat 0: the saved models on the original
folds; repeats 1–4: the whole pipeline retrained on new folds):

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
  CNN + radiomics and 0.966 for full fusion). Fully nested stacking (notebook 30) gave slightly higher
  out-of-fold values than the non-nested stacking (CNN + radiomics 0.948 ± 0.012 vs. 0.942; full
  fusion 0.952 vs. 0.947), and CNN + radiomics stayed above both branches in all five repeats
  ([`nested_stacking_summary.csv`](../results/revision_2026-10/nested_stacking_summary.csv)).
- **Training seeds.** Retraining the main CNN with five further seeds (notebook 33) gave held-out
  macro-AUCs over the six seeds of 0.910 ± 0.009 for the CNN (0.897–0.919) and 0.947 ± 0.003 for
  CNN + radiomics (0.944–0.952); the saved main models are the best of the six (by 0.002 and 0.004 over the next-best seed), and the
  saved CNN is a favorable out-of-fold draw (0.943 against 0.913–0.924 for six retrainings).
  The 0.013 spread of the three CNN candidates lies within this seed variability
  ([`seed_variability_spread.csv`](../results/revision_2026-10/seed_variability_spread.csv)).
- **Calibration.** CNN + radiomics had one-versus-rest calibration slopes of 0.82–1.12 and
  calibration-in-the-large of −0.50 to 0.35 on the held-out set.
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

## Corrected-mask sensitivity analysis

Because liver masking blanked tumor tissue (above), notebook 28 repeated the whole pipeline with each
phase multiplied by the union of the liver and tumor masks, and retrained the CNN, radiomics (features
re-extracted), and both fusions with the same folds, seeds, and settings. The analysis is post hoc;
its decision rules were fixed before the run. None of the conclusions changed:

| Check | Main pipeline (liver mask) | Tumor preserved (liver ∪ tumor mask) |
|---|---|---|
| CNN + radiomics, held-out macro-AUC | 0.952 (0.906–0.985) | 0.963 (0.920–0.991); difference +0.011 (−0.016 to 0.042) |
| Non-contrast artifact, CNN (injected / repaired) | +0.25 / −0.50 | +0.25 / −0.42; rule met in both directions |
| MCT-LTDiag, CNN + radiomics | 0.578 (0.500–0.657) | 0.571 (0.492–0.650); paired p = 0.83 |

Radiomics improved most where tissue had been removed (out-of-fold macro-AUC 0.924 vs. 0.877 in the 83
patients with less than 90% of the tumor inside the mask). On MCT-LTDiag the retrained radiomics and
fusion models assigned 192–198 of 203 patients to cHCC-CCA at the internal decision rule, although
their AUCs were unchanged. All values are in the `corrected_mask_*.csv` tables.

## Retraining with slice density equalized

Notebook 29 tested whether removing the class-dependent slice density helps. Before cropping, every scan
was resampled along the slice axis so that its anatomical slice-density estimate (slices containing
liver divided by the largest in-plane liver width) equals 0.4468, the median of the development
patients' portal-venous scans; MCT-LTDiag received the same label-free rule. The CNN, radiomics
(features re-extracted), and both fusions were retrained with the same folds, seeds, and settings. The
decision rules were fixed in the analysis log before the run.

| Check | Main pipeline | Slice density equalized |
|---|---|---|
| Class medians of the slice-density estimate (largest / smallest) | 2.2–5.4-fold | at most 1.011-fold |
| Slice counts alone, held-out macro-AUC | 0.853 | 0.678 |
| CNN + radiomics, held-out macro-AUC | 0.952 (0.906–0.985) | 0.934 (0.872–0.978); difference −0.018 (−0.061 to 0.024) |
| Non-contrast series made thick before equalization, CNN | — | +0.087 (0.067 to 0.107) |
| MCT-LTDiag, CNN + radiomics | 0.578 (0.500–0.657) | 0.510 (0.430–0.590); paired p = 0.17 |
| MCT-LTDiag, radiomics | 0.655 (0.579–0.731) | 0.474 (0.394–0.554); paired p < 0.001 |

Equalization removed most of the slice-count signal without a measurable change in held-out
performance, but it did not improve external discrimination, and the equalized models assigned almost
every MCT-LTDiag patient to cHCC-CCA at the internal decision rule. The equalized CNN still responded to
a thick non-contrast reconstruction: resampling equalizes the number of slices, not the through-plane
blur of a thick reconstruction. All values are in the `equalized_density_*.csv` tables.

## Acquisition-matched tests

Notebooks 31 and 32 asked how much of the external failure the acquisition explains. Every internal
scan was given the slice spacing of MCT-LTDiag, which has 5 mm slices: adjacent slices were averaged
until the ratio of liver slices to liver width reached the MCT-LTDiag median (0.117). A blur-only
control applied the same averaging and then interpolated back to the original slice count. The
decision rules were fixed in the analysis log before the runs ([analysis plans](analysis_plans.md),
section 60).

| CNN + radiomics | Internal HCC-vs-ICC AUC (n = 39) | Internal macro-AUC (n = 56) | MCT-LTDiag AUC (95% CI) | Internal ICC patients called ICC (of 99) | MCT-LTDiag patients called ICC / cHCC-CCA (of 203) |
|---|---:|---:|---:|---:|---:|
| Main pipeline (unchanged scans) | 0.947 | 0.952 | 0.578 (0.500–0.657) | 89 | 4 / 97 |
| Frozen models, internal scans at MCT-LTDiag spacing | 0.795 | 0.735 | — | 15 | — |
| Frozen models, blur-only control | 0.932 | 0.887 | — | 92 | — |
| Retrained, slice density equalized at the development median (notebook 29) | 0.921 | 0.934 | 0.510 (0.430–0.590) | 80 | 4 / 198 |
| Retrained, all scans at MCT-LTDiag spacing | 0.929 | 0.905 | 0.627 (0.550–0.703) | 63 | 10 / 191 |

Internal values are held-out, except the ICC calls, which count all 99 ICC patients (development
patients out of fold). Out of fold (n = 154), the internal HCC-versus-ICC AUCs of the five rows were
0.963, 0.765, 0.928, 0.954, and 0.878. Decisions use the most probable of three classes. The frozen rows were
evaluated internally only; their external inputs are unchanged by construction.

- **Frozen models.** MCT-like acquisition lowered the held-out HCC-versus-ICC AUC from 0.947 to 0.795
  (−0.153, −0.274 to −0.050), while the blur-only control changed it little (−0.016, −0.068 to 0.026)
  but lowered the three-class macro-AUC (0.887) and the number of HCC patients called HCC (81 to 33 of
  94), so blur and slice geometry are not fully separated. By the pre-specified rule, acquisition
  explains part of the external loss: 41% held-out (95% CI 12–88%) and 51% out of fold (33–75%), with
  the CIs and the out-of-fold share computed post hoc by bootstrap over both cohorts. ICC predictions almost disappeared, as on MCT-LTDiag. A thick non-contrast reconstruction made
  by the same averaging raised the CNN's cHCC-CCA probability by 0.281 (0.237–0.325; blur-only control
  0.040).
- **Retrained models.** Retraining every model at the MCT-LTDiag spacing removed most of the
  slice-count signal (slice counts alone: held-out macro-AUC 0.853 to 0.661) and kept the internal
  discrimination of CNN + radiomics within the rule (macro-AUC −0.047, −0.103 to 0.002), although the
  CNN alone fell (0.802 vs. 0.919); out of fold, the HCC-versus-ICC AUC of CNN + radiomics fell from
  0.963 to 0.878. On MCT-LTDiag, CNN + radiomics reached 0.627: better than chance, but not better
  than the main model (paired p = 0.30), and it called 191 of 203 MCT-LTDiag patients cHCC-CCA, as
  the models retrained with corrected masks (197) and equalized slice density (198) did: the cHCC-CCA
  non-contrast scans, the only native thick reconstructions in training, stay almost unchanged by slab
  averaging (median factor 0.91), like every MCT-LTDiag scan. The pre-specified readings of the
  retrainings, including that acquisition geometry is not the main cause of the external failure,
  are therefore inconclusive.

Thickening removes image detail as well as the shortcut, so a fall in performance cannot be attributed
to the shortcut alone. All values are in the `acquisition_matched_*.csv` tables.

## External validation

On MCT-LTDiag the primary CNN + radiomics model reached an HCC-versus-ICC AUC of 0.578
(0.500–0.657), at most marginally better than chance (the first run, which excluded two patients
contrary to the plan, gave 0.581, 0.503–0.660, on 201 patients); calibration failed for every model, and none of 26 mitigation comparisons was
significant after Benjamini–Hochberg adjustment. On HCC-TACE-Seg, the phase-dropout CNN recognized
1 of 89 HCC with the submitted pipeline, 0 after the axis order was fixed with 1 mm isotropic voxels,
and 47 after the internal geometry rules (native slices, internal in-plane pixel size and crop): only
this last step changed its predictions.
Full fusion's higher external AUC (0.690) disappeared within each sex: within men and within women it
was no better than CNN + radiomics (post hoc), consistent with the sex composition of the two classes. Details are in the
[external validation page](external_validation_mct_ltdiag.md).

## Attention maps

Grad-CAM attention of the main CNN gave the tumor more than its share of the crop (not tested
statistically) in held-out HCC
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
| The external CNN results reflect domain shift | The submitted external pipeline passed HCC-TACE-Seg volumes to the CNN with the slice axis and the first in-plane axis swapped, used a different intensity window, and resampled them to 1 mm isotropic voxels. All three are documented (notebooks 17 and 20); the step-by-step correction shows that only the last step, which changed slice spacing, in-plane pixel size, and crop construction together, changed the CNN predictions. Its phase-assignment rules also took the non-contrast and arterial inputs of about half of the patients from a later examination than the segmentation; this is documented, not changed. |
| Radiomics shape features | Shape features were computed on a unit-spacing grid and are not physical measurements; they are removed from all revised models. |

The v1.1.0 tables in [`results/aggregate`](../results/aggregate/) are unchanged and remain the
record of the submitted analysis.

## What the repository cannot show

Patient-level predictions, splits, crops, masks, clinical rows, and checkpoints stay private
([privacy boundary](privacy_and_data_boundary.md)). The released tables are therefore checked for
internal consistency and against the manuscript, but recomputing them requires the source datasets
and the private run outputs.
