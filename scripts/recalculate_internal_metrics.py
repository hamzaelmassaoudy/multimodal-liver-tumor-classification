#!/usr/bin/env python
"""Recalculate aggregate three-class metrics from an authorized prediction table."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, f1_score

from liver_tumor_pipeline.metrics import macro_ovr_auc, validate_probabilities


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("predictions", type=Path)
    parser.add_argument("--label-column", default="label")
    parser.add_argument(
        "--probability-columns",
        nargs=3,
        default=("prob_HCC", "prob_ICC", "prob_CHCC"),
        metavar=("HCC", "ICC", "CHCC"),
    )
    args = parser.parse_args()

    frame = pd.read_csv(args.predictions)
    required = {args.label_column, *args.probability_columns}
    missing = required - set(frame.columns)
    if missing:
        raise KeyError(f"Prediction table is missing columns: {sorted(missing)}")
    labels = frame[args.label_column].to_numpy(dtype=int)
    probabilities = validate_probabilities(frame[list(args.probability_columns)].to_numpy())
    predicted = probabilities.argmax(axis=1)
    result = {
        "rows": int(len(frame)),
        "macro_ovr_auc": macro_ovr_auc(labels, probabilities),
        "accuracy": float(accuracy_score(labels, predicted)),
        "macro_f1": float(f1_score(labels, predicted, average="macro")),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
