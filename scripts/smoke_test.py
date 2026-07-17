#!/usr/bin/env python
"""Run a deterministic public-clone smoke test without patient data or model training."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from liver_tumor_pipeline.constants import FULL_FUSION_FEATURES, PHASE_ORDER
from liver_tumor_pipeline.fusion import build_full_fusion_features, fusion_feature_names
from liver_tumor_pipeline.preprocessing import preprocess_independent_phases
from liver_tumor_pipeline.validation import validate_release

REPO_ROOT = Path(__file__).resolve().parents[1]


def exercise_synthetic_preprocessing() -> None:
    """Confirm phase-specific centers, liver-centroid fallback, stacking, and zero padding."""

    shape = (12, 13, 14)
    tumor_centers = {"P": (1, 2, 3), "C1": (4, 5, 6), "C2": (7, 8, 9)}
    fallback_center = (10, 11, 12)
    ct_by_phase: dict[str, np.ndarray] = {}
    tumor_by_phase: dict[str, np.ndarray] = {}
    liver_by_phase: dict[str, np.ndarray] = {}

    for index, phase in enumerate(PHASE_ORDER, start=1):
        ct = np.full(shape, index * 20, dtype=np.float32)
        tumor = np.zeros(shape, dtype=np.uint8)
        liver = np.zeros(shape, dtype=np.uint8)
        center = tumor_centers.get(phase, fallback_center)
        if phase != "C3":
            tumor[center] = 1
        liver[center] = 1
        ct_by_phase[phase] = ct
        tumor_by_phase[phase] = tumor
        liver_by_phase[phase] = liver

    result = preprocess_independent_phases(ct_by_phase, tumor_by_phase, liver_by_phase, crop_size=8)
    expected_centers = np.asarray(
        [tumor_centers["P"], tumor_centers["C1"], tumor_centers["C2"], fallback_center]
    )
    if result["ct"].shape != (4, 8, 8, 8):
        raise RuntimeError("Synthetic phase-stack shape check failed")
    if not np.array_equal(result["centers"], expected_centers):
        raise RuntimeError("Independent phase-center or liver-fallback check failed")
    if int(result["tumor_mask"][3].sum()) != 0 or int(result["liver_mask"][3].sum()) != 1:
        raise RuntimeError("Empty-tumor liver-centroid fallback check failed")


def exercise_synthetic_fusion() -> None:
    """Confirm the immutable W4 + W5 + age + sex eight-feature construction."""

    w4 = np.asarray([[0.70, 0.20, 0.10], [0.10, 0.30, 0.60]])
    w5 = np.asarray([[0.60, 0.25, 0.15], [0.20, 0.20, 0.60]])
    age = np.asarray([54.0, 67.0])
    sex = np.asarray([0.0, 1.0])
    features = build_full_fusion_features(w4, w5, age, sex)
    expected = np.column_stack((w4, w5, age, sex))
    if features.shape != (2, 8) or not np.allclose(features, expected):
        raise RuntimeError("Eight-feature full-fusion construction check failed")
    if fusion_feature_names() != FULL_FUSION_FEATURES:
        raise RuntimeError("Full-fusion feature-name order check failed")


def main() -> int:
    issues = validate_release(REPO_ROOT)
    if issues:
        raise SystemExit("\n".join(f"ERROR: {issue}" for issue in issues))
    exercise_synthetic_preprocessing()
    exercise_synthetic_fusion()
    print(
        "Public-clone smoke test passed: release validation, independent-phase "
        "preprocessing, and eight-feature fusion."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
