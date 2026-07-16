#!/usr/bin/env python
"""Aggregate the locked external sex=0 and sex=1 prediction scenarios."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from liver_tumor_pipeline.external import compare_sex_scenarios


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("predictions", type=Path, help="Private aligned scenario table")
    parser.add_argument("--historical-column", default="predicted_label_sex0")
    parser.add_argument("--median-sex-column", default="predicted_label_sex1")
    args = parser.parse_args()
    frame = pd.read_csv(args.predictions)
    required = {args.historical_column, args.median_sex_column}
    missing = required - set(frame.columns)
    if missing:
        raise KeyError(f"Scenario table is missing columns: {sorted(missing)}")
    summary = compare_sex_scenarios(
        frame[args.historical_column].to_numpy(),
        frame[args.median_sex_column].to_numpy(),
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
