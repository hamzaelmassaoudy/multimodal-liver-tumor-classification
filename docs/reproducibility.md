# Reproducibility and auditability

This release separates public aggregate verification from workflows requiring user-obtained data
or authorized local derived artifacts.

## Supported from a public clone

- Validate corrected aggregate schemas and scientific invariants.
- Verify exact-value nine-test DeLong adjustments.
- Inspect independent phase-centering and zero-padding logic.
- Exercise preprocessing, fusion, metrics, external scenarios, and safety logic on synthetic data.
- Review corrected internal performance, sex provenance/sensitivity, per-class results, paired tests,
  confusion counts, C2 retention, external adapter QC, and radiomics feature-handling controls.
- Review the [October 2026 revision](revision_2026-10.md) tables and figures in
  `results/revision_2026-10` and the code of revision notebooks 15–28.

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
class weights, the whole pipeline was retrained in 5 × 5 repeated cross-validation, and
Harrell's bootstrap estimated the optimism of both fusions (0.007). See the
[revision overview](revision_2026-10.md).

## Configuration

Copy `configs/paths.example.yaml` to ignored `configs/paths.yaml`, set the documented environment
variables, and keep that file outside version control. See [artifact contracts](artifact_contracts.md).
