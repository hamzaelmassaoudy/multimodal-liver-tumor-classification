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


def test_nine_comparison_adjustments_match_released_values():
    raw = np.array([0.1579, 0.3263, 0.0293, 0.5549, 0.1030, 0.3457, 0.5367, 0.1816, 0.2275])
    expected_bonferroni = np.array([1.0, 1.0, 0.2637, 1.0, 0.9270, 1.0, 1.0, 1.0, 1.0])
    expected_bh = np.array(
        [
            0.4086,
            0.44447142857142857,
            0.2637,
            0.5549,
            0.4086,
            0.44447142857142857,
            0.5549,
            0.4086,
            0.4095,
        ]
    )
    np.testing.assert_allclose(bonferroni_adjust(raw), expected_bonferroni)
    np.testing.assert_allclose(benjamini_hochberg_adjust(raw), expected_bh)
