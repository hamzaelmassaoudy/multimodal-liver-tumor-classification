import inspect

import numpy as np

from liver_tumor_pipeline.constants import FULL_FUSION_FEATURES
from liver_tumor_pipeline.fusion import build_full_fusion_features, fusion_feature_names


def test_full_fusion_feature_order_and_values():
    w4 = np.array([[0.1, 0.2, 0.7], [0.6, 0.3, 0.1]])
    w5 = np.array([[0.3, 0.4, 0.3], [0.2, 0.5, 0.3]])
    features = build_full_fusion_features(w4, w5, np.array([61, 52]), np.array([1, 0]))
    np.testing.assert_allclose(features[0], [0.1, 0.2, 0.7, 0.3, 0.4, 0.3, 61, 1])
    assert fusion_feature_names() == FULL_FUSION_FEATURES


def test_w3_is_excluded_from_full_fusion_api_and_names():
    parameters = inspect.signature(build_full_fusion_features).parameters
    assert all("w3" not in name.lower() for name in parameters)
    assert all("w3" not in name.lower() for name in FULL_FUSION_FEATURES)
    assert len(FULL_FUSION_FEATURES) == 8
