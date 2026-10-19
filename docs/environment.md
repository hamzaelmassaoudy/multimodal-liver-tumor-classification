# Software environment

The public analysis tools and the historical imaging workflow have different environment
requirements. Installing the tools does not reconstruct the training environment.

## Public-tools check environment

Local checks use Python 3.12.14 on Windows with the dependency versions below. The
[constraint file](../configs/public-tools-py312.txt) records this environment so the
public commands can be rerun with the same package versions.

| Package | Version |
|---|---:|
| NumPy | 2.2.6 |
| pandas | 2.3.3 |
| scikit-learn | 1.9.1 |
| SciPy | 1.18.1 |
| PyYAML | 6.0.3 |
| pytest | 8.4.2 |
| Ruff | 0.17.0 |

Build tools are separate from runtime dependencies. The package requires Python 3.10
or newer; its broader dependency ranges are declared in [pyproject.toml](../pyproject.toml).
CI is configured to check Python 3.10 and 3.12 on Linux, and Python 3.12 on Windows.
The live [Actions page](https://github.com/hamzaelmassaoudy/multimodal-liver-tumor-classification/actions)
is the source for hosted run status.

To use the recorded dependencies with Python 3.12:

```bash
python -m pip install -e ".[test]" -c configs/public-tools-py312.txt
```

Checks cover tests, lint and formatting, the synthetic example, smoke testing,
aggregate consistency, DeLong adjustments, and release validation. They do not
include CNN training, full imaging preprocessing, or clinical validation.

## Historical workflow

Exact historical versions were not preserved for every imaging and modeling component.
The `workflow` extra supplies dependency ranges for inspecting and running supported
notebooks with authorized local inputs. It is not a historical lock file, and newly
installed versions may produce different numerical outputs. Private checkpoints and the
missing physical geometry impose additional [reconstruction limits](reproducibility.md).

## Revision environment

The revision notebooks ran on Google Colab with Python 3.13, PyTorch 2.11, MONAI 1.6.1,
PyRadiomics 3.1.1, LightGBM 4.6.0, and scikit-learn 1.6.1, with an NVIDIA A100 or L4 GPU for
the CNN analyses.

The revision scripts need the `revision` extra (`python -m pip install -e ".[revision]"`).
With matplotlib 3.9.2, `make_revision_figures.py` reproduces the published figures pixel for
pixel; other matplotlib versions can differ slightly in font rendering.
