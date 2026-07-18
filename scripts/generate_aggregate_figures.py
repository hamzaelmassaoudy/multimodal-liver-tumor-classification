#!/usr/bin/env python
"""Generate privacy-safe figures exclusively from released aggregate CSV files."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def save_internal_performance(aggregate: Path, figures: Path) -> None:
    frame = pd.read_csv(aggregate / "internal_performance.csv")
    frame = frame[frame["heldout_macro_auc"].notna()].copy()
    positions = np.arange(len(frame))
    width = 0.38
    fig, axis = plt.subplots(figsize=(10, 5.6))
    axis.bar(
        positions - width / 2,
        frame["cv_macro_auc_mean"],
        width,
        yerr=frame["cv_macro_auc_sd"],
        capsize=3,
        label="Five-fold CV",
        color="#4C78A8",
    )
    axis.bar(
        positions + width / 2,
        frame["heldout_macro_auc"],
        width,
        label="Held-out evaluation",
        color="#F58518",
    )
    axis.set_xticks(positions, frame["model"], rotation=25, ha="right")
    axis.set_ylabel("Macro one-versus-rest AUC")
    axis.set_ylim(0.5, 1.0)
    axis.legend(frameon=False)
    axis.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(figures / "internal_performance.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def save_external_scenarios(aggregate: Path, figures: Path) -> None:
    frame = pd.read_csv(aggregate / "external_stress_test.csv")
    selections = [
        ("W3 single-phase CNN", "Frozen external inference", "W3"),
        ("W4 multiphase CNN", "Frozen external inference", "W4"),
        ("W5 radiomics-LightGBM", "Baseline real plus imputed feature handling", "W5 baseline"),
        ("Full fusion", "Missing sex, fold-local median", "Full fusion\nmissing → median"),
        ("Full fusion", "Encoded sex=0 sensitivity", "Full fusion\nsex=0 sensitivity"),
    ]
    values = []
    labels = []
    for branch, scenario, label in selections:
        rows = frame[(frame["branch"] == branch) & (frame["scenario"] == scenario)]
        if len(rows) != 1:
            raise ValueError(f"Expected one aggregate row for {branch}: {scenario}")
        values.append(float(rows.iloc[0]["hcc_sensitivity"]))
        labels.append(label)
    fig, axis = plt.subplots(figsize=(9.4, 5.0))
    bars = axis.bar(labels, values, color=["#4C78A8", "#72B7B2", "#59A14F", "#F2CF5B", "#E45756"])
    axis.set_ylabel("HCC sensitivity")
    axis.set_ylim(0, 1.08)
    axis.grid(axis="y", alpha=0.2)
    for bar, value in zip(bars, values, strict=True):
        axis.text(bar.get_x() + bar.get_width() / 2, value + 0.025, f"{value:.3f}", ha="center")
    fig.tight_layout()
    fig.savefig(figures / "external_stress_test.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def save_crop_retention(aggregate: Path, figures: Path) -> None:
    frame = pd.read_csv(aggregate / "c2_crop_retention.csv")
    selected = frame[
        frame["metric"].isin(
            [
                "Some tumor loss",
                "Retention below 95%",
                "Retention below 90%",
                "Retention below 75%",
                "Retention below 50%",
            ]
        )
    ]
    fig, axis = plt.subplots(figsize=(8.5, 4.8))
    bars = axis.barh(selected["metric"], selected["percent"], color="#B279A2")
    axis.invert_yaxis()
    axis.set_xlabel("Patients (%)")
    axis.set_xlim(0, 60)
    axis.grid(axis="x", alpha=0.2)
    for bar, value in zip(bars, selected["percent"], strict=True):
        axis.text(value + 1, bar.get_y() + bar.get_height() / 2, f"{value:.1f}%", va="center")
    fig.tight_layout()
    fig.savefig(figures / "c2_crop_retention.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aggregate", type=Path, default=Path("results/aggregate"))
    parser.add_argument("--figures", type=Path, default=Path("results/figures"))
    args = parser.parse_args()
    args.figures.mkdir(parents=True, exist_ok=True)
    save_internal_performance(args.aggregate, args.figures)
    save_external_scenarios(args.aggregate, args.figures)
    save_crop_retention(args.aggregate, args.figures)
    print("Generated three figures from released aggregate tables.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
