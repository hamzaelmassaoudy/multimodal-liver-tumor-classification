# Contributing

Contributions must preserve the scientific definitions, privacy boundary, and aggregate-only
release design of this repository.

## Development setup

Use Python 3.10 or later in an isolated environment:

```bash
python -m pip install -e ".[test]"
python -m pytest
python -m ruff check src scripts tests
python -m ruff format --check src scripts tests
python scripts/smoke_test.py
python scripts/validate_release.py .
```

The test and validation workflows use synthetic inputs and released aggregates. They must not
require patient data, model training, cloud authentication, or private checkpoints.

## Scientific invariants

Changes must retain these definitions unless supported by a separately reviewed study:

- Class order HCC, ICC, cHCC-CCA.
- Phase order P, C1, C2, C3.
- Independent phase-specific lesion-centered cropping to `96 x 96 x 96`.
- No claim of explicit registration or voxelwise phase correspondence.
- Crop-restricted radiomics terminology and C2-only retention scope.
- Unit-spacing limitation for historical radiomics shape outputs.
- W3 exclusion from the exact eight-feature full-fusion vector.
- Unresolved internal sex retained as missing for the corrected primary analysis.
- Historical non-male-to-zero encoding identified only as a sensitivity analysis.
- Corrected nine-comparison DeLong values and adjustment family.
- Corrected missing-sex fold-median external scenario identified as model-defined primary.
- Condition C identified as an internal diagnostic refit, not frozen external validation.

Proposed registration, physical-space alignment, or adaptive-crop methods are new research and
must not replace the provenance of existing results.

## Privacy and files

Never submit patient images, masks, identifiers, clinical rows, splits, predictions, feature
matrices, private paths, credentials, authentication output, manuscript files, or unpublished
checkpoints. Tests must use clearly synthetic arrays. Public result additions must be aggregate,
documented in `docs/results_provenance.md`, and supported by verifiable scientific evidence.

## Change quality

Before submitting a change:

1. Run unit tests, lint, aggregate validation, and release validation.
2. Confirm notebooks have no outputs or execution counts.
3. Check every relative Markdown link.
4. Explain the scientific source for any changed number or method statement.
5. Keep commits neutral and focused.

By contributing, you agree that accepted contributions are distributed under the repository’s
[MIT License](LICENSE).
