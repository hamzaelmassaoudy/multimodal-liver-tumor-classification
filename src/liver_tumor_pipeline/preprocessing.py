"""Historical independent phase-centered preprocessing and retention utilities."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import numpy as np

from .constants import CROP_SIZE, PHASE_ORDER


def compute_center_of_mass(mask: np.ndarray) -> tuple[int, int, int] | None:
    """Return the rounded mean coordinate of positive voxels, or ``None`` if empty."""

    array = np.asarray(mask)
    if array.ndim != 3:
        raise ValueError(f"Expected a 3D mask, received shape {array.shape}")
    coordinates = np.asarray(np.where(array > 0))
    if coordinates.shape[1] == 0:
        return None
    return tuple(int(round(value)) for value in coordinates.mean(axis=1))


def crop_cube(
    volume: np.ndarray,
    center: Sequence[int],
    size: int = CROP_SIZE,
) -> np.ndarray:
    """Crop a cubic array around ``center`` and zero-pad outside image boundaries."""

    array = np.asarray(volume)
    if array.ndim != 3:
        raise ValueError(f"Expected a 3D volume, received shape {array.shape}")
    if len(center) != 3:
        raise ValueError("Center must have exactly three coordinates")
    if size <= 0:
        raise ValueError("Crop size must be positive")

    half = size // 2
    starts = [int(coordinate) - half for coordinate in center]
    ends = [start + size for start in starts]
    pad_before = [max(0, -start) for start in starts]
    pad_after = [max(0, end - array.shape[index]) for index, end in enumerate(ends)]
    source_slices = tuple(
        slice(max(0, start), min(array.shape[index], end))
        for index, (start, end) in enumerate(zip(starts, ends, strict=True))
    )
    cropped = array[source_slices]
    if any(pad_before) or any(pad_after):
        cropped = np.pad(
            cropped,
            tuple(zip(pad_before, pad_after, strict=True)),
            mode="constant",
            constant_values=0,
        )
    expected = (size, size, size)
    if cropped.shape != expected:
        raise RuntimeError(f"Crop shape invariant failed: expected {expected}, got {cropped.shape}")
    return cropped


def preprocess_independent_phases(
    ct_by_phase: Mapping[str, np.ndarray],
    tumor_by_phase: Mapping[str, np.ndarray],
    liver_by_phase: Mapping[str, np.ndarray],
    *,
    crop_size: int = CROP_SIZE,
) -> dict[str, np.ndarray]:
    """Apply the historical registration-free, phase-specific centering algorithm.

    Each phase uses its own tumor-mask centroid, with its own liver-mask centroid as
    the fallback for an empty tumor mask. Cross-phase source grids are not compared.
    The four fixed-size results can therefore be stacked even when source depths differ.
    """

    ct_crops: list[np.ndarray] = []
    tumor_crops: list[np.ndarray] = []
    liver_crops: list[np.ndarray] = []
    centers: list[tuple[int, int, int]] = []

    for phase in PHASE_ORDER:
        try:
            ct = np.asarray(ct_by_phase[phase])
            tumor = np.asarray(tumor_by_phase[phase])
            liver = np.asarray(liver_by_phase[phase])
        except KeyError as exc:
            raise KeyError(f"Missing required phase: {phase}") from exc
        if ct.ndim != 3 or ct.shape != tumor.shape or ct.shape != liver.shape:
            raise ValueError(
                f"Within-phase CT/tumor/liver shapes must match for {phase}: "
                f"{ct.shape}, {tumor.shape}, {liver.shape}"
            )

        center = compute_center_of_mass(tumor)
        if center is None:
            center = compute_center_of_mass(liver)
        if center is None:
            raise ValueError(f"Both tumor and liver masks are empty for phase {phase}")

        masked_ct = ct.astype(np.float32, copy=False) * (liver > 0)
        ct_crops.append(np.clip(crop_cube(masked_ct, center, crop_size), 0, 255).astype(np.uint8))
        tumor_crops.append((crop_cube(tumor, center, crop_size) > 0).astype(np.uint8))
        liver_crops.append((crop_cube(liver, center, crop_size) > 0).astype(np.uint8))
        centers.append(center)

    return {
        "ct": np.stack(ct_crops, axis=0),
        "tumor_mask": np.stack(tumor_crops, axis=0),
        "liver_mask": np.stack(liver_crops, axis=0),
        "centers": np.asarray(centers, dtype=np.int64),
    }


def tumor_retention(original_voxels: float, cropped_voxels: float) -> float:
    """Calculate retained positive-tumor fraction for one nonempty mask."""

    original = float(original_voxels)
    cropped = float(cropped_voxels)
    if not np.isfinite(original) or not np.isfinite(cropped):
        raise ValueError("Tumor voxel counts must be finite")
    if original <= 0:
        raise ValueError("Original tumor voxel count must be positive")
    if cropped < 0 or cropped > original:
        raise ValueError("Cropped tumor voxel count must be within [0, original]")
    return cropped / original


def summarize_retention(
    original_voxels: Sequence[float], cropped_voxels: Sequence[float]
) -> dict[str, float | int]:
    """Aggregate privacy-safe tumor-retention statistics without returning patient rows."""

    original = np.asarray(original_voxels, dtype=float)
    cropped = np.asarray(cropped_voxels, dtype=float)
    if original.ndim != 1 or cropped.shape != original.shape or original.size == 0:
        raise ValueError("Original and cropped counts must be nonempty aligned vectors")
    if not np.isfinite(original).all() or not np.isfinite(cropped).all():
        raise ValueError("Tumor voxel counts must be finite")
    if (original <= 0).any() or (cropped < 0).any() or (cropped > original).any():
        raise ValueError("Invalid original or cropped tumor voxel counts")

    retention = cropped / original
    return {
        "patients": int(original.size),
        "exact_retention": int(np.count_nonzero(cropped == original)),
        "some_loss": int(np.count_nonzero(cropped < original)),
        "below_95_percent": int(np.count_nonzero(retention < 0.95)),
        "below_90_percent": int(np.count_nonzero(retention < 0.90)),
        "below_75_percent": int(np.count_nonzero(retention < 0.75)),
        "below_50_percent": int(np.count_nonzero(retention < 0.50)),
        "empty_crops": int(np.count_nonzero(cropped == 0)),
        "median_retention": float(np.median(retention)),
        "minimum_retention": float(np.min(retention)),
        "volume_weighted_retention": float(cropped.sum() / original.sum()),
    }
