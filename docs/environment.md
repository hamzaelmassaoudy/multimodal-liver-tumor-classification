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

The revision notebooks ran on Google Colab, with an NVIDIA A100 or L4 GPU for the CNN analyses.
Each run saved its package versions in its private `summary.json`, and all runs recorded the same
versions:

| Package | Version |
|---|---|
| Python | 3.13.15 (3.13.16 in notebook 22, which ran on the CPU only) |
| PyTorch | 2.11.0, CUDA 13.0 build |
| MONAI | 1.6.1 |
| scikit-learn | 1.6.1 |
| LightGBM | 4.6.0 |
| NumPy | 2.1.3 |
| SimpleITK | 2.5.6 |
| pydicom | 3.0.2 |
| PyRadiomics | 3.1.1.dev111, a development build (commit `8ed579383`) |

PyRadiomics was not a released version. The notebooks install it from PyPI and, if that fails,
from the master branch on GitHub; every run that extracted features recorded the development build
3.1.1.dev111, which is 111 commits after v3.1.0 (commit `8ed579383b44806651c463d5e691f3b2b57522ab`, 16 June 2025).
Because the fallback installs whatever the master branch holds at the time, a later run could get
a different build. To install the exact build:

```bash
python -m pip install "pyradiomics @ git+https://github.com/AIM-Harvard/pyradiomics.git@8ed579383b44806651c463d5e691f3b2b57522ab"
```

Features re-extracted with this build matched the features of the original analysis to within
10⁻¹⁵ (largest relative difference; notebooks 26 and 28), so the radiomics results do not depend
on the build. See [reproducibility](reproducibility.md) for which steps reproduce exactly.

The revision scripts need the `revision` extra (`python -m pip install -e ".[revision]"`).
With matplotlib 3.9.2, `make_revision_figures.py` reproduces the published figures pixel for
pixel; other matplotlib versions can differ slightly in font rendering.
