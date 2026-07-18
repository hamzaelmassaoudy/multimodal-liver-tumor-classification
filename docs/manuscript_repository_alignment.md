# Manuscript and repository alignment

This release follows the corrected primary analysis reported in the final manuscript.

## Internal preprocessing and radiomics

Each P, C1, C2, and C3 phase was independently cropped to `96 x 96 x 96` voxels around
its own tumor-mask centroid, with a same-phase liver-centroid fallback for an empty tumor mask.
The crops were stacked as W4 channels. No explicit interphase registration or physical-coordinate
mapping was performed.

W5 extracted crop-restricted tumor radiomics. The public C2 audit reports exact retention in
124/278 patients, some loss in 154/278, median retention 99.89%, minimum 15.64%, and
volume-weighted retention 61.46%. Cached arrays lacked geometry and spacing; SimpleITK conversion
used unit spacing, so shape outputs are not verified physical-unit measurements.

## Clinical variables and fusion

The internal provenance audit found 185 male, 90 female, and three unresolved sex entries. The
corrected primary analysis retained unresolved values as missing and used fold-local training
medians. The historical non-male-to-zero encoding is reported only as a sensitivity analysis.

Full fusion contains eight features: W4 probabilities for HCC, ICC, and cHCC-CCA; W5 probabilities
in the same order; age; and sex. W3 is a comparator and is excluded. Corrected clinical and fusion
logistic regressions were refitted on internal data; upstream W3, W4, W5, CNN, radiomics, and
LightGBM components were not retrained.

Corrected full fusion achieved CV macro-AUC `0.955 ± 0.033` and held-out macro-AUC 0.945
(95% CI 0.890–0.984), with 45/56 correct. Historical full-fusion held-out AUC was 0.950;
correction changed one held-out prediction and no OOF hard prediction.

## Statistical interpretation

Nine raw two-sided DeLong comparisons are exploratory. The smallest raw p-value, 0.029347,
was full fusion versus W4 for cHCC-CCA; its adjusted values were both 0.264126. Full fusion
versus W5 for that class had p=0.345737. No comparison remained significant after Bonferroni
or Benjamini–Hochberg correction across nine tests.

## External interpretation

HCC-TACE-Seg supplied an HCC-only stress test of 103 patients. Missing external sex with each
corrected fusion model’s fold-local median yielded sensitivity 0.806 (83/103; CI 0.728–0.883).
Encoded sex=0 yielded 0.019 (2/103; CI 0–0.049), and 82/103 hard labels differed. Both values
are model-defined because external age and sex were unavailable.

C2 fallback occurred for 102/103 patients, preventing a meaningful fallback comparison. Strict
radiomics Condition C was an internal diagnostic refit using an externally defined availability
subset, not frozen external validation. No verified external CNN-plus-radiomics result is reported.

## Reconstruction limits

Aggregate reanalysis is supported. Exact all-fold reconstruction is limited by missing W3 fold 1
and W4 fold 0 checkpoints, unavailable source geometry and phase-specific crop coordinates, and
intentional nonpublication of patient-level artifacts.
