# Repository scope

This repository accompanies the research study "Multimodal Classification of Primary Liver Tumors on Multiphase CT: Internal Fusion Performance and External Transportability Stress Testing." It documents the historical analysis that produced the reported results and provides privacy-safe aggregate artifacts, reusable analysis utilities, configuration templates, curated notebooks, and synthetic-data tests.

## Included scope

- The verified four-phase, independently lesion-centered preprocessing method.
- W3 single-phase CNN, W4 four-phase CNN, W5 crop-restricted radiomics-LightGBM, the clinical baseline, and late-fusion specifications.
- Aggregate internal performance, exploratory DeLong comparisons, C2 crop-retention findings, and external HCC-only stress-test summaries.
- Deterministic reanalysis utilities that operate on authorized local artifacts or released aggregate files.
- Explicit scientific, privacy, and reproducibility boundaries.

## Deliberate boundaries

The repository does not distribute CT images, masks, clinical rows, patient identifiers, patient-level splits or predictions, manuscript files, or private derived artifacts. Dataset access remains subject to each source repository's terms. Model training and clinical deployment are outside the release-validation workflow.

The repository does not claim that phase inputs were registered or voxelwise aligned. It does not present a proposed shared-reference crop as the method used for the paper. Registration, physical-coordinate alignment, controlled resampling, and adaptive crop design are future research directions.

## Intended use

The software and documentation are for research and aggregate scientific audit only. They are not a medical device and must not be used for diagnosis, treatment selection, or patient management. See [scientific scope](scientific_scope.md), [privacy boundary](privacy_and_data_boundary.md), and [reproducibility](reproducibility.md).
