# Reproducibility and auditability

This release provides a modular and independently auditable analysis framework within the limits of retained artifacts. It separates public aggregate reanalysis from workflows that require user-obtained datasets or authorized private derived artifacts.

## Supported from a public clone

- Validate released aggregate schemas and scientific invariants.
- Recalculate the nine-test Bonferroni and Benjamini-Hochberg adjustments from released raw DeLong p-values.
- Inspect the verified independent phase-centering and zero-padding implementation.
- Exercise preprocessing, fusion, probability, metric, external-scenario, and release-safety logic on synthetic data.
- Review aggregate internal performance, C2 crop retention, external sex scenarios, and radiomics imputation controls.

After installing the package and test dependencies, run:

```bash
python -m pytest
ruff check .
python scripts/validate_aggregate_results.py
python scripts/validate_release.py .
```

These checks do not require patient data and do not train a model.

## Requires user-obtained data

Dataset preprocessing and model workflow notebooks require users to obtain PLC-CECT V4 or HCC-TACE-Seg from their official custodians and configure local roots. Source datasets are not redistributed. Access routes and responsibilities are documented in [datasets](datasets.md) and [`data/README.md`](../data/README.md).

## Requires authorized local artifacts

Aggregate metric recalculation from saved predictions, the C2 retention audit, and the external sex-scenario aggregation require patient-level or derived inputs that are intentionally not published. The scripts validate and summarize user-supplied local files without authorizing their distribution.

## Exact reconstruction limits

- The historical W3 fold 1 checkpoint was not retained.
- The historical W4 fold 0 checkpoint was not retained.
- Original internal source geometry was not retained with the processed arrays.
- Historical phase-specific crop coordinates were not retained.
- Patient-level splits, predictions, clinical rows, and derived imaging artifacts remain private.
- Exact historical package versions are not available for every dependency; compatible ranges are provided for the released utilities.

Consequently, saved-prediction metric reanalysis and scientific workflow inspection are supported, while exact all-fold CNN inference and exact end-to-end reconstruction are not.

## Cross-validation limitations

CNN checkpoints were selected using the outer validation folds that also produced OOF predictions. CNN class weights were calculated from labels across the complete 222-patient development cohort. These choices can make cross-validation and stacking estimates optimistic. They are not patient leakage and did not involve the independent 56-patient held-out evaluation set. Interpretation should emphasize held-out internal performance.

## Configuration

Copy `configs/paths.example.yaml` to the ignored local path `configs/paths.yaml`, set the documented environment variables, and keep that file outside version control. The loader fails clearly when required variables or inputs are unavailable. See [`paths.example.yaml`](../configs/paths.example.yaml) and [artifact contracts](artifact_contracts.md).
