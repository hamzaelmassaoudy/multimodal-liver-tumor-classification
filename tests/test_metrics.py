import numpy as np
import pytest

from liver_tumor_pipeline.constants import CLASS_ORDER
from liver_tumor_pipeline.metrics import (
    benjamini_hochberg_adjust,
    bonferroni_adjust,
    macro_ovr_auc,
    validate_probabilities,
)


def test_class_order_is_locked():
    assert CLASS_ORDER == ("HCC", "ICC", "cHCC-CCA")


def test_probability_rows_and_macro_auc():
    labels = np.array([0, 1, 2, 0, 1, 2])
    probabilities = np.array(
        [
            [0.8, 0.1, 0.1],
            [0.1, 0.8, 0.1],
            [0.1, 0.1, 0.8],
            [0.7, 0.2, 0.1],
            [0.1, 0.7, 0.2],
            [0.2, 0.1, 0.7],
        ]
    )
    np.testing.assert_array_equal(validate_probabilities(probabilities), probabilities)
    assert macro_ovr_auc(labels, probabilities) == pytest.approx(1.0)


def test_invalid_probability_rows_fail():
    with pytest.raises(ValueError):
        validate_probabilities(np.array([[0.4, 0.4, 0.4]]))
    with pytest.raises(ValueError):
        validate_probabilities(np.array([[1.1, -0.1, 0.0]]))


def test_corrected_nine_comparison_adjustments_match_released_values():
    raw = np.array(
        [0.300528, 0.629143, 0.029347, 0.735069, 0.113875, 0.345737, 0.910200, 0.368868, 0.227495]
    )
    expected_bonferroni = np.array([1.0, 1.0, 0.264126, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0])
    expected_bh = np.array(
        [0.553302, 0.808898, 0.264126, 0.826953, 0.512436, 0.553302, 0.910200, 0.553302, 0.553302]
    )
    np.testing.assert_allclose(bonferroni_adjust(raw), expected_bonferroni, atol=5e-6)
    np.testing.assert_allclose(benjamini_hochberg_adjust(raw), expected_bh, atol=5e-6)
