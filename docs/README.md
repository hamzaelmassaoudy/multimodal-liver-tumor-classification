# Documentation

For a first run, follow the [quick start](quickstart.md). It needs no patient data.
The [synthetic fusion example](../examples/synthetic_fusion.py) shows the input contract
and the order of training-fold imputation and feature construction.

## Running the software

| Guide | What it covers |
|---|---|
| [Quick start](quickstart.md) | Installation, commands, expected output, and common setup errors. |
| [Software environment](environment.md) | Versions used for public-tools checks and the separate historical environment limit. |
| [Reproducibility](reproducibility.md) | Analyses supported by the release and what prevents exact reconstruction. |
| [Dataset access](datasets.md) | Cohorts, provider links, and local configuration. |
| [Artifact contracts](artifact_contracts.md) | Required schemas for authorized local inputs. |
| [Notebook sequence](../notebooks/README.md) | The fourteen workflow notebooks and their prerequisites. |

## Understanding the study

| Guide | What it covers |
|---|---|
| [Scientific scope](scientific_scope.md) | Research question, cohort design, and interpretation. |
| [Preprocessing](preprocessing.md) | Independent phase cropping, C2 retention, and radiomics geometry. |
| [Model architecture](model_architecture.md) | W3, W4, W5, clinical, and fusion branches. |
| [Fusion definition](fusion_definition.md) | Class order, eight inputs, and missing clinical values. |
| [External stress test](external_stress_test.md) | HCC-only results, clinical assumptions, adapter QC, and radiomics controls. |
| [Model card](model_card.md) | Intended use, performance, and limitations in one place. |

## Inspecting the release

[Results provenance](results_provenance.md) is the reference for aggregate values and
the missing-sex correction. [Released tables](../results/README.md) and
[aggregate figures](../results/figures/README.md) describe the files.
[Analysis alignment](manuscript_repository_alignment.md) summarizes the released method
and result definitions. [Privacy and data boundaries](privacy_and_data_boundary.md)
describe what can be shared. [Contributing](../CONTRIBUTING.md) lists the checks required
for changes, and the [changelog](../CHANGELOG.md) records repository updates.
