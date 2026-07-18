"""Deterministic aggregate utilities for external missing-sex scenarios."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np


def hcc_sensitivity(predicted_labels: Sequence[int], *, hcc_label: int = 0) -> float:
    """Calculate HCC sensitivity for a cohort known to contain only HCC cases."""

    predicted = np.asarray(predicted_labels, dtype=int).reshape(-1)
    if predicted.size == 0:
        raise ValueError("Predicted labels cannot be empty")
    return float(np.mean(predicted == hcc_label))


def compare_sex_scenarios(
    primary_missing_sex_predictions: Sequence[int],
    sex_zero_predictions: Sequence[int],
    *,
    hcc_label: int = 0,
) -> dict[str, float | int]:
    """Compare the corrected missing-sex primary and encoded-sex-zero scenarios."""

    primary = np.asarray(primary_missing_sex_predictions, dtype=int).reshape(-1)
    sex_zero = np.asarray(sex_zero_predictions, dtype=int).reshape(-1)
    if primary.size == 0 or primary.shape != sex_zero.shape:
        raise ValueError("Scenario predictions must be nonempty aligned vectors")
    return {
        "patients": int(primary.size),
        "primary_hcc_count": int(np.count_nonzero(primary == hcc_label)),
        "primary_hcc_sensitivity": hcc_sensitivity(primary, hcc_label=hcc_label),
        "sex_zero_hcc_count": int(np.count_nonzero(sex_zero == hcc_label)),
        "sex_zero_hcc_sensitivity": hcc_sensitivity(sex_zero, hcc_label=hcc_label),
        "changed_predictions": int(np.count_nonzero(primary != sex_zero)),
    }
