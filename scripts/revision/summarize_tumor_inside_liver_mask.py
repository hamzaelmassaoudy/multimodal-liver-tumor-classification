#!/usr/bin/env python
"""Summarize the private tumor-inside-liver-mask census into publishable class-level tables.

Rules fixed before the summary was computed: the patient measure is the portal-venous (C2) share,
and a tumor counts as inside when at least 90% of its voxels lie in the liver mask (the threshold
of the crop-truncation analysis). Model performance by subgroup uses saved predictions only.

Example::

    python scripts/revision/summarize_tumor_inside_liver_mask.py \
        --census private/tumor_inside_liver_mask.csv \
        --project-root "$PRIVATE_ARTIFACT_ROOT/liver_project" --output-dir results/revision_2026-10
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

CLASS_NAMES = {0: "HCC", 1: "ICC", 2: "cHCC-CCA"}
MODELS = {
    "CNN": "CNN phase_dropout_CNN [complete]",
    "Radiomics": "radiomics radiomics_noshape",
    "CNN + radiomics": "cnn_plus_radiomics: [ref] phase_dropout_CNN + radiomics_noshape",
    "Full fusion": "full_fusion: [ref] phase_dropout_CNN + radiomics_noshape",
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--census", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    labels = pd.read_parquet(args.project_root / "radiomics" / "radiomics_features.parquet")
    labels = labels.assign(patient_id=labels.patient_id.astype(str)).set_index("patient_id")[
        "label"
    ]
    census = pd.read_csv(args.census, dtype={"patient_id": str})
    census = census[census.patient_id.isin(labels.index)]
    census["share"] = pd.to_numeric(census.share_inside, errors="coerce")
    census.loc[census.same_grid.astype(str) != "True", "share"] = np.nan
    wide = census.pivot(index="patient_id", columns="phase", values="share")
    wide["label"] = labels.loc[wide.index]

    rows = []
    for label, name in CLASS_NAMES.items():
        for phase in ("P", "C1", "C2", "C3"):
            values = wide.loc[wide.label == label, phase].dropna()
            rows.append(
                {
                    "class": name,
                    "phase": phase,
                    "n": len(values),
                    "median": values.median(),
                    "q1": values.quantile(0.25),
                    "q3": values.quantile(0.75),
                    "n_lt_0.9": int((values < 0.9).sum()),
                    "n_lt_0.5": int((values < 0.5).sum()),
                    "n_eq_0": int((values == 0).sum()),
                }
            )
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out / "tumor_inside_liver_mask_by_class_phase.csv", index=False)

    preds = pd.read_csv(
        args.project_root / "revision_2026-10" / "E8b_20261018T025705Z" / "E8b_E9_predictions.csv",
        dtype={"patient_id": str},
    )
    rows = []
    for cohort in ("internal_oof", "internal_test"):
        for name, key in MODELS.items():
            table = preds[(preds.cohort == cohort) & (preds.model == key)].set_index("patient_id")
            table = table.join(wide[["C2", "label"]], how="left")
            groups = [
                ("all", np.ones(len(table), bool)),
                ("C2 share >= 0.9", (table.C2 >= 0.9).to_numpy()),
                ("C2 share < 0.9", (table.C2 < 0.9).to_numpy()),
            ]
            for group, keep in groups:
                sub = table[keep]
                y = sub.label.to_numpy().astype(int)
                p = sub[["p_HCC", "p_ICC", "p_CHCC"]].to_numpy()
                counts = np.bincount(y, minlength=3)
                macro = (
                    np.mean([roc_auc_score(y == k, p[:, k]) for k in range(3)])
                    if counts.min() >= 3
                    else np.nan
                )
                two = np.isin(y, [0, 1])
                rows.append(
                    {
                        "cohort": cohort,
                        "model": name,
                        "group": group,
                        "n": len(sub),
                        "n_HCC/ICC/cHCC": "/".join(map(str, counts)),
                        "macro_auc": macro,
                        "hcc_vs_icc_auc": roc_auc_score(
                            y[two] == 0, p[two, 0] / (p[two, 0] + p[two, 1])
                        ),
                        "accuracy": float((p.argmax(1) == y).mean()),
                    }
                )
    pd.DataFrame(rows).to_csv(out / "performance_by_tumor_inside_liver_mask.csv", index=False)
    print(f"Wrote the class-level summary and subgroup performance to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
