#!/usr/bin/env python
"""Verify nine-test adjustments from corrected aggregate DeLong p-values."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from liver_tumor_pipeline.metrics import benjamini_hochberg_adjust, bonferroni_adjust


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Aggregate CSV containing uncorrected_p")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    frame = pd.read_csv(args.input)
    required = {"uncorrected_p", "bonferroni_p_9", "bh_p_9"}
    if len(frame) != 9 or not required.issubset(frame.columns):
        raise ValueError("The corrected DeLong table must contain nine rows and adjusted p-values")
    raw = frame["uncorrected_p"].to_numpy(dtype=float)
    calculated_bonferroni = bonferroni_adjust(raw)
    calculated_bh = benjamini_hochberg_adjust(raw)
    if not np.allclose(calculated_bonferroni, frame["bonferroni_p_9"], atol=5e-6):
        raise ValueError("Stored Bonferroni values do not match the corrected exact-p family")
    if not np.allclose(calculated_bh, frame["bh_p_9"], atol=5e-6):
        raise ValueError(
            "Stored Benjamini-Hochberg values do not match the corrected exact-p family"
        )
    frame["bonferroni_p_9_recalculated"] = calculated_bonferroni
    frame["bh_p_9_recalculated"] = calculated_bh
    if args.output:
        frame.to_csv(args.output, index=False)
        print(f"Wrote verified DeLong summary to {args.output}.")
    else:
        print("Corrected nine-test DeLong adjustment verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
