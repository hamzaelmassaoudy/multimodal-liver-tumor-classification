# Quick start

These steps run public aggregate checks and synthetic examples. No patient data, private
checkpoints, imaging packages, GPU, or cloud account is required.

## Clone and create an environment

Use Python 3.10 or newer and Git. Run:

```bash
git clone https://github.com/hamzaelmassaoudy/multimodal-liver-tumor-classification.git
cd multimodal-liver-tumor-classification
python -m venv .venv
```

Activate the environment in your shell.

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

If local policy prevents activation, use `.\.venv\Scripts\python.exe` in place of
`python` in the remaining commands. Activation is optional; no policy change is needed.

**macOS/Linux:**

```bash
source .venv/bin/activate
```

Install the package and its check tools from the repository root:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
```

For the recorded Python 3.12 dependency versions, add the constraint file:

```bash
python -m pip install -e ".[test]" -c configs/public-tools-py312.txt
```

See [environment details](environment.md) for the scope of this version record.

## First run

```bash
python scripts/smoke_test.py
python examples/synthetic_fusion.py
```

The smoke test ends with:

```text
Public-clone smoke test passed: release validation, independent-phase preprocessing, and eight-feature fusion.
```

The synthetic example ends with:

```text
Synthetic example only; no patient data or study performance is used.
Training-fold clinical medians (age, sex): [55.0, 1.0]
Training feature matrix: (6, 8)
Evaluation feature matrix: (2, 8)
Feature order: w4_p_HCC, w4_p_ICC, w4_p_CHCC, w5_p_HCC, w5_p_ICC, w5_p_CHCC, age, sex
```

The imputer is fitted on six synthetic training rows and reused for two synthetic
evaluation rows. Each real training fold would need its own fitted imputer. The example
constructs features only; it does not train a classifier or reproduce the reported AUC.

## Check the release

```bash
python -m pytest -q
python -m ruff check src scripts examples tests
python -m ruff format --check src scripts examples tests
python scripts/validate_aggregate_results.py
python scripts/recalculate_delong_summary.py results/aggregate/delong_summary.csv
python scripts/validate_release.py
```

Tests should finish with no failures. Aggregate and release commands print
`Aggregate result validation passed.` and `Release validation passed.` respectively.
The DeLong command recalculates adjustments from the released p-values; it does not
recalculate raw tests from private prediction rows.

## Imaging workflows

Install `python -m pip install -e ".[workflow]"` only for notebooks that need imaging
or model libraries. Obtain datasets from their providers, configure private paths as
specified in the [dataset guide](datasets.md), then follow the
[notebook sequence](../notebooks/README.md). Patient-linked outputs belong outside Git.
CNN inference also needs the private fold checkpoints, which are not distributed. See
[reproducibility](reproducibility.md). The revision scripts in `scripts/revision` need
`python -m pip install -e ".[revision]"`.

## Common setup errors

| Symptom | Resolution |
|---|---|
| `No module named liver_tumor_pipeline` | Use the active environment's Python and run `python -m pip install -e ".[test]"` from the repository root. |
| A script or result file cannot be found | Run the documented commands from the cloned repository root. |
| Notebook reports missing inputs | Check its prerequisites and local path configuration; public checks do not need those inputs. |
| Imaging dependency installation fails | First check the public tools without `.[workflow]`; imaging libraries have separate platform requirements. |
