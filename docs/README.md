# Documentation

For a first run, follow the [quick start](quickstart.md). It needs no patient data.
The [synthetic fusion example](../examples/synthetic_fusion.py) shows the input contract
and the order of training-fold imputation and feature construction.

## Revision (v2.0.0–2.2.1)

| Guide | What it covers |
|---|---|
| [Revision overview](revision_2026-10.md) | What changed from v1.1.0, internal results, and corrections to earlier statements. |
| [PLC-CECT dataset audit](plc_cect_dataset_audit.md) | Class-dependent acquisition, the counterfactual test, and advice for PLC-CECT users. |
| [External validation](external_validation_mct_ltdiag.md) | MCT-LTDiag validation, mitigation attempts, and the HCC-TACE-Seg stress test. |
| [Revision notebooks](revision_notebooks.md) | Notebooks 15–30, their safeguards, and their environment variables. |

## Running the software

| Guide | What it covers |
|---|---|
| [Quick start](quickstart.md) | Installation, commands, expected output, and common setup errors. |
| [Software environment](environment.md) | Versions used for public-tools checks, the historical workflow, and the revision. |
| [Reproducibility](reproducibility.md) | Analyses supported by the release and what prevents exact reconstruction. |
| [Dataset access](datasets.md) | Cohorts, provider links, and local configuration. |
| [Artifact contracts](artifact_contracts.md) | Required schemas for authorized local inputs. |
| [Notebook sequence](../notebooks/README.md) | All 28 notebooks and their prerequisites. |

## Understanding the study

| Guide | What it covers |
|---|---|
| [Scientific scope](scientific_scope.md) | Research questions, cohort design, and interpretation. |
| [Model card](model_card.md) | Intended use, performance, and limitations of the revised models. |
| [Preprocessing](preprocessing.md) | Independent phase cropping, C2 retention, and radiomics geometry. |
| [Model architecture](model_architecture.md) | W3, W4, W5, clinical, fusion, and the revised models. |
| [Fusion definition](fusion_definition.md) | Class order, eight inputs, and missing clinical values (v1.1.0). |
| [External stress test](external_stress_test.md) | The submitted HCC-only analysis (v1.1.0). |

## Inspecting the release

[Results provenance](results_provenance.md) is the reference for aggregate values and
the missing-sex correction. [Released tables](../results/README.md) and
[aggregate figures](../results/figures/README.md) describe the files.
[Analysis alignment](manuscript_repository_alignment.md) summarizes the method and result
definitions of the submitted analysis. [Privacy and data boundaries](privacy_and_data_boundary.md)
describe what can be shared. [Contributing](../CONTRIBUTING.md) lists the checks required
for changes, and the [changelog](../CHANGELOG.md) records repository updates.

Pages marked with a version note describe the analysis as submitted (v1.1.0); the revision pages
above describe the current analysis.
