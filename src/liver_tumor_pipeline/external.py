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
    historical_predictions: Sequence[int],
    median_sex_predictions: Sequence[int],
    *,
    hcc_label: int = 0,
) -> dict[str, float | int]:
    """Compare the locked sex=0 and sex=1 external prediction scenarios."""

    historical = np.asarray(historical_predictions, dtype=int).reshape(-1)
    sensitivity = np.asarray(median_sex_predictions, dtype=int).reshape(-1)
    if historical.size == 0 or historical.shape != sensitivity.shape:
        raise ValueError("Scenario predictions must be nonempty aligned vectors")
    return {
        "patients": int(historical.size),
        "historical_hcc_count": int(np.count_nonzero(historical == hcc_label)),
        "historical_hcc_sensitivity": hcc_sensitivity(historical, hcc_label=hcc_label),
        "median_sex_hcc_count": int(np.count_nonzero(sensitivity == hcc_label)),
        "median_sex_hcc_sensitivity": hcc_sensitivity(sensitivity, hcc_label=hcc_label),
        "changed_predictions": int(np.count_nonzero(historical != sensitivity)),
    }
