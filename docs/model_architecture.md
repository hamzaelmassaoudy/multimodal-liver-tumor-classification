# Model architecture

## Locked conventions

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

## Retained-artifact limitation

W3 fold 1 and W4 fold 0 checkpoints were not retained. Saved predictions support aggregate metric
reanalysis, but exact all-fold CNN inference cannot be reconstructed.
