# Changelog

## 2.2.0 — 2026-10-22

Two analyses planned after an independent review of the revision; their decision rules were fixed in the
analysis log before either run. The main models and all earlier results are unchanged.

### Added

- Notebook 29: retraining with slice density equalized across classes. Before cropping, every scan is
  resampled along the slice axis so that its anatomical slice-density estimate (slices containing liver
  divided by the largest in-plane liver width) equals one target, 0.4468, the median of the development
  patients' portal-venous scans; MCT-LTDiag gets the same label-free rule. The CNN, radiomics (features
  re-extracted), and both fusions are retrained with the same folds, seeds, and settings. Equalization
  removed most of the slice-count signal (slice-count-only held-out macro-AUC 0.853 to 0.678) without a
  measurable change in held-out performance (CNN + radiomics 0.934 vs. 0.952; difference −0.018,
  −0.061 to 0.024). It did not improve external discrimination (MCT-LTDiag CNN + radiomics 0.510 vs.
  0.578, paired p = 0.17; radiomics 0.474 vs. 0.655, p < 0.001), and the equalized models assigned
  almost every MCT-LTDiag patient to cHCC-CCA. A non-contrast series made thick before equalization
  still raised the equalized CNN's cHCC-CCA probability (+0.087, 0.067 to 0.107), so resampling does not
  remove the blur of a thick reconstruction.
- Notebook 30: fully nested evaluation of the stacked fusions. In each of the five repeated
  cross-validations, an inner four-fold cross-validation inside every outer fold (100 CNN trainings)
  produces the meta-learners' training inputs. The non-nested estimates were not optimistic: nested
  out-of-fold macro-AUC 0.948 vs. 0.942 for CNN + radiomics (difference −0.006, range −0.008 to
  −0.002), and CNN + radiomics stayed above both branches in all five repeats.
- Nine cohort-level tables (`equalized_density_*.csv`, `nested_stacking_*.csv`); the export script
  reproduces the existing 35 tables unchanged.
- Tests that lock the new headline values; package, citation, and manifest versions set to 2.2.0.

## 2.1.3 — 2026-10-20

Figures brought to the figure rules of the journal. No analysis, table, or value changed.

### Changed

- Every figure is drawn at the printed width of 16.5 cm with black labels of 8–11 pt in sentence
  case and italic *p*. `make_revision_figures.py` checks these rules on each figure and stops with a
  list of the labels that break them. Each figure is also written as a 600 dpi TIFF.
- Figure 1 redesigned: cohorts and data partition, model pipeline, and evaluation. The manuscript
  version shows the CT crops and radiomic features of one patient and is not published, like Figures
  2, 6, and 8. The copy published here (`--figures design_public`) has schematic tiles and a
  schematic feature strip instead.
- Figures 3, 4, 5, and 7: same data and values; titles, labels, and legends shortened or moved so that
  they fit the printed width at 8 pt, and the value labels of Figure 3A give the point estimates only.

## 2.1.2 — 2026-10-20

Reproducibility documentation only; no code, result, or figure changed.

### Added

- The exact package versions recorded by every revision run, including the PyRadiomics build: a
  development build, 3.1.1.dev111 (commit `8ed579383b44806651c463d5e691f3b2b57522ab`), installed from
  GitHub because the notebooks fall back to the master branch. The pinned install command is in the
  [environment](docs/environment.md) page.
- A determinism section in [reproducibility](docs/reproducibility.md): cropping, radiomics, and the
  fusion and statistics steps reproduce exactly; CNN inference from the saved checkpoints reproduces
  within 10⁻³; CNN retraining is seeded but not bit-exact on a GPU, and its run-to-run variation was
  not measured.

## 2.1.1 — 2026-10-20

Documentation and figure corrections from a consistency check of the paper, code, and results. No analysis,
table, or headline value changed.

### Changed

- Figure 7: the phase-dropout CNN reference in panel C now uses the same run as Table 5 (0.528, 0.448–0.607);
  the mitigation run had recomputed the same predictions (largest difference about 1e-4), which moved the
  upper bound across a rounding boundary (0.608). `make_revision_figures.py` reproduces the published figures
  pixel for pixel.
- Figure 6 (private): the axis label no longer says n = 278, because each condition uses the patients of the
  classes concerned.
- Model card: the range of external calibration intercepts is −0.87 to −2.02 for the models in the table
  (−2.06 belonged to a fusion with the original CNN that is not shown).
- Dataset documentation: collection periods, institutions, and basis of diagnosis from the source
  publications; the PLC-CECT curators kept only the slices containing liver, which supports the
  slice-thickness reading of the dataset audit; the three patients with unresolved sex also have no recorded
  age, and the meta-learners treat both as missing; the HCC-TACE-Seg dataset DOI (10.7937/TCIA.5FNA-0924),
  and MCT-LTDiag added to the data access notes.

## 2.1.0 — 2026-10-20

Analyses added after a second check of the revision, before resubmission.

### Added

- Notebook 28: corrected-mask sensitivity analysis. Each phase is masked by the union of the liver and
  tumor masks instead of the liver mask, so tumor tissue outside the released liver mask is kept; the
  CNN, radiomics, and both fusions are retrained with the same folds, seeds, and settings. No conclusion
  changed: CNN + radiomics 0.963 held-out (main 0.952), the CNN still uses the non-contrast artifact, and
  MCT-LTDiag 0.571 (main 0.578; paired p = 0.83).
- Within-sex external comparison (post hoc): the full-fusion advantage on MCT-LTDiag disappears within
  men and within women, so it comes from sex.
- Eight cohort-level tables (`corrected_mask_*.csv`, `external_mct_ltdiag_by_sex.csv`), produced by the
  extended `export_revision_aggregates.py`, which reproduces the existing 27 tables unchanged and now
  writes Unix line endings on every platform.
- Tests that lock the corrected-mask and within-sex headline values.

### Changed

- External specificity is reported as the share of ICC patients not called HCC (for example 0.52 for
  CNN + radiomics), with Brier scores; the earlier "ICC specificity" was the share called ICC.
- Wording matched to the evidence: slice thickness is inferred from slice counts, and the sex
  explanation is backed by the within-sex result.

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
