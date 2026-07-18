#!/usr/bin/env python
"""Aggregate corrected-primary and encoded-sex-zero external predictions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from liver_tumor_pipeline.external import compare_sex_scenarios


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("predictions", type=Path, help="Private aligned scenario table")
    parser.add_argument("--primary-column", default="predicted_label_missing_fold_median")
    parser.add_argument("--sex-zero-column", default="predicted_label_sex0")
    args = parser.parse_args()
    frame = pd.read_csv(args.predictions)
    required = {args.primary_column, args.sex_zero_column}
    missing = required - set(frame.columns)
    if missing:
        raise KeyError(f"Scenario table is missing columns: {sorted(missing)}")
    summary = compare_sex_scenarios(
        frame[args.primary_column].to_numpy(),
        frame[args.sex_zero_column].to_numpy(),
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
