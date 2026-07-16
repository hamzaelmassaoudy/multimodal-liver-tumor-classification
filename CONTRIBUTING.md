# Contributing

Contributions should preserve the scientific definitions, privacy boundary, and aggregate-only release design of this repository.

## Development setup

Use Python 3.10 or later in an isolated environment:

```bash
python -m pip install -e ".[test]"
python -m pytest
ruff check .
python scripts/validate_release.py .
```

The test and validation workflows use synthetic inputs and released aggregates. They must not require patient data, model training, cloud authentication, or private checkpoints.

## Scientific invariants

Changes must retain unless supported by a separately reviewed study:

- Class order HCC, ICC, cHCC-CCA.
- Phase order P, C1, C2, C3.
- Historical independent phase-specific tumor-centroid cropping to `96 x 96 x 96`.
- No claim of explicit registration or voxelwise phase correspondence.
- Crop-restricted radiomics terminology and C2-only retention scope.
- W3 exclusion from the eight-feature full-fusion vector.
- Corrected nine-comparison DeLong interpretation.
- Clear separation of historical sex=0 and locked-median sex=1 external scenarios.

Proposed registration, physical-space alignment, or adaptive-crop methods must be identified as new research and must not replace the provenance of existing results.

## Privacy and files

Never submit patient images, masks, identifiers, clinical rows, splits, predictions, feature matrices, private paths, credentials, authentication output, manuscript files, or unpublished checkpoints. Tests must use clearly synthetic arrays. Public result additions must be aggregate, documented in `docs/results_provenance.md`, and supported by verifiable scientific evidence.

## Change quality

Before submitting a change:

1. Run the unit tests, lint check, aggregate validation, and release validation.
2. Confirm that notebooks have no outputs or execution counts.
3. Check all relative Markdown links.
4. Explain the scientific source for any changed number or method statement.
5. Keep commits neutral and focused.

No general reuse license is granted solely by public availability of this repository. Contribution acceptance and licensing remain subject to explicit author agreement.
