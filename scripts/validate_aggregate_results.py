#!/usr/bin/env python
"""Validate released aggregate schemas and reproducibility boundaries."""

from __future__ import annotations

import argparse
from pathlib import Path

from liver_tumor_pipeline.validation import validate_aggregate_directory


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("aggregate_dir", nargs="?", type=Path, default=Path("results/aggregate"))
    args = parser.parse_args()
    issues = validate_aggregate_directory(args.aggregate_dir)
    if issues:
        raise SystemExit("\n".join(issues))
    print("Aggregate result validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
