"""Probability and multiclass metric utilities used by aggregate reanalysis."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import roc_auc_score

from .constants import CLASS_ORDER


def bonferroni_adjust(p_values: np.ndarray) -> np.ndarray:
    """Adjust a nonempty vector of raw p-values with Bonferroni correction."""

    values = np.asarray(p_values, dtype=float).reshape(-1)
    if values.size == 0 or not np.isfinite(values).all() or ((values < 0) | (values > 1)).any():
        raise ValueError("P-values must be a nonempty finite vector within [0, 1]")
    return np.minimum(values * values.size, 1.0)


def benjamini_hochberg_adjust(p_values: np.ndarray) -> np.ndarray:
    """Adjust a nonempty vector of raw p-values in original row order."""

    values = np.asarray(p_values, dtype=float).reshape(-1)
    if values.size == 0 or not np.isfinite(values).all() or ((values < 0) | (values > 1)).any():
        raise ValueError("P-values must be a nonempty finite vector within [0, 1]")
    order = np.argsort(values)
    ranked = values[order]
    factors = ranked * values.size / np.arange(1, values.size + 1)
    adjusted_ranked = np.minimum.accumulate(factors[::-1])[::-1]
    adjusted = np.empty_like(adjusted_ranked)
    adjusted[order] = np.clip(adjusted_ranked, 0, 1)
    return adjusted


def validate_probabilities(
    probabilities: np.ndarray,
    *,
    atol: float = 1e-6,
) -> np.ndarray:
    """Validate finite three-class probability rows in the locked class order."""

    array = np.asarray(probabilities, dtype=float)
    if array.ndim != 2 or array.shape[1] != len(CLASS_ORDER):
        raise ValueError(
            f"Expected probability shape (n, {len(CLASS_ORDER)}) for {CLASS_ORDER}, "
            f"received {array.shape}"
        )
    if not np.isfinite(array).all():
        raise ValueError("Probabilities must be finite")
    if (array < -atol).any() or (array > 1 + atol).any():
        raise ValueError("Probabilities must be between zero and one")
    if not np.allclose(array.sum(axis=1), 1.0, atol=atol):
        raise ValueError("Each probability row must sum to one")
    return array


def macro_ovr_auc(labels: np.ndarray, probabilities: np.ndarray) -> float:
    """Calculate macro one-versus-rest AUC using the locked three-class order."""

    probability_array = validate_probabilities(probabilities)
    label_array = np.asarray(labels, dtype=int).reshape(-1)
    if len(label_array) != len(probability_array):
        raise ValueError("Labels and probabilities must have the same number of rows")
    expected = set(range(len(CLASS_ORDER)))
    if set(np.unique(label_array)) != expected:
        raise ValueError(f"Labels must contain all encoded classes {sorted(expected)}")
    return float(
        roc_auc_score(
            label_array,
            probability_array,
            labels=list(range(len(CLASS_ORDER))),
            multi_class="ovr",
            average="macro",
        )
    )
