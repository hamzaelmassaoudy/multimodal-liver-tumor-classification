# Scientific scope

## Research question

The study evaluates whether complementary imaging and clinical branches improve classification of three primary liver tumor classes on multiphase contrast-enhanced CT, and then subjects the frozen models to a deliberately difficult external HCC-only transportability test.

## Internal study design

PLC-CECT V4 contributed 278 patients: 94 hepatocellular carcinoma (HCC), 99 intrahepatic cholangiocarcinoma (ICC), and 85 combined hepatocellular-cholangiocarcinoma (cHCC-CCA). A patient-level stratified split assigned 222 patients to development and 56 to independent internal evaluation. Five patient-level stratified folds were used within development, with every phase from a patient kept in one partition.

The evaluated branches were:

- Clinical baseline using age and sex.
- W3, a portal-venous C2 single-phase 3D CNN.
- W4, a four-channel multiphase 3D CNN.
- W5, crop-restricted PyRadiomics features classified by LightGBM.
- CNN plus radiomics late fusion.
- Full fusion of W4 probabilities, W5 probabilities, age, and sex.
- A tumor-size-only development-CV baseline.

The primary metric was macro one-versus-rest AUC in class order HCC, ICC, cHCC-CCA. The held-out internal evaluation results are the strongest evidence because known cross-validation decisions may make CV and stacking estimates optimistic.

## External scope

The external HCC-TACE-Seg analysis retained 103 known-HCC patients. It was an HCC-only transportability stress test, not multiclass external validation. No external multiclass AUC or verified external CNN-plus-radiomics result is reported. The internal and external adapters differed in source conversion, resampling, crop construction, available phases, segmentations, feature availability, and missing-data handling.

## Appropriate interpretation

The internal results support proof-of-concept classification within the evaluated cohorts and historical workflow. The external findings demonstrate substantial sensitivity to domain, adapter, feature-availability, and missing-sex assumptions. They do not establish clinical readiness or robust transportability.

See [preprocessing](preprocessing.md), [fusion definition](fusion_definition.md), [external stress test](external_stress_test.md), and [model card](model_card.md).
