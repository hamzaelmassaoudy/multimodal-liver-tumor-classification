# Changelog

## 2.0.0 — 2026-10-19

Adds the analyses of the October 2026 revision of the manuscript, now titled "Multimodal
Classification of Primary Liver Tumors on Multiphase CT: Internal Performance, Acquisition
Artifacts, and Limited External Transportability". See the
[revision overview](docs/revision_2026-10.md).

### Added

- Revision notebooks 15–27: reproduction of the submitted results, radiomics without shape
  features, missing-phase tests and the phase-dropout CNN, repeated cross-validation, crop
  truncation and adaptive crops, external validation on MCT-LTDiag, the repaired HCC-TACE-Seg
  stress test, mitigation strategies, the PLC-CECT dataset audit and counterfactual test, and
  quantitative Grad-CAM.
- 27 cohort-level tables and 5 figures in `results/revision_2026-10`.
- `scripts/revision`: export of the revision tables, the manuscript figures, and the
  tumor-inside-liver-mask census and its class-level summary.
- Documentation: revision overview, PLC-CECT dataset audit, external validation, and revision
  notebook guide.
- A `revision` optional dependency group.
- Tests that lock the revision headline values, check that every revision file is documented,
  keep patient-image figures out of the repository, and check that version numbers agree.

### Changed

- The README, model card, and scientific scope describe the revised study; pages that describe the
  submitted analysis carry a version note.
- Citation metadata: version 2.0.0 and the revised title.

### Corrected

- v1.1.0 stated that the W3 fold 1 and W4 fold 0 checkpoints were not retained. All five fold
  checkpoints of both CNNs were retained privately, and the revision reproduced their saved
  predictions. The statement is corrected in the documentation, four notebook text cells, and
  `results/aggregate/reproducibility_status.json`.
- External age and sex are available for all 103 HCC-TACE-Seg patients through the TCIA clinical
  file, and are used in the revision.
- The historical external pipeline passed HCC-TACE-Seg volumes to the CNNs with two axes swapped;
  notebook 12 now says so and points to the corrected analysis.
- Crop coordinates were not saved, but the revision recomputed crops identical to the original
  crops for 278 of 278 patients.

### Unchanged

- The v1.1.0 tables and figures in `results/aggregate` and `results/figures`, and the code cells of
  notebooks 01–14.

## Repository maintenance after 1.1.0

- Shorten the front page and add a documentation index with a clear route to methods and results.
- Add shell-specific setup instructions, expected command output, and public-tools environment
  constraints.
- Add an explicitly synthetic example of training-fold clinical imputation and eight-feature fusion
  construction.
- Include examples in lint checks and run CI on Linux and Windows with Python 3.10/3.12 coverage.
- Clarify the clinical-data availability statement and separate frozen external inference from the
  Condition C diagnostic refit.

## 1.1.0 — 2026-07-18

The [v1.1.0 release](https://github.com/hamzaelmassaoudy/multimodal-liver-tumor-classification/releases/tag/v1.1.0)
is the fixed software reference for the analysis as submitted. Its aggregate results include the
missing-sex correction and retain the historical encoding as a sensitivity analysis. Its tag and
archived contents are not replaced by later versions.
