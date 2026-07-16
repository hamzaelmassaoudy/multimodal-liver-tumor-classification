import numpy as np
import pytest

from liver_tumor_pipeline.preprocessing import (
    compute_center_of_mass,
    crop_cube,
    preprocess_independent_phases,
    summarize_retention,
    tumor_retention,
)


def test_center_and_deterministic_crop_size():
    mask = np.zeros((9, 9, 9), dtype=np.uint8)
    mask[3:6, 3:6, 3:6] = 1
    center = compute_center_of_mass(mask)
    assert center == (4, 4, 4)
    first = crop_cube(mask, center, 6)
    second = crop_cube(mask, center, 6)
    assert first.shape == (6, 6, 6)
    np.testing.assert_array_equal(first, second)


def test_boundary_padding_is_zero_and_preserves_source_voxel():
    volume = np.ones((3, 4, 5), dtype=np.uint8)
    crop = crop_cube(volume, (0, 0, 0), 6)
    assert crop.shape == (6, 6, 6)
    assert crop[3, 3, 3] == 1
    assert crop[0, 0, 0] == 0


def test_independent_phase_centers_accept_different_source_depths():
    ct = {}
    tumor = {}
    liver = {}
    for index, (phase, depth) in enumerate(
        zip(("P", "C1", "C2", "C3"), (7, 8, 9, 10), strict=True)
    ):
        shape = (8, 8, depth)
        ct[phase] = np.full(shape, index + 1, dtype=np.float32)
        tumor[phase] = np.zeros(shape, dtype=np.uint8)
        liver[phase] = np.ones(shape, dtype=np.uint8)
        tumor[phase][2 + index, 3, depth // 2] = 1
    result = preprocess_independent_phases(ct, tumor, liver, crop_size=6)
    assert result["ct"].shape == (4, 6, 6, 6)
    assert result["tumor_mask"].sum(axis=(1, 2, 3)).tolist() == [1, 1, 1, 1]
    assert len({tuple(center) for center in result["centers"]}) == 4


def test_empty_tumor_uses_same_phase_liver_center():
    shape = (7, 7, 7)
    ct = {phase: np.ones(shape) for phase in ("P", "C1", "C2", "C3")}
    tumor = {phase: np.zeros(shape) for phase in ct}
    liver = {phase: np.zeros(shape) for phase in ct}
    for phase in liver:
        liver[phase][1, 2, 3] = 1
    result = preprocess_independent_phases(ct, tumor, liver, crop_size=4)
    assert result["centers"].tolist() == [[1, 2, 3]] * 4


def test_tumor_retention_and_aggregate_thresholds():
    assert tumor_retention(100, 75) == 0.75
    summary = summarize_retention([100, 100, 100, 100], [100, 94, 74, 0])
    assert summary["exact_retention"] == 1
    assert summary["some_loss"] == 3
    assert summary["below_95_percent"] == 3
    assert summary["below_75_percent"] == 2
    assert summary["empty_crops"] == 1
    assert summary["volume_weighted_retention"] == pytest.approx(0.67)


def test_invalid_retention_is_rejected():
    with pytest.raises(ValueError):
        tumor_retention(10, 11)
