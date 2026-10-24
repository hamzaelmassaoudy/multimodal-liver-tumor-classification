# Revision results (October 2026)

Cohort-level tables and figures of the [October 2026 revision](../../docs/revision_2026-10.md). They
contain no patient identifiers, patient rows, probabilities, split membership, images, or masks.
The tables were exported from the private run outputs by
[`export_revision_aggregates.py`](../../scripts/revision/export_revision_aggregates.py) (the
tumor-inside-liver-mask tables by
[`summarize_tumor_inside_liver_mask.py`](../../scripts/revision/summarize_tumor_inside_liver_mask.py)),
and the values of the tables used in the revised manuscript match it.

Conventions: AUCs are macro-AUCs (one-versus-rest, three classes) internally and HCC-versus-ICC AUCs
for the score p(HCC) / [p(HCC) + p(ICC)] externally. `CHCC` in a column or row denotes cHCC-CCA.
Held-out results use the 56-patient held-out set; out-of-fold results use the 222 development
patients. A `post_hoc` column marks analyses decided after seeing data.

## Internal models (PLC-CECT)

| File | Contents |
|---|---|
| [`internal_models.csv`](internal_models.csv) | Held-out macro-AUC with bootstrap CI, accuracy, macro-F1, cross-validation, repeated cross-validation, and results without the non-contrast phase for all seven models |
| [`internal_comparisons.csv`](internal_comparisons.csv) | Paired held-out differences with bootstrap CI and p, smallest Benjamini–Hochberg-adjusted DeLong p, and repeated-CV differences |
| [`internal_per_class.csv`](internal_per_class.csv) | Held-out sensitivity and specificity per class with exact CIs |
| [`internal_repeated_cv_summary.csv`](internal_repeated_cv_summary.csv) | 5 × 5 repeated cross-validation: pooled out-of-fold, all-25-fold spread, and held-out ensembles |
| [`internal_repeated_cv_per_fold.csv`](internal_repeated_cv_per_fold.csv) | Macro-AUC of every repeat and fold |
| [`internal_optimism.csv`](internal_optimism.csv) | Harrell bootstrap optimism and optimism-corrected AUC of both fusions |
| [`internal_missing_phase_patterns.csv`](internal_missing_phase_patterns.csv) | Original, retrained, and phase-dropout CNNs under seven phase patterns |
| [`internal_fusion_missing_phase_patterns.csv`](internal_fusion_missing_phase_patterns.csv) | The fusions under the same phase patterns |
| [`calibration.csv`](calibration.csv) | Brier score, calibration-in-the-large (column `intercept`, slope fixed at 1) and calibration slope, internally and on MCT-LTDiag |

## Tumor size and crops

| File | Contents |
|---|---|
| [`crop_truncation_by_class_phase.csv`](crop_truncation_by_class_phase.csv) | Share of each tumor kept by the fixed 96³ crop, by class and phase, with cross-phase overlap |
| [`tumor_size_strata_out_of_fold.csv`](tumor_size_strata_out_of_fold.csv) | Out-of-fold performance by tumor-size third and by truncation |
| [`tumor_size_by_inplane_extent.csv`](tumor_size_by_inplane_extent.csv) | Macro-AUC with bootstrap CI and accuracy by third of the in-plane portal-venous tumor extent, out of fold and held-out (post hoc; Supplementary Table S11) |
| [`adaptive_crop_internal.csv`](adaptive_crop_internal.csv) | Adaptive-crop and fixed-crop CNNs and fusions, internal, under each phase pattern; `cv_sd` is the population SD of the five fold AUCs as the run reported it, `cv_sd_sample` the sample SD used in the other tables |
| [`adaptive_crop_size_strata.csv`](adaptive_crop_size_strata.csv) | Adaptive-crop results by tumor-size third |
| [`adaptive_crop_external.csv`](adaptive_crop_external.csv) | Adaptive-crop results on MCT-LTDiag, including large tumors |
| [`adaptive_crop_paired_differences.csv`](adaptive_crop_paired_differences.csv) | Adaptive minus fixed crop, internal and external |

## Dataset audit and attention

