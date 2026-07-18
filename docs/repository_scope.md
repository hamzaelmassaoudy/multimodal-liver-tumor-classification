# Repository scope

This repository accompanies “Multimodal Classification of Primary Liver Tumors on Multiphase CT:
Internal Fusion Performance and External Transportability Stress Testing.” It provides corrected
aggregate results, reusable analysis utilities, curated notebooks, configuration examples, and
synthetic-data tests.

## Included

- Independent phase-specific lesion-centered preprocessing.
- W3, W4, W5, clinical, and late-fusion specifications.
- Corrected internal sex handling and aggregate sensitivity evidence.
- Corrected internal performance, DeLong, paired-fold, per-class, and confusion summaries.
- C2 crop retention and external adapter/fallback summaries.
- External missing-covariate and radiomics feature-handling controls.
- Deterministic release, privacy, and scientific-invariant validation.

## Excluded

The repository does not distribute CT images, masks, clinical rows, patient identifiers,
patient-level splits or predictions, manuscript files, private derived artifacts, or checkpoints.
Dataset access remains subject to each provider’s terms. Model training and clinical deployment are
outside the release-validation workflow.

The repository does not claim registered phase inputs, physical-space correspondence, or verified
physical radiomics geometry. Registration, controlled resampling, and adaptive crops are future
research directions rather than descriptions of the reported pipeline.

## Intended use and license

The software and documentation support research and aggregate scientific audit only. They are not
a medical device. Repository-authored materials are provided under the [MIT License](../LICENSE);
third-party datasets are not included or relicensed.
