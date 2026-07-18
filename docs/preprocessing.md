# Preprocessing

## Internal four-phase algorithm

The phase order was P, C1, C2, C3. For each phase independently, the workflow:

1. Loaded that phase’s CT, tumor mask, and liver mask.
2. Applied liver masking to the CT.
3. Calculated the positive tumor-mask centroid for that phase.
4. Used the same-phase liver-mask centroid only when the tumor mask was empty.
5. Cropped CT, tumor mask, and liver mask to `96 x 96 x 96` around that center.
6. Applied zero padding at array boundaries.
7. Stacked the independently lesion-centered CT crops as channels.

The public implementation is in [`preprocessing.py`](../src/liver_tumor_pipeline/preprocessing.py).
No explicit interphase registration, physical-coordinate mapping, or correspondence-enforcing
resampling was performed. No additional internal resampling beyond the source release was applied.

## Fixed-crop retention

| C2 metric | Verified result |
|---|---:|
| Exact retention | 124/278 (44.6%) |
| Some tumor loss | 154/278 (55.4%) |
| Below 95% retention | 80/278 (28.8%) |
| Below 90% retention | 67/278 (24.1%) |
| Below 75% retention | 39/278 (14.0%) |
| Below 50% retention | 15/278 (5.4%) |
| Empty crops | 0/278 |
| Median retention | 99.89% |
| Minimum retention | 15.64% |
| Volume-weighted retention | 61.46% |

These values apply only to C2. Original geometry and phase-specific crop coordinates required for
equivalent P, C1, and C3 audits were not retained. W5 is therefore described as crop-restricted
tumor radiomics, not guaranteed complete-lesion radiomics.

## Historical radiomics geometry

Cached arrays did not retain source image geometry or spacing. NumPy arrays were converted to
SimpleITK images without restoring physical spacing, so default unit spacing was used. Shape
outputs must be interpreted as crop-grid or voxel-coordinate descriptors rather than verified
physical-volume or physical-distance measurements.

## Clinical metadata correction

Historical preprocessing encoded 1 only for an exact male token and mapped every other value to 0.
The corrected primary analysis instead maps male to 1, female to 0, and leaves unresolved values
missing for fold-local imputation. This correction affects clinical and fusion logistic regression;
it does not change CT preprocessing or any upstream branch output.

## External adapter

The external adapter differed from the internal workflow in conversion, resampling, crop
construction, phase availability, segmentation inputs, feature availability, and missing-phase
handling. Those differences are documented in [external stress test](external_stress_test.md).
