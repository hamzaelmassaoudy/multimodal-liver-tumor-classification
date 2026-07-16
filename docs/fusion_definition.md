# Late-fusion definition

## Class and column order

Every probability triplet is ordered:

1. HCC
2. ICC
3. cHCC-CCA

Some historical files use `CHCC` as the third probability-column token. It denotes cHCC-CCA and does not define a fourth class.

## Full-fusion vector

The full-fusion model used exactly eight inputs in this immutable order:

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

W3 was a comparator and was explicitly excluded. The public constructor [`build_full_fusion_features`](../src/liver_tumor_pipeline/fusion.py) does not accept W3 probabilities and validates both three-class probability matrices before constructing the feature matrix.

The CNN-plus-radiomics comparator used the six W4 and W5 probability features without age or sex. The full model added the two clinical features. The meta-learner was fold-specific multinomial logistic regression.

## Fold pairing and evaluation

OOF W4 and W5 probabilities were paired by patient and fold within the 222-patient development cohort. Fold-specific meta-learners were then applied to the corresponding held-out internal predictions. Patient-level tables are not released; only privacy-safe aggregates are public.

## External clinical assumptions

External age was unavailable and replaced with the locked fold-specific development median. External sex was also unavailable. The historical adapter encoded sex as 0; a deterministic sensitivity analysis substituted the locked fold median of 1 in every fold. The models were neither retrained nor recalibrated for this comparison. See [external stress test](external_stress_test.md).
