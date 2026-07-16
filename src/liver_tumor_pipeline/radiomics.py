"""Verified historical radiomics specification checks."""

from __future__ import annotations

from typing import Any

EXPECTED_FEATURE_CLASSES = (
    "shape",
    "firstorder",
    "glcm",
    "glrlm",
    "glszm",
    "gldm",
    "ngtdm",
)


def validate_radiomics_config(config: dict[str, Any]) -> None:
    """Fail if configuration changes the retained historical W5 specification."""

    expected = {
        "image_representation": "cached_0_255",
        "normalization": False,
        "bin_width": 5,
        "dimensionality": "3D",
        "features_per_phase": 107,
        "candidate_features_per_patient": 428,
    }
    mismatches = {
        key: (config.get(key), value) for key, value in expected.items() if config.get(key) != value
    }
    if tuple(config.get("feature_classes", ())) != EXPECTED_FEATURE_CLASSES:
        mismatches["feature_classes"] = (config.get("feature_classes"), EXPECTED_FEATURE_CLASSES)
    if mismatches:
        raise ValueError(
            f"Radiomics configuration differs from the historical specification: {mismatches}"
        )
