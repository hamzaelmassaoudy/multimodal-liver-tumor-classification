#!/usr/bin/env python
"""Count, for every PLC-CECT scan, the share of the tumor mask lying inside the released liver mask.

The internal preprocessing multiplies each CT by its liver mask, so tumor voxels outside that mask
become zero in the model inputs. This post hoc census reads the released NIfTI masks directly.
Its output has one row per patient and phase and therefore stays private; publish only the
class-level summary produced by ``summarize_tumor_inside_liver_mask.py``.

Example::

    python scripts/revision/census_tumor_inside_liver_mask.py \
        --plc-cect-root "$PLC_CECT_ROOT" --output private/tumor_inside_liver_mask.csv
"""

from __future__ import annotations

import argparse
import csv
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import nibabel as nib
import numpy as np


def mask(path: Path) -> np.ndarray:
    array = np.asanyarray(nib.load(str(path)).dataobj)
    while array.ndim > 3:
        array = array[..., 0]
    return array > 0


def measure(job: tuple[str, str, Path, Path]) -> list:
    patient, phase, tumor_path, liver_path = job
    try:
        tumor, liver = mask(tumor_path), mask(liver_path)
    except Exception as error:  # an unreadable file is reported, not hidden
        return [patient, phase, "", "", "", f"error: {error}"]
    if tumor.shape != liver.shape:
        return [patient, phase, int(tumor.sum()), "", "", False]
    voxels = int(tumor.sum())
    inside = int((tumor & liver).sum())
    return [patient, phase, voxels, inside, inside / voxels if voxels else "", True]


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--plc-cect-root", type=Path, required=True, help="folder of patient_data.csv"
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    root = args.plc_cect_root
    jobs, seen = [], set()
    with (root / "patient_data.csv").open(encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            key = (row["patient_id"], row["phase"])
            if key in seen or row["cancer_type"] not in {"HCC", "ICC", "CHCC"}:
                continue
            seen.add(key)
            jobs.append((*key, root / row["mask_path"], root / row["liver_mask_path"]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            [
                "patient_id",
                "phase",
                "tumor_voxels",
                "inside_liver_voxels",
                "share_inside",
                "same_grid",
            ]
        )
        with ThreadPoolExecutor(args.workers) as pool:
            writer.writerows(pool.map(measure, jobs))
    print(f"Measured {len(jobs)} scans; private output written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
