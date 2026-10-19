# External validation

The revision evaluates the frozen PLC-CECT models on two public cohorts. No model was fitted,
tuned, thresholded, or recalibrated on external data.

| Cohort | Role | Patients | What it can show |
|---|---|---|---|
| [MCT-LTDiag](https://doi.org/10.7910/DVN/S3RW15) (Peking Union Medical College Hospital; Harvard Dataverse version 3.1) | External validation | 103 HCC, 100 ICC | HCC-versus-ICC discrimination and calibration |
| [HCC-TACE-Seg](https://www.cancerimagingarchive.net/collection/hcc-tace-seg/) (TCIA) | Stress test | 89 HCC without mixed-scan inputs (103 in total) | HCC sensitivity only |

No public external cohort contains cHCC-CCA, so the three-class task cannot be validated externally.

## MCT-LTDiag

All four phases are present and registered to the portal-venous phase. Every scan has 5 mm slices and
an in-plane pixel size of 0.56–0.96 mm. Age and sex were observed for every patient (HCC 82 men and
21 women; ICC 47 men and 53 women), and 23 patients had recorded prior chemotherapy or TACE. Every
downloaded file was checked against its published checksum (notebook 18).

The score is p(HCC) / [p(HCC) + p(ICC)]. Sensitivity and specificity use the internal decision rule
(most probable of three classes), so a cHCC-CCA prediction counts as an error.

| Model | HCC-vs-ICC AUC (95% CI) | HCC sensitivity | ICC specificity | Calibration intercept / slope |
|---|---:|---:|---:|---:|
| **CNN + radiomics (pre-specified primary)** | **0.578 (0.500–0.657)** | 0.52 | 0.02 | −2.02 / 0.29 |
| Phase-dropout CNN | 0.528 (0.448–0.607) | 0.72 | 0.02 | −1.52 / 0.08 |
| Original CNN | 0.525 (0.445–0.605) | 0.83 | 0.17 | −0.87 / 0.07 |
| Radiomics (no shape) | 0.655 (0.579–0.731) | 0.21 | 0.10 | −1.19 / 0.26 |
| Full fusion (+ observed age, sex) | 0.690 (0.617–0.763) | 0.53 | 0.05 | −1.97 / 0.48 |
| Sex alone (post hoc) | 0.663 | — | — | — |

- **Discrimination.** The CNNs were at chance level. Radiomics kept part of its signal. Full fusion
  was higher only because sex separated the classes in this cohort (79.6% of HCC and 47.0% of ICC
  patients were men).
- **Predicted classes.** The models rarely predicted ICC and assigned many patients of both classes to
  cHCC-CCA, a class absent from the cohort.
- **Calibration.** Calibration failed for every model.
- **Sensitivity analyses.** Pre-specified preprocessing variants gave 0.57–0.63 for CNN + radiomics,
  and excluding the 23 previously treated patients gave 0.605.

All models, preprocessing variants, and subsets are in
[`external_mct_ltdiag.csv`](../results/revision_2026-10/external_mct_ltdiag.csv) and
[`calibration.csv`](../results/revision_2026-10/calibration.csv).

## Mitigation

Each strategy used internal data only, or MCT-LTDiag images without their labels, and was evaluated
once. P values are DeLong tests against the reference model, adjusted with Benjamini–Hochberg within
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

## HCC-TACE-Seg stress test

The submitted analysis reported that the CNNs recognized almost no external HCC. The revision traced
this result through each pipeline correction (notebooks 17 and 20):

| Model (89 HCC) | Submitted pipeline | + intensity window matched | + axis order fixed | + internal geometry rules |
|---|---:|---:|---:|---:|
| Original CNN | 0 | 0 | 0 | 9 |
| Phase-dropout CNN (main) | 1 | 1 | 0 | 47 |
| Single-phase CNN | 5 | 3 | 4 | 59 |
| Radiomics | — | 85 | 85 | 84 |
| CNN + radiomics | — | 11 | 7 | 67 |

The submitted pipeline read the volumes with the slice axis and the first in-plane axis swapped
relative to the training arrays. Fixing the axis order alone did not help, because 1 mm isotropic
resampling still stretched the anatomy along the slice axis compared with the training arrays.

Because the cohort contains only HCC, these numbers measure sensitivity, not discrimination. On
MCT-LTDiag the same main CNN labelled 72% of HCC and 67% of ICC patients as HCC. Full fusion
recognized 66 of 89 patients with the observed age and sex but 84 with training medians, which
shows how strongly its output depends on the clinical inputs. Results for all 103 patients are in
[`external_hcc_tace_seg.csv`](../results/revision_2026-10/external_hcc_tace_seg.csv).
