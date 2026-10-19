# Model architecture

## Study conventions

- Class order: HCC, ICC, cHCC-CCA.
- Phase order: P, C1, C2, C3.
- Crop size: `96 x 96 x 96` voxels.

The compatibility token `CHCC` denotes cHCC-CCA.

## W3: single-phase CNN

W3 used portal-venous C2 only with input shape `1 x 96 x 96 x 96`. It was a randomly
initialized MONAI 3D ResNet-18 and served only as a comparator.

## W4: multiphase CNN

W4 used P/C1/C2/C3 channels with input shape `4 x 96 x 96 x 96`. Each channel was
independently centered on its own phase-specific tumor-mask centroid. Joint flips of the stacked
crops during augmentation do not imply source-phase registration.

## W5: radiomics-LightGBM

W5 extracted original-image PyRadiomics features from the tumor retained inside each crop. Enabled
classes were shape, first-order, GLCM, GLRLM, GLSZM, GLDM, and NGTDM. There were 107 features
per phase and 428 candidates per patient, followed by fold-specific selection and LightGBM.

Cached arrays lacked source geometry and spacing. SimpleITK conversion used unit spacing, so shape
outputs are crop-grid descriptors rather than verified physical-unit measurements. Crop truncation
also means W5 is crop-restricted rather than guaranteed complete-lesion radiomics.

## Clinical and fusion models

The clinical baseline used age and sex. Corrected primary models retained unresolved sex as missing
and used fold-local median imputation. Full fusion used W4 and W5 probability triplets plus age and
sex. W3 was excluded. See [fusion definition](fusion_definition.md).

## Revised models (v2.0.0)

The October 2026 revision kept the W4 architecture and input but retrained it with phase
dropout (random phases zeroed during training), an inner validation split for checkpoint
choice, and per-fold class weights. This phase-dropout CNN is the main CNN of the revision.
Radiomics dropped the 56 shape features (372 kept), and CNN + radiomics (six probabilities)
became the primary model. See the [revision overview](revision_2026-10.md).

## Checkpoints

All five fold checkpoints of W3 and W4 are retained privately and are not distributed. The
v1.1.0 statement that W3 fold 1 and W4 fold 0 were not retained was wrong; the revision
reproduced the saved predictions from these checkpoints.
