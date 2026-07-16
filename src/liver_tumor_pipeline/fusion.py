"""Late-fusion feature construction with the locked eight-feature order."""

from __future__ import annotations

import numpy as np

from .constants import FULL_FUSION_FEATURES
from .metrics import validate_probabilities


def build_full_fusion_features(
    w4_probabilities: np.ndarray,
    w5_probabilities: np.ndarray,
    age: np.ndarray,
    sex: np.ndarray,
) -> np.ndarray:
    """Construct W4 + W5 + age + sex features; W3 is intentionally not accepted."""

    w4 = validate_probabilities(w4_probabilities)
    w5 = validate_probabilities(w5_probabilities)
    if w4.shape != w5.shape:
        raise ValueError("W4 and W5 probability matrices must have identical shapes")
    age_array = np.asarray(age, dtype=float).reshape(-1)
    sex_array = np.asarray(sex, dtype=float).reshape(-1)
    if len(age_array) != len(w4) or len(sex_array) != len(w4):
        raise ValueError("Clinical vectors must align with probability rows")
    if not np.isfinite(age_array).all() or not np.isfinite(sex_array).all():
        raise ValueError("Clinical fusion inputs must be finite")
    features = np.column_stack((w4, w5, age_array, sex_array))
    if features.shape[1] != len(FULL_FUSION_FEATURES):
        raise RuntimeError("Full-fusion feature-count invariant failed")
    return features


def fusion_feature_names() -> tuple[str, ...]:
    """Return the immutable feature names corresponding to constructed columns."""

    return FULL_FUSION_FEATURES
