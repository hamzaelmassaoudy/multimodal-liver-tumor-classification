# Reproducibility and auditability

This release separates public aggregate verification from workflows requiring user-obtained data
or authorized local derived artifacts.

## Supported from a public clone

- Validate the schemas and scientific invariants of the submitted-analysis tables in `results/aggregate`
  (`scripts/validate_aggregate_results.py`).
- Check the revision tables in `results/revision_2026-10`, including `manuscript_values.csv`, against
  the values reported in the revised manuscript (`tests/test_revision_results.py`).
- Verify exact-value nine-test DeLong adjustments.
- Inspect independent phase-centering and zero-padding logic.
- Exercise preprocessing, fusion, metrics, external scenarios, and safety logic on synthetic data.
- Review corrected internal performance, sex provenance/sensitivity, per-class results, paired tests,
  confusion counts, C2 retention, external adapter QC, and radiomics feature-handling controls.
- Review the [October 2026 revision](revision_2026-10.md) tables and figures in
  `results/revision_2026-10`, the code of revision notebooks 15–33, and the
  [analysis plans](analysis_plans.md).

```bash
python -m pytest
python -m ruff check src scripts examples tests
python -m ruff format --check src scripts examples tests
python scripts/smoke_test.py
python scripts/validate_aggregate_results.py
python scripts/validate_release.py .
```

These checks neither require patient data nor train a model.

## Requires user-obtained data or authorized local artifacts

Dataset preprocessing and model notebooks require users to obtain PLC-CECT V4, MCT-LTDiag, or
HCC-TACE-Seg from their custodians. Patient-linked metric recalculation, the C2 retention audit, and external
scenario aggregation require private local artifacts. Those inputs must not be committed.

## Exact reconstruction limits

- Fold checkpoints are retained privately and are not distributed. (v1.1.0 stated that the
  W3 fold 1 and W4 fold 0 checkpoints were not retained; that was wrong. All five folds of both
  CNNs exist, and the revision reproduced their saved predictions.)
- The released PLC-CECT files store a nominal 1 mm spacing, so physical voxel geometry cannot
  be recovered.
- Historical phase-specific crop coordinates were not saved. The revision recomputed the crops
  from the released dataset, and they matched the original crops for 278 of 278 patients.
- Patient-level splits, predictions, clinical rows, and imaging artifacts remain private.
- Exact historical package versions are unavailable for every dependency.

The public release supports aggregate checks and workflow inspection. Rerunning CNN inference
needs the private checkpoints and the source images, so exact end-to-end reconstruction is not
possible from a public clone.

## Determinism of the revision runs

- **Reproduced exactly:** cropping, radiomics extraction, the LightGBM radiomics models, the
  logistic fusions, and the statistics. The revision notebooks start with checks against saved
  results and stop on any mismatch. Notebook 15 reproduced all 75 submitted values,
  including the fusion results and the DeLong tests (largest difference 1.1 × 10⁻¹⁶); rebuilt
  crops matched the original crops for 278 of 278 internal patients (notebooks 26 and 28) and
  the MCT-LTDiag crops for 203 of 203 (notebook 28); re-extracted features matched within 10⁻¹⁵;
  and retrained radiomics models reproduced the saved predictions within 10⁻¹⁶.
- **CNN predictions from the saved checkpoints:** below 10⁻³ of the saved probabilities (largest
  difference 6.1 × 10⁻⁴, notebook 16), and the AUCs checked were unchanged. The small differences
  come from GPU arithmetic.
- **CNN retraining is not bit-exact.** Training fixes the random seeds but does not enable
  PyTorch's deterministic algorithms, and notebooks 03, 04, and 16 also enable cuDNN autotuning
  (`torch.backends.cudnn.benchmark = True`). Retraining on a GPU therefore gives close but not
  bit-identical weights and predictions. Notebook 33 measured this variation; its training code seeds the
  data-loader workers and does not use cuDNN autotuning, unlike notebook 16, so retraining the main
  CNN with its own seed (held-out macro-AUC −0.003, CNN + radiomics −0.001; out-of-fold CNN −0.019)
  shows retraining variation rather than GPU arithmetic alone, and over
  six training seeds the held-out macro-AUC was 0.910 ± 0.009 for the CNN and 0.947 ± 0.003 for
  CNN + radiomics. (The repeated cross-validation of notebook 23 shows how much the results vary
  with different folds.)
- **Package versions:** see the [environment](environment.md), including the exact PyRadiomics
  build.

## Corrected analysis boundary

The missing-sex correction refitted only internal clinical and fusion logistic regressions after
retaining three unresolved sex entries as missing. It did not retrain W3, W4, W5, any CNN,
radiomics extractor, or LightGBM model. The primary and frozen external pathways performed no
fitting or tuning. Condition C
separately refitted radiomics classifiers on internal development data using an externally
defined, label-free feature-availability subset; see the [external controls](external_stress_test.md).

The released adapter audit records C2 fallback in 102/103 external patients. The
nonfallback group contains one patient, so no comparative effect is inferred.

## Cross-validation limitations

CNN checkpoints were selected using outer validation folds that also produced OOF predictions.
CNN class weights used labels across all 222 development patients. In addition, the upstream
OOF models were not refitted inside each downstream stacking-validation split. These dependencies
can make CV and stacking estimates optimistic. An unbiased estimate of the full fitting procedure
would require nesting upstream fitting and model selection within each evaluation split. The
56-patient held-out evaluation set did not enter these development procedures.

The revision addressed these points: the main CNN uses an inner validation split and per-fold
class weights, the pipeline was run in 5 × 5 repeated cross-validation (repeat 0 with the saved models,
repeats 1–4 retrained on new folds), and
Harrell's bootstrap estimated the optimism of both fusions (0.007). Notebook 30 then nested the
stacking step: in every outer fold of the five repeats, the meta-learners were fitted only on
predictions of base models trained without that fold. The nested out-of-fold macro-AUC was slightly
higher than the non-nested one (CNN + radiomics 0.948 vs. 0.942), so the non-nested estimates were
not optimistic. The choice of the main CNN, made after its internal results were known, is not
nested. See the [revision overview](revision_2026-10.md).

## Configuration

Copy `configs/paths.example.yaml` to ignored `configs/paths.yaml`, set the documented environment
variables, and keep that file outside version control. See [artifact contracts](artifact_contracts.md).
