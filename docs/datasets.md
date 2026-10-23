# Datasets

## Internal cohort: PLC-CECT V4

The Primary Liver Cancer CECT Imaging Dataset, PLC-CECT V4, supplied the internal cohort. The analyzed release contained four CT phases (P, C1, C2, and C3) for 278 patients:

| Class | Patients |
|---|---:|
| HCC | 94 |
| ICC | 99 |
| cHCC-CCA | 85 |
| Total | 278 |

According to the source publication (Luo et al., *Sci Data* 2025), the scans were acquired between January 2015
and December 2022 at Chongqing Yubei District People's Hospital, China, diagnoses were confirmed histologically or
cytologically, and the curators kept only the slices containing liver, clipped intensities to −200…200 HU, and
rescaled them to 0–255. For three patients, sex is unresolved and age is not recorded; the analysis treats both as
missing (see the [fusion definition](fusion_definition.md)).

The study used 222 development patients and 56 held-out internal evaluation patients. Five patient-level stratified folds were defined inside the development cohort. The repository does not distribute the patient-level manifest or split membership.

Dataset access and its current terms are provided by the [Science Data Bank record](https://doi.org/10.57760/sciencedb.12207). Users must obtain the release directly from its custodian and comply with the dataset license and access conditions.

The [dataset audit](plc_cect_dataset_audit.md) found that acquisition differs by class in this
release (slice counts, slice spacing, storage format). Read it before training on PLC-CECT.

## External cohort: MCT-LTDiag

MCT-LTDiag (Peking Union Medical College Hospital; scans acquired between August 2014 and January 2024;
pathological or clinical diagnoses) is available from
[Harvard Dataverse](https://doi.org/10.7910/DVN/S3RW15); the revision used version 3.1 (CC0).
It has no cHCC-CCA class, so the revision used all 103 HCC and 100 ICC patients for
HCC-versus-ICC validation. The four phases are registered to the portal-venous phase, every
scan has 5 mm slices, and age and sex are recorded for every patient. Notebook 18 downloads
the cases and checks each file against its published checksum.

## Stress-test cohort: HCC-TACE-Seg

The external source was [HCC-TACE-Seg at The Cancer Imaging Archive](https://doi.org/10.7937/TCIA.5FNA-0924): 105 patients with confirmed HCC
treated at The University of Texas MD Anderson Cancer Center between 2002 and 2012. The study retained 103 known-HCC patients after applying the historical external workflow. No retained patient had all four phases required by the internal multiphase input.

This cohort supported an HCC-only stress test. It did not support external discrimination among HCC, ICC, and cHCC-CCA, so external multiclass AUC is neither defined nor reported.

TCIA also lists a separate clinical XLSX download, including demographic data, on the
[collection page](https://www.cancerimagingarchive.net/collection/hcc-tace-seg/).
Age and sex were not available in the artifacts used for the v1.1.0 external analysis. The
October 2026 revision linked the TCIA clinical workbook to all 103 retained cases, observed
age and sex for 103 of 103, and used them in the
[revised external analysis](external_validation_mct_ltdiag.md).

## Data responsibility

This repository contains no raw or processed patient imaging, masks, DICOM or NIfTI volumes, clinical rows, patient-level predictions, or split files. Public availability at the source does not authorize redistribution here. Users are responsible for source access, data governance, de-identification, local storage, and compliance with applicable terms.

Local dataset roots are supplied through environment variables documented in [`configs/paths.example.yaml`](../configs/paths.example.yaml). A private `configs/paths.yaml` may be created locally and is ignored by Git. See [privacy and data boundary](privacy_and_data_boundary.md).
