# Datasets

## Internal cohort: PLC-CECT V4

The Primary Liver Cancer CECT Imaging Dataset, PLC-CECT V4, supplied the internal cohort. The analyzed release contained four CT phases (P, C1, C2, and C3) for 278 patients:

| Class | Patients |
|---|---:|
| HCC | 94 |
| ICC | 99 |
| cHCC-CCA | 85 |
| Total | 278 |

The study used 222 development patients and 56 held-out internal evaluation patients. Five patient-level stratified folds were defined inside the development cohort. The repository does not distribute the patient-level manifest or split membership.

Dataset access and its current terms are provided by the [Science Data Bank record](https://doi.org/10.57760/sciencedb.12207). Users must obtain the release directly from its custodian and comply with the dataset license and access conditions.

## External cohort: HCC-TACE-Seg

The external source was [HCC-TACE-Seg at The Cancer Imaging Archive](https://www.cancerimagingarchive.net/collection/hcc-tace-seg/). The study retained 103 known-HCC patients after applying the historical external workflow. No retained patient had all four phases required by the internal multiphase input.

This cohort supported an HCC-only stress test. It did not support external discrimination among HCC, ICC, and cHCC-CCA, so external multiclass AUC is neither defined nor reported.

## Data responsibility

This repository contains no raw or processed patient imaging, masks, DICOM or NIfTI volumes, clinical rows, patient-level predictions, or split files. Public availability at the source does not authorize redistribution here. Users are responsible for source access, data governance, de-identification, local storage, and compliance with applicable terms.

Local dataset roots are supplied through environment variables documented in [`configs/paths.example.yaml`](../configs/paths.example.yaml). A private `configs/paths.yaml` may be created locally and is ignored by Git. See [privacy and data boundary](privacy_and_data_boundary.md).