| File | Contents |
|---|---|
| [`dataset_audit_by_class.csv`](dataset_audit_by_class.csv) | File counts, three-channel storage, empty masks, and slice measures by class and phase |
| [`acquisition_only_discrimination.csv`](acquisition_only_discrimination.csv) | Discrimination by slice counts alone compared with CNN + radiomics, also within the subset with ambiguous slice counts (post hoc) |
| [`tumor_inside_liver_mask_by_class_phase.csv`](tumor_inside_liver_mask_by_class_phase.csv) | Share of each tumor mask inside the released liver mask (post hoc) |
| [`performance_by_tumor_inside_liver_mask.csv`](performance_by_tumor_inside_liver_mask.csv) | Model performance by that share (post hoc) |
| [`counterfactual_effects.csv`](counterfactual_effects.csv) | Counterfactual slice-resampling shifts against matched smoothing controls, with the pre-specified criteria |
| [`counterfactual_predicted_classes.csv`](counterfactual_predicted_classes.csv) | Predicted classes for unchanged, control, and counterfactual scans |
| [`attention_enrichment_summary.csv`](attention_enrichment_summary.csv) | Grad-CAM attention inside the tumor relative to the tumor's share of the crop |
| [`attention_phase_share_summary.csv`](attention_phase_share_summary.csv) | Share of gradient × input attribution per phase |

## External cohorts

| File | Contents |
|---|---|
| [`external_mct_ltdiag.csv`](external_mct_ltdiag.csv) | MCT-LTDiag AUC (DeLong and bootstrap CI), HCC sensitivity, the share of ICC patients called ICC (column `icc_specificity`), and predicted classes for every model, preprocessing variant, and subset; standard specificity (ICC not called HCC) follows from the counts |
| [`external_mct_ltdiag_mitigation.csv`](external_mct_ltdiag_mitigation.csv) | Every mitigation strategy on MCT-LTDiag |
| [`external_mct_ltdiag_mitigation_comparisons.csv`](external_mct_ltdiag_mitigation_comparisons.csv) | Mitigation versus reference: difference, DeLong p, and Benjamini–Hochberg-adjusted p within each family |
| [`external_hcc_tace_seg.csv`](external_hcc_tace_seg.csv) | HCC-TACE-Seg HCC recognition after each pipeline correction, for 89 and 103 patients |
| [`external_mct_ltdiag_secondary_comparisons.csv`](external_mct_ltdiag_secondary_comparisons.csv) | The secondary comparisons of the analysis plan (phase-dropout versus original CNN, full fusion versus CNN + radiomics, radiomics versus CNN) on all 203 MCT-LTDiag patients: AUC difference with paired bootstrap 95% CI and paired DeLong p; a fourth row from the same run was not planned (`pre_specified`) |
| [`external_mct_ltdiag_by_sex.csv`](external_mct_ltdiag_by_sex.csv) | MCT-LTDiag AUC of CNN + radiomics and full fusion within men and within women, with the paired DeLong test (post hoc) |

## Corrected-mask sensitivity analysis (notebook 28, post hoc)

Each phase masked by the union of the liver and tumor masks instead of the liver mask; every model retrained with the same folds, seeds, and settings. Rows labelled `main` repeat the main models for comparison; `CHCC` denotes cHCC-CCA.

| File | Contents |
|---|---|
| [`corrected_mask_crops_by_class.csv`](corrected_mask_crops_by_class.csv) | Patients whose crops gained tumor voxels, and the portal-venous tumor share inside the liver mask, by class |
| [`corrected_mask_internal.csv`](corrected_mask_internal.csv) | Held-out and out-of-fold results of the retrained and the main models |
| [`corrected_mask_internal_paired.csv`](corrected_mask_internal_paired.csv) | Retrained minus main model: held-out bootstrap difference and out-of-fold difference |
| [`corrected_mask_by_tumor_inside_liver.csv`](corrected_mask_by_tumor_inside_liver.csv) | Results for patients with less than and at least 90% of the tumor inside the liver mask |
| [`corrected_mask_counterfactual_effects.csv`](corrected_mask_counterfactual_effects.csv) | Non-contrast artifact test with the retrained models (rules of Section 3.9 of the paper) |
| [`corrected_mask_external.csv`](corrected_mask_external.csv) | MCT-LTDiag results of the retrained and the main models |
| [`corrected_mask_external_paired.csv`](corrected_mask_external_paired.csv) | Retrained minus main model on MCT-LTDiag, paired DeLong test |

