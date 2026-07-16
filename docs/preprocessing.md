# Historical preprocessing

This document describes the preprocessing that produced the reported internal results.

## Internal four-phase algorithm

The phase order was P, C1, C2, C3. For each phase independently, the historical workflow:

1. Loaded that phase's CT, tumor mask, and liver mask.
2. Applied liver masking to the CT.
3. Calculated the centroid of the positive tumor mask for that phase.
4. Used the phase's liver-mask centroid only when its tumor mask was empty.
5. Cropped CT, tumor mask, and liver mask to a `96 x 96 x 96` voxel cube around that phase-specific center.
6. Applied zero padding when a crop extended beyond an array boundary.
7. Stacked the four independently lesion-centered CT crops as channels.

The public implementation is in [`preprocessing.py`](../src/liver_tumor_pipeline/preprocessing.py). It accepts differing source depths across phases because centering and cropping occur separately.

No explicit interphase registration, physical-coordinate mapping, or correspondence-enforcing resampling was performed by the internal study pipeline. No additional resampling beyond the source release was applied internally. Equivalent tensor coordinates across W4 channels were therefore not guaranteed to depict identical anatomy. The method is a registration-free, lesion-centered representation; it must not be interpreted as voxelwise temporal tracking.

## Fixed-crop retention

The fixed cube retained nearly all tumor voxels for many cases but meaningfully truncated a subset. The retained artifacts support an aggregate audit for C2 only:

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

These values do not extend to P, C1, or C3. Original source geometry and historical phase-specific crop coordinates were not retained, so a complete four-phase audit cannot be reconstructed. Only aggregate C2 findings are released in [`c2_crop_retention.csv`](../results/aggregate/c2_crop_retention.csv).

Because truncation occurred, radiomic features are described as **crop-restricted tumor radiomics**, not guaranteed complete-lesion radiomics.

## External adapter

The historical external adapter differed from internal preprocessing in source conversion, resampling, crop construction, phase availability, segmentation inputs, feature availability, and missing-phase handling. Those differences are part of the stress test and are documented in [external stress test](external_stress_test.md).

Shared physical-space alignment, explicit registration, controlled resampling, and adaptive crop sizes are future methodological directions. They are not presented as the source of the current results.
