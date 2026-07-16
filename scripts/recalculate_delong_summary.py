#!/usr/bin/env python
"""Recalculate nine-test p-value adjustments from an aggregate DeLong table."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from liver_tumor_pipeline.metrics import benjamini_hochberg_adjust, bonferroni_adjust


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Aggregate CSV containing reported_raw_p")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    frame = pd.read_csv(args.input)
    if len(frame) != 9 or "reported_raw_p" not in frame:
        raise ValueError("The finalized correction family must contain exactly nine raw p-values")
    raw = frame["reported_raw_p"].to_numpy(dtype=float)
    frame["bonferroni_p_9_recalculated"] = bonferroni_adjust(raw)
    frame["bh_p_9_recalculated"] = benjamini_hochberg_adjust(raw)
    if args.output:
        frame.to_csv(args.output, index=False)
    else:
        print(frame.to_csv(index=False), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
