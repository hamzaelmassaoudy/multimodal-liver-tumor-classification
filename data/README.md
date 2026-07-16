# Data access and local configuration

No patient data are distributed in this repository.

## Source datasets

- **PLC-CECT V4:** obtain the Primary Liver Cancer CECT Imaging Dataset from its [Science Data Bank record](https://doi.org/10.57760/sciencedb.12207).
- **HCC-TACE-Seg:** obtain the external collection from [The Cancer Imaging Archive](https://www.cancerimagingarchive.net/collection/hcc-tace-seg/).

Review and follow the current source terms before download or use. Data being publicly obtainable from a custodian does not authorize redistribution through this software repository.

## Local paths

Dataset and private-artifact roots are configured with the environment variables referenced in [`configs/paths.example.yaml`](../configs/paths.example.yaml):

- `PLC_CECT_ROOT`
- `HCC_TACE_SEG_ROOT`
- `PRIVATE_ARTIFACT_ROOT`
- `OUTPUT_ROOT`

Create a local `configs/paths.yaml` from the provided example, set the variables in the execution environment, and keep the local file untracked. The configuration loader reports a clear error when a required variable or path is unavailable.

## Public/private boundary

Do not add raw CT, processed arrays, masks, DICOM metadata, NIfTI or NPZ volumes, clinical spreadsheets, identifiers, split files, feature matrices, or patient-level predictions to this directory. Use only authorized local storage governed by the applicable dataset terms and institutional requirements.

The repository's released `results/aggregate` files contain cohort-level statistics only. See [dataset documentation](../docs/datasets.md) and [privacy boundary](../docs/privacy_and_data_boundary.md).
