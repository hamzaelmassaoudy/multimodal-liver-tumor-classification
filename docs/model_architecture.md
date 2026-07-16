# Model architecture

## Locked class and phase conventions

- Class order: HCC, ICC, cHCC-CCA.
- Phase order: P, C1, C2, C3.
- Crop size: `96 x 96 x 96` voxels.

The token `CHCC` appears in some historical probability-column names for compatibility; its display class is cHCC-CCA.

## W3: single-phase CNN

W3 used the portal-venous C2 crop only, with input shape `1 x 96 x 96 x 96`. The network was MONAI's three-dimensional ResNet-18 with random initialization and a three-class output. W3 was a comparator and was not an input to the full-fusion model.

## W4: multiphase CNN

W4 used input shape `4 x 96 x 96 x 96`, with channels ordered P, C1, C2, C3. Each channel was independently centered on its own phase-specific tumor-mask centroid. The network was a three-dimensional ResNet-18 initialized randomly, with a three-class output.

Historical training augmentation used random in-plane flips, with the same selected spatial flip applied jointly across all W4 channels, and per-channel intensity jitter. Validation and internal evaluation used no augmentation. Applying the same flip to the stacked crops does not imply that the source phases were anatomically registered.

## W5: radiomics-LightGBM

W5 extracted original-image PyRadiomics features from the tumor portion retained inside each fixed crop. The cached images used the 0-255 representation, no additional radiomics z-score normalization, fixed bin width 5, and three-dimensional extraction. Enabled classes were shape, first-order, GLCM, GLRLM, GLSZM, GLDM, and NGTDM.

There were 107 features per phase and 428 candidate features per patient. Feature handling and selection were fold-specific, followed by LightGBM classification. Because some lesions were truncated by the fixed cube, W5 is a crop-restricted tumor-radiomics branch.

## Clinical and fusion models

The clinical baseline used age and sex. Late fusion used fold-specific multinomial logistic regression. The exact full-fusion vector is defined in [fusion definition](fusion_definition.md).

## Retained-artifact limitation

The W3 fold 1 and W4 fold 0 historical checkpoints were not retained. Saved predictions support aggregate metric reanalysis, but exact all-fold historical CNN inference cannot be reconstructed from the checkpoint collection. See [reproducibility](reproducibility.md).
