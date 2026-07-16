# Manuscript and repository alignment

This repository uses the finalized scientific specification for the reported study.

## Internal preprocessing

Each P, C1, C2, and C3 CT phase was liver-masked and independently cropped to `96 x 96 x 96` voxels around its own tumor-mask centroid, with a same-phase liver-centroid fallback for an empty tumor mask. The independently lesion-centered crops were stacked as W4 channels. No explicit interphase registration or physical-coordinate mapping was performed, so voxelwise anatomical correspondence across channels was not guaranteed.

The public code and documentation do not substitute shared-reference cropping for this historical method.

## Radiomics and crop retention

W5 extracted crop-restricted tumor radiomics from the retained portion of each phase's fixed crop. It is not described as guaranteed complete-lesion radiomics. The public C2-only aggregate audit reports exact retention in 124/278 patients, some loss in 154/278, median retention of 99.89%, minimum retention of 15.64%, volume-weighted retention of 61.46%, and no empty C2 crops. Equivalent P, C1, and C3 retention values are unavailable and are not inferred.

## Fusion

The full-fusion vector contains eight features: W4 probabilities for HCC, ICC, and cHCC-CCA; W5 probabilities in the same order; age; and sex. W3 remains a comparator and is excluded. Fold-specific multinomial logistic regression was the meta-learner.

## Statistical interpretation

Nine raw two-sided DeLong p-values are exploratory. The smallest raw p-value, 0.0293, was full fusion versus W4 multiphase CNN for cHCC-CCA. Full fusion versus W5 for that class had p=0.3457. No comparison remained significant after Bonferroni or Benjamini-Hochberg correction across nine tests.

## External interpretation

HCC-TACE-Seg supplied an HCC-only transportability stress test of 103 retained patients, not multiclass external validation. Internal and external adapters differed in conversion, resampling, crop construction, phase and feature availability, segmentation inputs, and missing-data handling.

The historical full-fusion adapter used sex=0 and yielded HCC sensitivity 0.019. A deterministic locked fold-median sex=1 sensitivity analysis yielded 0.806 and changed 82/103 labels. The latter is not the historical result and does not assert observed sex. Radiomics control results show strong dependence on the imputation pathway. No verified external CNN-plus-radiomics result is reported.

## Validation and reconstruction limits

CNN checkpoint selection used outer validation folds that also produced OOF predictions, and class weights used labels across the 222-patient development cohort. These choices can make CV and stacking estimates optimistic but did not involve patient leakage or the 56-patient held-out evaluation set.

Aggregate metric reanalysis is supported. Exact all-fold reconstruction is limited by missing W3 fold 1 and W4 fold 0 checkpoints, unavailable original geometry and phase-specific crop coordinates, and intentional nonpublication of patient-level derived artifacts.
