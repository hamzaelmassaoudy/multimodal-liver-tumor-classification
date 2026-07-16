#!/usr/bin/env python
"""Calculate privacy-safe aggregate C2 crop retention from retained private artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from liver_tumor_pipeline.preprocessing import summarize_retention


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("metadata", type=Path, help="Private processed metadata CSV")
    parser.add_argument("radiomics", type=Path, help="Private W5 radiomics Parquet file")
    parser.add_argument("--output", type=Path, help="Optional aggregate-only JSON output")
    args = parser.parse_args()

    metadata = pd.read_csv(args.metadata, usecols=["patient_id", "tumor_vol"])
    radiomics = pd.read_parquet(
        args.radiomics,
        columns=["patient_id", "C2_original_shape_VoxelVolume"],
    )
    if metadata["patient_id"].duplicated().any() or radiomics["patient_id"].duplicated().any():
        raise ValueError("Private input identifiers must be unique")
    aligned = metadata.merge(radiomics, on="patient_id", how="inner", validate="one_to_one")
    if len(aligned) != len(metadata) or len(aligned) != len(radiomics):
        raise ValueError("Private C2 artifacts do not have identical membership")
    aggregate = summarize_retention(
        aligned["tumor_vol"].to_numpy(),
        aligned["C2_original_shape_VoxelVolume"].to_numpy(),
    )
    payload = json.dumps(aggregate, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