## Retraining with slice density equalized (notebook 29)

Every scan resampled along the slice axis to one anatomical slice density before cropping; every model retrained with the same folds, seeds, and settings. Rows labelled `main` repeat the main models for comparison.

| File | Contents |
|---|---|
| [`equalized_density_by_class.csv`](equalized_density_by_class.csv) | Class medians of the slice-density estimate and of the slice counts, before and after equalization, by phase |
| [`equalized_density_slice_count_model.csv`](equalized_density_slice_count_model.csv) | A slice-count-only model before and after equalization: held-out and out-of-fold discrimination |
| [`equalized_density_internal.csv`](equalized_density_internal.csv) | Held-out and out-of-fold results of the retrained and the main models |
| [`equalized_density_internal_paired.csv`](equalized_density_internal_paired.csv) | Retrained minus main model: held-out bootstrap difference and out-of-fold difference |
| [`equalized_density_residual_artifact.csv`](equalized_density_residual_artifact.csv) | Non-contrast artifact injected or repaired before equalization, against the unaltered equalized scan |
| [`equalized_density_external.csv`](equalized_density_external.csv) | MCT-LTDiag results of the retrained and the main models |
| [`equalized_density_external_paired.csv`](equalized_density_external_paired.csv) | Retrained minus main model on MCT-LTDiag, paired DeLong test |

## Nested stacking (notebook 30)

| File | Contents |
|---|---|
| [`nested_stacking_per_repeat.csv`](nested_stacking_per_repeat.csv) | Nested and non-nested out-of-fold macro-AUC of both fusions per repeat, and their differences from the two branches |
| [`nested_stacking_summary.csv`](nested_stacking_summary.csv) | Mean over the five repeats: optimism of the non-nested estimates and the number of repeats in which each fusion exceeded each branch |

## Acquisition-matched tests (notebooks 31 and 32)

Every internal scan given the slice spacing of MCT-LTDiag (median ratio of liver slices to liver width 0.117) by averaging adjacent slices. Notebook 31 evaluates the frozen main models, with a blur-only control (the same averaging, then interpolation back to the original slice count); notebook 32 retrains every model with the same folds, seeds, and settings. Rows labelled `main` or `unchanged` repeat the main models for comparison.

| File | Contents |
|---|---|
| [`acquisition_matched_frozen_hcc_vs_icc.csv`](acquisition_matched_frozen_hcc_vs_icc.csv) | Held-out and out-of-fold HCC-versus-ICC AUC of the frozen models with unchanged, MCT-like, and blur-only scans: DeLong CI, paired difference with bootstrap CI and DeLong p, share of the external loss reproduced, and the reading of the pre-specified rule |
| [`acquisition_matched_frozen_macro_auc.csv`](acquisition_matched_frozen_macro_auc.csv) | Three-class macro-AUC under the same conditions, with the paired bootstrap difference |
| [`acquisition_matched_frozen_predicted_classes.csv`](acquisition_matched_frozen_predicted_classes.csv) | Predicted classes by true class under each condition |
| [`acquisition_matched_frozen_thick_noncontrast.csv`](acquisition_matched_frozen_thick_noncontrast.csv) | Non-contrast series made thick by the same averaging in HCC and ICC scans: shift of p(cHCC-CCA) against the blur-only control, with the criteria of the counterfactual test |
| [`acquisition_matched_frozen_density_by_class.csv`](acquisition_matched_frozen_density_by_class.csv) | Scans thickened, averaging factor, class medians of the slice counts and of the slice-density estimate before and after, and tumor masks lost, by phase |
| [`acquisition_matched_retrained_by_class.csv`](acquisition_matched_retrained_by_class.csv) | Class medians of the slice-density estimate and of the slice counts before and after, by phase |
| [`acquisition_matched_retrained_slice_count_model.csv`](acquisition_matched_retrained_slice_count_model.csv) | A slice-count-only model before and after: held-out and out-of-fold discrimination |
| [`acquisition_matched_retrained_internal.csv`](acquisition_matched_retrained_internal.csv) | Held-out and out-of-fold results of the retrained and the main models, with per-class recall |
| [`acquisition_matched_retrained_internal_paired.csv`](acquisition_matched_retrained_internal_paired.csv) | Retrained minus main model: held-out bootstrap difference and p, and out-of-fold difference |
| [`acquisition_matched_retrained_residual_artifact.csv`](acquisition_matched_retrained_residual_artifact.csv) | Non-contrast artifact injected or repaired before the averaging, against the unaltered averaged scan |
| [`acquisition_matched_retrained_external.csv`](acquisition_matched_retrained_external.csv) | MCT-LTDiag AUC, HCC sensitivity, ICC recall, share of ICC patients not called HCC, and predicted classes of the retrained and the main models |
| [`acquisition_matched_retrained_external_paired.csv`](acquisition_matched_retrained_external_paired.csv) | Retrained minus main model on MCT-LTDiag, paired DeLong test |

