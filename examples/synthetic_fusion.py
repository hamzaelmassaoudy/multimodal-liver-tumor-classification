#!/usr/bin/env python
"""Demonstrate training-fold imputation and fusion with entirely synthetic inputs."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.impute import SimpleImputer

from liver_tumor_pipeline.fusion import build_full_fusion_features, fusion_feature_names


@dataclass(frozen=True)
class SyntheticExample:
    """Feature matrices and the imputer fitted on the synthetic training fold."""

    training_features: np.ndarray
    evaluation_features: np.ndarray
    imputer: SimpleImputer


def run_example() -> SyntheticExample:
    """Build eight-column matrices without using evaluation rows to fit imputation."""

    # These invented probabilities are not outputs from study models or patient data.
    training_w4 = np.array(
        [
            [0.7, 0.2, 0.1],
            [0.2, 0.6, 0.2],
            [0.1, 0.2, 0.7],
            [0.6, 0.3, 0.1],
            [0.1, 0.7, 0.2],
            [0.2, 0.2, 0.6],
        ]
    )
    training_w5 = np.array(
        [
            [0.6, 0.3, 0.1],
            [0.2, 0.7, 0.1],
            [0.2, 0.1, 0.7],
            [0.7, 0.2, 0.1],
            [0.2, 0.6, 0.2],
            [0.1, 0.3, 0.6],
        ]
    )
    training_clinical = np.array(
        [[40, 0], [50, 1], [np.nan, np.nan], [60, 0], [70, 1], [55, 1]], dtype=float
    )
    evaluation_w4 = np.array([[0.5, 0.3, 0.2], [0.2, 0.2, 0.6]])
    evaluation_w5 = np.array([[0.6, 0.2, 0.2], [0.1, 0.3, 0.6]])
    evaluation_clinical = np.array([[np.nan, np.nan], [83, 0]], dtype=float)

    # A real workflow must fit a separate imputer inside each training fold.
    # Evaluation rows are transformed with the training medians, never fitted.
    imputer = SimpleImputer(strategy="median")
    training_imputed = imputer.fit_transform(training_clinical)
    evaluation_imputed = imputer.transform(evaluation_clinical)

    # The constructor requires finite clinical inputs, so imputation comes first.
    training_features = build_full_fusion_features(
        training_w4, training_w5, training_imputed[:, 0], training_imputed[:, 1]
    )
    evaluation_features = build_full_fusion_features(
        evaluation_w4, evaluation_w5, evaluation_imputed[:, 0], evaluation_imputed[:, 1]
    )
    return SyntheticExample(training_features, evaluation_features, imputer)


def main() -> int:
    example = run_example()
    print("Synthetic example only; no patient data or study performance is used.")
    print(f"Training-fold clinical medians (age, sex): {example.imputer.statistics_.tolist()}")
    print(f"Training feature matrix: {example.training_features.shape}")
    print(f"Evaluation feature matrix: {example.evaluation_features.shape}")
    print("Feature order: " + ", ".join(fusion_feature_names()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
