# External validation

The revision evaluates the frozen PLC-CECT models on two public cohorts. No model was fitted,
tuned, thresholded, or recalibrated on external data.

| Cohort | Role | Patients | What it can show |
|---|---|---|---|
| [MCT-LTDiag](https://doi.org/10.7910/DVN/S3RW15) (Peking Union Medical College Hospital; Harvard Dataverse version 3.1) | External validation | 103 HCC, 100 ICC | HCC-versus-ICC discrimination and calibration |
| [HCC-TACE-Seg](https://doi.org/10.7937/TCIA.5FNA-0924) (TCIA) | Stress test | 89 HCC without mixed-scan inputs (103 in total) | HCC sensitivity only |

No public external cohort contains cHCC-CCA, so the three-class task cannot be validated externally.

## MCT-LTDiag

All four phases are present and registered to the portal-venous phase. Every scan has 5 mm slices and
an in-plane pixel size of 0.56–0.96 mm. Age and sex were observed for every patient (HCC 82 men and
21 women; ICC 47 men and 53 women), and 23 patients had recorded prior chemotherapy or TACE. Every
downloaded file was checked against its published checksum (notebook 18).

The score is p(HCC) / [p(HCC) + p(ICC)]. HCC sensitivity (HCC patients called HCC), ICC recall (ICC
patients called ICC), and the share of ICC patients not called HCC use the internal decision rule
(most probable of three classes).

| Model | HCC-vs-ICC AUC (95% CI) | HCC sensitivity | ICC recall; ICC not called HCC | Calibration-in-the-large / slope / Brier |
|---|---:|---:|---:|---:|
| **CNN + radiomics (pre-specified primary)** | **0.578 (0.500–0.657)** | 0.52 | 0.02; 0.52 | −2.02 / 0.29 / 0.37 |
| Phase-dropout CNN | 0.528 (0.448–0.607) | 0.72 | 0.02; 0.33 | −1.52 / 0.08 / 0.34 |
| Original CNN | 0.525 (0.445–0.605) | 0.83 | 0.17; 0.22 | −0.87 / 0.07 / 0.31 |
| Radiomics (no shape) | 0.655 (0.579–0.731) | 0.21 | 0.10; 0.88 | −1.19 / 0.26 / 0.30 |
| Full fusion (+ observed age, sex) | 0.690 (0.617–0.763) | 0.53 | 0.05; 0.61 | −1.97 / 0.48 / 0.32 |
| Sex alone (post hoc) | 0.663 | — | — | — |

- **Discrimination.** CNN + radiomics was at most marginally better than chance (lower bound of the
  95% CI 0.4997). The first run of this evaluation (notebook 19) excluded two patients whose masks lay
  on another grid, contrary to the plan, and gave 0.581 (0.503–0.660) on 201 patients; notebook 21
  restored them, and the table uses all 203. The CNNs were at chance level. Radiomics kept part of its signal. Full fusion
  was higher because sex separated the classes in this cohort (79.6% of HCC and 47.0% of ICC
  patients were men): within men and within women it was no better than CNN + radiomics (+0.009,
  p = 0.68; −0.004, p = 0.87; post hoc,
  [`external_mct_ltdiag_by_sex.csv`](../results/revision_2026-10/external_mct_ltdiag_by_sex.csv)).
- **Predicted classes.** The models rarely predicted ICC (2 to 17 of 100 ICC patients) and assigned many patients of both classes to
  cHCC-CCA, a class absent from the cohort; three-class accuracy over the 203 patients was 0.28 for
  CNN + radiomics (0.16–0.51 across models). The predicted classes followed the slice spacing: after
  1 mm isotropic resampling, CNN + radiomics called 97 of 103 HCC and 93 of 100 ICC patients ICC.
- **Calibration.** Calibration failed for every model (Brier scores 0.30–0.37, against 0.25 for a
  constant prediction of 0.5). For the same HCC-versus-ICC score, CNN + radiomics had a
  calibration-in-the-large of −2.02 and a slope of 0.29 externally, against −0.26 and 0.89 on the 39 held-out HCC and ICC patients
  (post hoc; Figure 7B, drawn by `make_revision_figures.py`).
- **Sensitivity analyses.** Pre-specified preprocessing variants gave 0.57–0.63 for CNN + radiomics,
  excluding the 23 previously treated patients gave 0.605, and preserving the tumor tissue (corrected
  mask, notebook 28) gave 0.571 (paired p = 0.83).

All models, preprocessing variants, and subsets are in
[`external_mct_ltdiag.csv`](../results/revision_2026-10/external_mct_ltdiag.csv) and
[`calibration.csv`](../results/revision_2026-10/calibration.csv).

## Mitigation

Each strategy used internal data only, or MCT-LTDiag images without their labels, and was evaluated
once; ComBat is the only one that estimated parameters (its feature adjustments) from MCT-LTDiag, and the
acquisition-matched tests below took their target slice spacing from the MCT-LTDiag scans. P values are DeLong tests against the reference model, adjusted with Benjamini–Hochberg within
each family ([`external_mct_ltdiag_mitigation_comparisons.csv`](../results/revision_2026-10/external_mct_ltdiag_mitigation_comparisons.csv)).

| Strategy | External AUC | Difference vs reference (95% CI) | Adjusted p |
|---|---:|---:|---:|
| ComBat harmonization of radiomics | 0.550 | −0.104 (−0.183 to −0.024) | 0.09 |
| Perturbation-robust radiomics | 0.691 | +0.036 (−0.039 to 0.110) | 0.57 |
| CNN + radiomics without the non-contrast phase | 0.666 | +0.087 (0.012–0.160) | 0.29 |

Test-time harmonization, scanner-variation training, and their combination left the CNN near chance
(0.535–0.549). None of the 26 comparisons was significant after adjustment. Models without the
non-contrast phase were nominally better externally, which is consistent with, but does not prove,
the [non-contrast artifact](plc_cect_dataset_audit.md) hindering transfer.

Retraining every model with slice density equalized across classes (notebook 29; decision rules fixed
before the run) did not improve external discrimination either: CNN + radiomics 0.510 vs. 0.578
(paired p = 0.17) and radiomics 0.474 vs. 0.655 (p < 0.001), and the equalized models assigned almost
every patient to cHCC-CCA at the internal decision rule
([`equalized_density_external.csv`](../results/revision_2026-10/equalized_density_external.csv)).

Retraining every model with all scans at the slice spacing of MCT-LTDiag (notebook 32) gave
CNN + radiomics 0.627 (0.550–0.703): better than chance but not better than the main model (paired
p = 0.30), with 191 of 203 patients called cHCC-CCA
([`acquisition_matched_retrained_external.csv`](../results/revision_2026-10/acquisition_matched_retrained_external.csv)).
Giving the internal scans this spacing reproduced 41% of the external loss (post hoc 95% CI 12–88%;
notebook 31), and the retrained models, at 0.929 held-out, fell to 0.878 out of fold (see the
[revision overview](revision_2026-10.md#acquisition-matched-tests)).

## HCC-TACE-Seg stress test

The submitted analysis reported that the CNNs recognized almost no external HCC. The revision traced
this result through each pipeline correction (notebooks 17 and 20):

| Model (89 HCC) | Submitted pipeline | + intensity window matched | + axis order fixed (1 mm isotropic) | + internal geometry rules (native slices) |
|---|---:|---:|---:|---:|
| Original CNN | 0 | 0 | 0 | 9 |
| Phase-dropout CNN (main) | 1 | 1 | 0 | 47 |
| Single-phase CNN | 5 | 3 | 4 | 59 |
| Radiomics | — | 85 | 85 | 84 |
| CNN + radiomics | — | 11 | 7 | 67 |

The submitted pipeline read the volumes with the slice axis and the first in-plane axis swapped
relative to the training arrays and resampled them to 1 mm isotropic voxels. Only the last step
changed the CNN predictions: with 1 mm isotropic voxels the main CNN called 86 of 89 patients ICC, and
after the internal geometry rules, which keep the native 2.5 mm slices and apply the internal in-plane
pixel size and crop together, it recognized 47. This matches the dependence on input geometry seen
internally and is not evidence of a corrected pipeline error. The
phase-assignment rules of the submitted pipeline, which the revision kept, also took the non-contrast
input from a later examination than the segmentation in 51 of 96 patients and the arterial input in 28
of 59; only the portal-venous input is always the segmented series.

Because the cohort contains only HCC, these numbers measure sensitivity, not discrimination. On
MCT-LTDiag the same main CNN labelled 72% of HCC and 67% of ICC patients as HCC. Full fusion
recognized 66 of 89 patients with the observed age and sex but 84 with training medians, which
shows how strongly its output depends on the clinical inputs. Radiomics recognized 84 of 89 although
64% of its selected feature cells in all 103 patients had to be filled with training-fold medians; fed only these medians,
it predicted cHCC-CCA for all 89 patients. Results for all 103 patients are in
[`external_hcc_tace_seg.csv`](../results/revision_2026-10/external_hcc_tace_seg.csv).
