# Revision results (October 2026)

Cohort-level tables and figures of the [October 2026 revision](../../docs/revision_2026-10.md). They
contain no patient identifiers, patient rows, probabilities, split membership, images, or masks.
The tables were exported from the private run outputs by
[`export_revision_aggregates.py`](../../scripts/revision/export_revision_aggregates.py) (the
tumor-inside-liver-mask tables by
[`summarize_tumor_inside_liver_mask.py`](../../scripts/revision/summarize_tumor_inside_liver_mask.py)),
and their values match the revised manuscript.

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
| [`calibration.csv`](calibration.csv) | Brier score, calibration intercept and slope, internally and on MCT-LTDiag |

## Tumor size and crops

| File | Contents |
|---|---|
| [`crop_truncation_by_class_phase.csv`](crop_truncation_by_class_phase.csv) | Share of each tumor kept by the fixed 96³ crop, by class and phase, with cross-phase overlap |
| [`tumor_size_strata_out_of_fold.csv`](tumor_size_strata_out_of_fold.csv) | Out-of-fold performance by tumor-size third and by truncation |
| [`adaptive_crop_internal.csv`](adaptive_crop_internal.csv) | Adaptive-crop and fixed-crop CNNs and fusions, internal, under each phase pattern |
| [`adaptive_crop_size_strata.csv`](adaptive_crop_size_strata.csv) | Adaptive-crop results by tumor-size third |
| [`adaptive_crop_external.csv`](adaptive_crop_external.csv) | Adaptive-crop results on MCT-LTDiag, including large tumors |
| [`adaptive_crop_paired_differences.csv`](adaptive_crop_paired_differences.csv) | Adaptive minus fixed crop, internal and external |

## Dataset audit and attention

| File | Contents |
|---|---|
| [`dataset_audit_by_class.csv`](dataset_audit_by_class.csv) | File counts, three-channel storage, empty masks, and slice measures by class and phase |
| [`acquisition_only_discrimination.csv`](acquisition_only_discrimination.csv) | Discrimination by slice counts alone compared with CNN + radiomics (post hoc) |
| [`tumor_inside_liver_mask_by_class_phase.csv`](tumor_inside_liver_mask_by_class_phase.csv) | Share of each tumor mask inside the released liver mask (post hoc) |
| [`performance_by_tumor_inside_liver_mask.csv`](performance_by_tumor_inside_liver_mask.csv) | Model performance by that share (post hoc) |
| [`counterfactual_effects.csv`](counterfactual_effects.csv) | Counterfactual slice-resampling shifts against matched smoothing controls, with the pre-specified criteria |
| [`counterfactual_predicted_classes.csv`](counterfactual_predicted_classes.csv) | Predicted classes for unchanged, control, and counterfactual scans |
| [`attention_enrichment_summary.csv`](attention_enrichment_summary.csv) | Grad-CAM attention inside the tumor relative to the tumor's share of the crop |
| [`attention_phase_share_summary.csv`](attention_phase_share_summary.csv) | Share of gradient × input attribution per phase |

## External cohorts

| File | Contents |
|---|---|
| [`external_mct_ltdiag.csv`](external_mct_ltdiag.csv) | MCT-LTDiag AUC (DeLong and bootstrap CI), sensitivity, specificity, and predicted classes for every model, preprocessing variant, and subset |
| [`external_mct_ltdiag_mitigation.csv`](external_mct_ltdiag_mitigation.csv) | Every mitigation strategy on MCT-LTDiag |
| [`external_mct_ltdiag_mitigation_comparisons.csv`](external_mct_ltdiag_mitigation_comparisons.csv) | Mitigation versus reference: difference, DeLong p, and Benjamini–Hochberg-adjusted p within each family |
| [`external_hcc_tace_seg.csv`](external_hcc_tace_seg.csv) | HCC-TACE-Seg HCC recognition after each pipeline correction, for 89 and 103 patients |

## Figures

The figures are the manuscript figures, drawn by
[`make_revision_figures.py`](../../scripts/revision/make_revision_figures.py) at 600 dpi. Figures 2,
6, and 8 show patient images and are not published here.

| File | Contents |
|---|---|
| [`figure1_study_design.png`](figures/figure1_study_design.png) | Cohorts, preprocessing, models, and evaluation |
| [`figure3_internal_performance.png`](figures/figure3_internal_performance.png) | Held-out discrimination with and without the non-contrast phase, repeated cross-validation, confusion table, and missing-phase robustness |
| [`figure4_size_truncation.png`](figures/figure4_size_truncation.png) | Crop truncation, size strata, and the adaptive crop |
| [`figure5_dataset_artifacts.png`](figures/figure5_dataset_artifacts.png) | Slice counts by class and acquisition-only discrimination |
| [`figure7_external_validation.png`](figures/figure7_external_validation.png) | MCT-LTDiag discrimination, calibration, and mitigation |