## Training-seed variability (notebook 33)

The main CNN retrained with five further seeds (offsets +1000 to +5000) and once with its own seed (offset 0); both fusions refitted for each. Rows of the saved main models are included.

| File | Contents |
|---|---|
| [`seed_variability_per_seed.csv`](seed_variability_per_seed.csv) | Held-out and out-of-fold macro-AUC, held-out HCC-versus-ICC AUC, accuracy, and per-class recall of the CNN and both fusions for each training seed |
| [`seed_variability_spread.csv`](seed_variability_spread.csv) | Range over the three seeds of the pre-specified statement; mean, SD, minimum, and maximum over all six seeds; change on retraining with the original seed |
| [`seed_variability_training.csv`](seed_variability_training.csv) | Chosen epoch, inner-validation AUC, and training time for each seed and fold |

## Values reported in the manuscript

| File | Contents |
|---|---|
| [`manuscript_values.csv`](manuscript_values.csv) | Values of the revised manuscript that no other table contains, each with its section, CI, number of patients, `post_hoc` flag, and source run: held-out one-versus-rest AUCs, calibration of the HCC-versus-ICC score on the 39 held-out HCC and ICC patients and on MCT-LTDiag, sex alone, the first MCT-LTDiag run (201 patients), slice counts alone on MCT-LTDiag, tumor inside the liver mask on MCT-LTDiag, the non-contrast artifact repaired in every held-out cHCC-CCA scan, the share of the external loss reproduced with its bootstrap CI, the internal columns of manuscript Table 6 held-out and out of fold, the share beyond the blur-only control, the out-of-fold seed range of CNN + radiomics, the slab-averaging factor of the cHCC-CCA non-contrast scans, crop retention, the lesion-size baseline, the imputed HCC-TACE-Seg feature cells, and the study of each HCC-TACE-Seg input |

The MCT-LTDiag predictions of the main CNN in `external_mct_ltdiag.csv` and in the comparison tables come
from two inferences of the same saved model (notebooks 21 and 24); their probabilities differ by at most
4.4 × 10⁻⁵ (`manuscript_values.csv`).

## Figures

The figures are the manuscript figures, drawn by
[`make_revision_figures.py`](../../scripts/revision/make_revision_figures.py) at 600 dpi and the
printed width of 16.5 cm. Figures 2, 6, and 8 show patient images and are not published here. The
manuscript Figure 1 shows the CT crops and radiomic features of one patient; the copy here
(`--figures design_public`) has schematic tiles and a schematic feature strip instead.

| File | Contents |
|---|---|
| [`figure1_study_design.png`](figures/figure1_study_design.png) | Cohorts and data partition, model pipeline (schematic inputs), and evaluation |
| [`figure3_internal_performance.png`](figures/figure3_internal_performance.png) | Held-out discrimination with and without the non-contrast phase, repeated cross-validation, confusion table, and missing-phase robustness |
| [`figure4_size_truncation.png`](figures/figure4_size_truncation.png) | Crop truncation, size strata, and the adaptive crop |
| [`figure5_dataset_artifacts.png`](figures/figure5_dataset_artifacts.png) | Slice counts by class and acquisition-only discrimination |
| [`figure7_external_validation.png`](figures/figure7_external_validation.png) | MCT-LTDiag discrimination, calibration, and mitigation |
