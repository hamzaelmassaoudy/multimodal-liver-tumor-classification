# Late-fusion definition

## Class and column order

Every probability triplet is ordered HCC, ICC, cHCC-CCA. Some retained files use `CHCC` as the
third token; it denotes cHCC-CCA and does not define a fourth class.

## Exact full-fusion vector

| Position | Feature |
|---:|---|
| 1 | W4 HCC probability |
| 2 | W4 ICC probability |
| 3 | W4 cHCC-CCA probability |
| 4 | W5 HCC probability |
| 5 | W5 ICC probability |
| 6 | W5 cHCC-CCA probability |
| 7 | Age |
| 8 | Sex |

W3 was a comparator and was excluded. The public constructor
[`build_full_fusion_features`](../src/liver_tumor_pipeline/fusion.py) validates the two three-class
probability matrices before constructing the eight-column matrix.

CNN-plus-radiomics used the six W4/W5 probability features. Full fusion added age and sex.
The meta-learner was fold-specific multinomial logistic regression.

## Corrected internal missingness handling

The provenance audit found three unresolved internal sex entries. The corrected primary analysis
retained them as missing. Each fold fitted median imputation and scaling on its training patients,
then fitted clinical and fusion logistic regression. The historical exact-token rule encoded male
as 1 and every other token as 0; it is retained only as a sensitivity analysis.

OOF W4 and W5 probabilities were paired by patient and fold within 222 development patients.
Corrected clinical and fusion models were refitted; upstream branch probabilities were unchanged.
Patient-level tables remain private.

## External clinical assumptions

External age and sex were unavailable. The corrected primary model-defined scenario passed both as
missing and used each model’s training-fold median; all five sex medians were 1. Encoded sex=0 was
evaluated separately. No external values or labels entered fitting or model selection for these
fusion scenarios. The separate radiomics Condition C availability-subset diagnostic is documented
in the [external stress test](external_stress_test.md).
