#!/usr/bin/env python
"""Draw the figures of the revised manuscript from the revision run outputs.

Every number comes from a run file in ``liver_project/revision_2026-10``; the few post hoc
quantities (acquisition-only classifiers, class-pair AUCs) are recomputed here from saved
predictions and image-header facts and are labelled post hoc in the captions. The inputs are
private (patient-level); only the aggregate figures are released in this repository.

Example::

    python scripts/revision/make_revision_figures.py \
        --project-root "$PRIVATE_ARTIFACT_ROOT/liver_project" \
        --output "$PRIVATE_ARTIFACT_ROOT/figures" --figures design internal size artifacts external

Each figure is written as PNG and PDF. The repository publishes PNG copies of Figures 1, 3, 4, 5,
and 7 in ``results/revision_2026-10/figures``; Figures 2, 6, and 8 show patient images and stay
private.
"""

import argparse
import json
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from sklearn.ensemble import RandomForestClassifier  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import roc_auc_score, roc_curve  # noqa: E402
from sklearn.model_selection import StratifiedKFold, cross_val_predict  # noqa: E402
from sklearn.pipeline import make_pipeline  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

PARSER = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
)
PARSER.add_argument("--project-root", type=Path, required=True, help="private liver_project folder")
PARSER.add_argument("--output", type=Path, required=True, help="folder for the PNG and PDF files")
PARSER.add_argument(
    "--raw-dir", type=Path, help="raw scans used for the stored-voxel panel of Figure 6"
)
PARSER.add_argument("--census-wide", type=Path, help="per-patient tumor-inside-liver-mask table")
PARSER.add_argument(
    "--figures",
    nargs="+",
    default=["design", "internal", "size", "artifacts", "external"],
    help="design examples internal size artifacts counterfactual external gradcam tace",
)
ARGS = PARSER.parse_args()
LP = ARGS.project_root
OUT = ARGS.output
OUT.mkdir(parents=True, exist_ok=True)
REV = LP / "revision_2026-10"
RUN = {
    "E3": "E3_20261017T041700Z",
    "E5c": "E5c_20261017T143217Z",
    "E8a": "E8a_20261017T162800Z",
    "E47": "E47_20261018T092239Z",
    "E7a": "E7a_20261017T191025Z",
    "E8b": "E8b_20261018T025705Z",
    "E6": "E6_20261017T114646Z",
    "F2": "F2_20261019T090444Z",
    "E4d": "E4d_20261019T030857Z",
}


def f(run, name, **kw):
    return pd.read_csv(REV / RUN[run] / name, **kw)


# ---- style (reference palette of the dataviz method; light surface; print) ----
INK, INK2, MUTED, GRID, BASE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
S1, S2, S3, S4 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"  # categorical slots 1-4 (validated)
CLASS_COL = {"HCC": S1, "ICC": S2, "cHCC-CCA": S3}
BLUES = ["#ffffff", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Liberation Sans", "DejaVu Sans"],
        "font.size": 7.5,
        "axes.titlesize": 8,
        "axes.labelsize": 7.5,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "legend.fontsize": 7,
        "axes.edgecolor": BASE,
        "axes.linewidth": 0.8,
        "xtick.color": INK2,
        "ytick.color": INK2,
        "axes.labelcolor": INK,
        "text.color": INK,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.major.size": 2.5,
        "ytick.major.size": 2.5,
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
        "legend.frameon": False,
        "savefig.facecolor": "white",
        "figure.facecolor": "white",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)
MM = 1 / 25.4


def panel(ax, letter, title):
    ax.set_title(title, loc="left", fontsize=8, color=INK, pad=6)
    ax.text(
        -0.02,
        1.02,
        letter,
        transform=ax.transAxes,
        fontsize=10,
        fontweight="bold",
        ha="right",
        va="bottom",
        color=INK,
    )


def grid_x(ax):
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def grid_y(ax):
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def save(fig, name):
    dest = (
        OUT
        if name.startswith("Figure") and name[6].isdigit()
        else OUT.parent / "2_Not_used_or_superseded"
    )
    dest.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(dest / f"{name}.{ext}", dpi=600, bbox_inches="tight")
    plt.close(fig)
    print("saved", name)


def macro_auc(y, p):
    return float(np.mean([roc_auc_score(y == k, p[:, k]) for k in range(3)]))


# ---- shared data ----
split = json.loads((LP / "splits" / "train_val_test.json").read_text())
DEV, TEST = [str(x) for x in split["dev_ids"]], [str(x) for x in split["test_ids"]]
LABEL = pd.read_parquet(LP / "radiomics" / "radiomics_features.parquet")[["patient_id", "label"]]
LABEL = LABEL.assign(patient_id=LABEL["patient_id"].astype(str)).set_index("patient_id")["label"]
CLASSES = ["HCC", "ICC", "cHCC-CCA"]
P3 = ["p_HCC", "p_ICC", "p_CHCC"]
PRED8B = f("E8b", "E8b_E9_predictions.csv", dtype={"patient_id": str})
MODEL_NAMES = {
    "CNN": "CNN",
    "radiomics": "Radiomics",
    "cnn_plus_radiomics": "CNN + radiomics",
    "full_fusion": "Full fusion",
}


# =================================================================================================
# Figure 3 — internal performance
# =================================================================================================
def figure_internal():
    m47 = f("E47", "E7b_internal_final_metrics.csv").set_index("model")
    r8b = f("E8b", "E8b_E9_internal_results.csv").set_index("model")
    rows = [
        ("CNN", "phase_dropout_CNN", "CNN noP_CNN [noP]"),
        ("Radiomics", "radiomics_noshape", "radiomics radiomics_noP"),
        (
            "CNN + radiomics",
            "cnn_plus_radiomics [phase_dropout_CNN]",
            "cnn_plus_radiomics: E9: noP_CNN + radiomics_noP",
        ),
        (
            "Full fusion",
            "full_fusion [phase_dropout_CNN]",
            "full_fusion: E9: noP_CNN + radiomics_noP",
        ),
    ]
    fig, axes = plt.subplots(
        2,
        2,
        figsize=(174 * MM, 132 * MM),
        gridspec_kw={"hspace": 0.62, "wspace": 0.95, "width_ratios": [1.15, 1]},
    )

    # A: held-out macro-AUC with / without the non-contrast phase
    ax = axes[0, 0]
    for i, (_name, a, b) in enumerate(rows):
        y = len(rows) - 1 - i
        for dy, src, key, col, filled in [(0.17, m47, a, S1, True), (-0.17, r8b, b, S2, False)]:
            est, lo, hi = (
                src.loc[key, "test_macro_auc"],
                src.loc[key, "boot_low"],
                src.loc[key, "boot_high"],
            )
            ax.plot([lo, hi], [y + dy] * 2, color=col, lw=1.6, solid_capstyle="round")
            ax.plot(
                est, y + dy, "o", ms=5, mfc=col if filled else "white", mec=col, mew=1.4, zorder=3
            )
            ax.text(
                1.005,
                y + dy,
                f"{est:.3f} ({lo:.3f}–{hi:.3f})",
                transform=ax.get_yaxis_transform(),
                va="center",
                fontsize=6.5,
                color=INK2,
            )
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows][::-1])
    ax.set_xlim(0.6, 1.0)
    ax.set_xlabel("Held-out macro-AUC (n = 56; bootstrap 95% CI)")
    grid_x(ax)
    ax.legend(
        handles=[
            Line2D([], [], color=S1, marker="o", lw=1.6, ms=5, label="All four phases"),
            Line2D(
                [],
                [],
                color=S2,
                marker="o",
                mfc="white",
                lw=1.6,
                ms=5,
                label="Without non-contrast phase",
            ),
        ],
        loc="lower left",
        bbox_to_anchor=(0, 1.06),
        ncol=2,
        handlelength=1.6,
        columnspacing=1.0,
        borderaxespad=0,
    )
    panel(ax, "A", "")

    # B: repeated cross-validation, 25 folds per model
    ax = axes[0, 1]
    pf = f("E7a", "E7a_per_fold.csv")
    summ = f("E7a", "E7a_summary.csv").set_index("model")
    order = [
        ("phase_dropout_CNN", "CNN"),
        ("radiomics_noshape", "Radiomics"),
        ("cnn_plus_radiomics", "CNN + radiomics"),
        ("full_fusion", "Full fusion"),
    ]
    rng = np.random.default_rng(1)
    for i, (key, _) in enumerate(order):
        yy = len(order) - 1 - i
        v = pf.loc[pf["model"] == key, "auc"].to_numpy()
        ax.scatter(
            v,
            yy + rng.uniform(-0.2, 0.2, len(v)),
            s=9,
            color=S1,
            alpha=0.55,
            linewidths=0,
            zorder=2,
        )
        mu, sd = summ.loc[key, "all25_folds_mean"], summ.loc[key, "all25_folds_sd"]
        ax.plot(
            [mu, mu], [yy - 0.32, yy + 0.32], color=INK, lw=1.6, solid_capstyle="round", zorder=3
        )
        ax.text(
            1.005,
            yy,
            f"{mu:.3f} ± {sd:.3f}",
            transform=ax.get_yaxis_transform(),
            va="center",
            fontsize=6.5,
            color=INK2,
        )
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([o[1] for o in order][::-1])
    ax.set_xlim(0.8, 1.0)
    ax.set_xlabel("Macro-AUC per fold (25 folds; bar = mean)")
    grid_x(ax)
    panel(ax, "B", "Repeated cross-validation, 5 × 5 folds (222)")

    # C: confusion matrix of CNN + radiomics on the held-out set
    ax = axes[1, 0]
    t = (
        PRED8B[
            (PRED8B["cohort"] == "internal_test")
            & (PRED8B["model"] == "cnn_plus_radiomics: [ref] phase_dropout_CNN + radiomics_noshape")
        ]
        .set_index("patient_id")
        .loc[TEST]
    )
    y = LABEL.loc[TEST].to_numpy()
    pred = t[P3].to_numpy().argmax(1)
    cm = np.array([[int(((y == i) & (pred == j)).sum()) for j in range(3)] for i in range(3)])
    from matplotlib.colors import LinearSegmentedColormap

    ax.imshow(cm, cmap=LinearSegmentedColormap.from_list("b", BLUES[:6]), vmin=0, vmax=cm.max())
    for i in range(3):
        for j in range(3):
            ax.text(
                j,
                i,
                str(cm[i, j]),
                ha="center",
                va="center",
                fontsize=8,
                color="white" if cm[i, j] > cm.max() * 0.55 else INK,
            )
    ax.set_xticks(range(3))
    ax.set_xticklabels(CLASSES)
    ax.set_yticks(range(3))
    ax.set_yticklabels(CLASSES)
    ax.set_xlabel("Predicted class")
    ax.set_ylabel("True class")
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    panel(ax, "C", f"CNN + radiomics, held-out set ({int(np.trace(cm))}/56 correct)")

    # D: missing-phase patterns, original vs phase-dropout CNN
    ax = axes[1, 1]
    e3 = f("E3", "E3_all_cnns_by_pattern.csv")
    pats = [
        ("complete", "All four phases"),
        ("drop_P", "No non-contrast"),
        ("drop_C1", "No arterial"),
        ("drop_C2", "No portal venous"),
        ("drop_C3", "No delayed"),
        ("P+C2", "Non-contrast + portal venous"),
        ("C2_only", "Portal venous only"),
    ]
    for i, (pat, _lab) in enumerate(pats):
        yy = len(pats) - 1 - i
        o = e3[(e3["model"] == "original") & (e3["pattern"] == pat)]["test_macro_auc"].iloc[0]
        d = e3[(e3["model"] == "D_phase_dropout") & (e3["pattern"] == pat)]["test_macro_auc"].iloc[
            0
        ]
        ax.plot([o, d], [yy, yy], color=BASE, lw=1.4, zorder=1)
        ax.plot(o, yy, "o", ms=5, color=S2, zorder=3)
        ax.plot(d, yy, "o", ms=5, color=S1, zorder=3)
    ax.set_yticks(range(len(pats)))
    ax.set_yticklabels([p[1] for p in pats][::-1])
    ax.set_xlim(0.5, 1.0)
    ax.set_xlabel("Held-out macro-AUC (n = 56)")
    grid_x(ax)
    ax.legend(
        handles=[
            Line2D([], [], color=S2, marker="o", lw=0, ms=5, label="Original CNN"),
            Line2D([], [], color=S1, marker="o", lw=0, ms=5, label="Phase-dropout CNN (main)"),
        ],
        loc="lower left",
        bbox_to_anchor=(0, 1.06),
        ncol=2,
        handletextpad=0.3,
        columnspacing=1.0,
        borderaxespad=0,
    )
    panel(ax, "D", "")
    save(fig, "Figure3_internal_performance")


# =================================================================================================
# Figure 5 — dataset artifacts in PLC-CECT (post hoc analyses of header facts and saved predictions)
# =================================================================================================
def figure_artefacts():
    H = f("E8b", "E9a_internal_header_shapes.csv", dtype={"patient_id": str})
    H["cls"] = H["class"].map({"HCC": "HCC", "ICC": "ICC", "CHCC": "cHCC-CCA"})
    mct = pd.read_csv(sorted(REV.glob("E4d_*/E4d_mct_facts.csv"))[-1], dtype={"patient_id": str})
    mct = mct[mct["size"].notna()].copy()
    mct["n_slices"] = mct["size"].map(lambda s: json.loads(s)[2])
    mct["dz"] = mct["spacing"].map(lambda s: json.loads(s)[2])
    mct["cls"] = np.where(mct["patient_id"].str.contains("b"), "HCC", "ICC")
    fig, axes = plt.subplots(
        2,
        2,
        figsize=(174 * MM, 122 * MM),
        gridspec_kw={"hspace": 0.6, "wspace": 0.42, "width_ratios": [1.55, 1]},
    )

    # A: slices per phase by class (internal)
    ax = axes[0, 0]
    phases = [("P", "Non-contrast"), ("C1", "Arterial"), ("C2", "Portal venous"), ("C3", "Delayed")]
    for i, (ph, _lab) in enumerate(phases):
        for j, c in enumerate(CLASSES):
            v = H[(H["phase"] == ph) & (H["cls"] == c)]["n_slices"].to_numpy()
            x = i + (j - 1) * 0.26
            b = ax.boxplot(
                v,
                positions=[x],
                widths=0.2,
                patch_artist=True,
                showfliers=False,
                medianprops={"color": "white", "lw": 1.2},
                whiskerprops={"color": CLASS_COL[c], "lw": 0.9},
                capprops={"color": CLASS_COL[c], "lw": 0.9},
            )
            b["boxes"][0].set(facecolor=CLASS_COL[c], edgecolor=CLASS_COL[c])
    ax.set_yscale("log")
    ax.set_yticks([20, 50, 100, 200, 300])
    ax.set_yticklabels(["20", "50", "100", "200", "300"])
    ax.set_xticks(range(4))
    ax.set_xticklabels([p[1] for p in phases])
    ax.set_ylabel("Slices per scan")
    grid_y(ax)
    ax.legend(
        handles=[plt.Rectangle((0, 0), 1, 1, color=CLASS_COL[c]) for c in CLASSES],
        labels=CLASSES,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.17),
        ncol=3,
        handlelength=1.0,
        borderaxespad=0,
        columnspacing=1.2,
    )
    panel(ax, "A", "PLC-CECT (internal), 278 patients")

    # B: MCT-LTDiag slices by class
    ax = axes[0, 1]
    for j, c in enumerate(["HCC", "ICC"]):
        v = mct[mct["cls"] == c]["n_slices"].to_numpy()
        b = ax.boxplot(
            v,
            positions=[j],
            widths=0.45,
            patch_artist=True,
            showfliers=False,
            medianprops={"color": "white", "lw": 1.2},
            whiskerprops={"color": CLASS_COL[c], "lw": 0.9},
            capprops={"color": CLASS_COL[c], "lw": 0.9},
        )
        b["boxes"][0].set(facecolor=CLASS_COL[c], edgecolor=CLASS_COL[c])
    a = roc_auc_score(mct["cls"] == "HCC", mct["n_slices"])
    a = max(a, 1 - a)
    ax.set_yscale("log")
    ax.set_yticks([20, 50, 100, 200, 300])
    ax.set_yticklabels(["20", "50", "100", "200", "300"])
    ax.set_ylim(15, 400)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["HCC", "ICC"])
    ax.set_ylabel("Slices per scan")
    grid_y(ax)
    thick = ", ".join(f"{v:g} mm" for v in sorted(mct["dz"].round(2).unique()))
    ax.text(
        0.5,
        0.97,
        f"slice thickness {thick}\nslice count alone: AUC {a:.2f}",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=6.5,
        color=INK2,
    )
    panel(ax, "B", "MCT-LTDiag (external), 203 patients")

    # C: what acquisition alone predicts (post hoc)
    ax = axes[1, 0]
    S = np.log(
        H.pivot(index="patient_id", columns="phase", values="n_slices")[["P", "C1", "C2", "C3"]]
    )
    yS = LABEL.loc[S.index].to_numpy()
    dev, test = S.index.isin(DEV), S.index.isin(TEST)

    def lr():
        return make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))

    rf = RandomForestClassifier(300, min_samples_leaf=5, random_state=42)
    held = {}
    for name, model in [("logistic", lr()), ("random forest", rf)]:
        model.fit(S[dev].to_numpy(), yS[dev])
        held[name] = macro_auc(yS[test], model.predict_proba(S[test].to_numpy()))
    m47 = f("E47", "E7b_internal_final_metrics.csv").set_index("model")
    cv = StratifiedKFold(5, shuffle=True, random_state=42)

    def logit(p):
        p = np.clip(p, 1e-6, 1 - 1e-6)
        return np.log(p / (1 - p))

    oof = PRED8B[
        (PRED8B["cohort"] == "internal_oof")
        & (PRED8B["model"] == "cnn_plus_radiomics: [ref] phase_dropout_CNN + radiomics_noshape")
    ].set_index("patient_id")
    oof = oof.assign(label=LABEL.loc[oof.index].to_numpy())
    hi = oof[oof["label"].isin([0, 1])]
    yh = (hi["label"] == 0).to_numpy().astype(int)
    sh = logit(hi["p_HCC"] / (hi["p_HCC"] + hi["p_ICC"])).to_numpy()
    Xh = S.loc[hi.index].to_numpy()
    s_only = cross_val_predict(lr(), Xh, yh, cv=cv, method="predict_proba")[:, 1]
    mid = (s_only > np.quantile(s_only, 0.25)) & (s_only < np.quantile(s_only, 0.75))
    items = [
        (
            "Slice counts only — 3 classes, held-out\n(logistic / random forest)",
            [held["logistic"], held["random forest"]],
            MUTED,
        ),
        (
            "CNN + radiomics — 3 classes, held-out",
            [m47.loc["cnn_plus_radiomics [phase_dropout_CNN]", "test_macro_auc"]],
            S1,
        ),
        ("Slice counts only — HCC vs ICC, out-of-fold", [roc_auc_score(yh, s_only)], MUTED),
        ("CNN + radiomics — HCC vs ICC, out-of-fold", [roc_auc_score(yh, sh)], S1),
        (
            "CNN + radiomics — HCC vs ICC where slice\n"
            f"counts are ambiguous (n = {int(mid.sum())})",
            [roc_auc_score(yh[mid], sh[mid])],
            S1,
        ),
        ("Slice count only — MCT-LTDiag HCC vs ICC", [a], MUTED),
    ]
    print(
        "  post hoc numbers (Figure dataset artefacts, panel C):",
        {it[0].replace("\n", " "): [round(v, 3) for v in it[1]] for it in items},
    )
    for i, (_lab, vals, col) in enumerate(items):
        yy = len(items) - 1 - i
        ax.plot([0.5, max(vals)], [yy, yy], color=GRID, lw=1.0, zorder=1)
        for v in vals:
            ax.plot(v, yy, "o", ms=5, color=col, zorder=3)
        ax.text(
            max(vals) + 0.012,
            yy,
            " / ".join(f"{v:.2f}" for v in vals),
            va="center",
            fontsize=6.5,
            color=INK2,
        )
    ax.set_yticks(range(len(items)))
    ax.set_yticklabels([it[0] for it in items][::-1], fontsize=6.5)
    ax.set_xlim(0.5, 1.04)
    ax.set_xlabel("AUC (macro-AUC for 3 classes)")
    grid_x(ax)
    panel(ax, "C", "Acquisition alone predicts the class internally (post hoc)")

    # D: removing the non-contrast phase hurts cHCC-CCA, not HCC vs ICC (post hoc, out-of-fold)
    ax = axes[1, 1]
    pairs = [
        ("CNN", "CNN phase_dropout_CNN [complete]", "CNN noP_CNN [noP]"),
        ("Radiomics", "radiomics radiomics_noshape", "radiomics radiomics_noP"),
        (
            "CNN + radiomics",
            "cnn_plus_radiomics: [ref] phase_dropout_CNN + radiomics_noshape",
            "cnn_plus_radiomics: E9: noP_CNN + radiomics_noP",
        ),
        (
            "Full fusion",
            "full_fusion: [ref] phase_dropout_CNN + radiomics_noshape",
            "full_fusion: E9: noP_CNN + radiomics_noP",
        ),
    ]

    def task_auc(model, task):
        d = PRED8B[(PRED8B["cohort"] == "internal_oof") & (PRED8B["model"] == model)].set_index(
            "patient_id"
        )
        lab = LABEL.loc[d.index].to_numpy()
        if task == "hcc_icc":
            k = np.isin(lab, [0, 1])
            return roc_auc_score(
                lab[k] == 0, (d["p_HCC"] / (d["p_HCC"] + d["p_ICC"])).to_numpy()[k]
            )
        return roc_auc_score(lab == 2, d["p_CHCC"].to_numpy())

    for i, (_name, a_, b_) in enumerate(pairs):
        for dy, task, col in [(0.15, "hcc_icc", S1), (-0.15, "chcc", S3)]:
            yy = len(pairs) - 1 - i + dy
            w, wo = task_auc(a_, task), task_auc(b_, task)
            ax.annotate(
                "",
                xy=(wo, yy),
                xytext=(w, yy),
                arrowprops={"arrowstyle": "-|>", "color": col, "lw": 1.3, "mutation_scale": 7},
            )
            ax.plot(w, yy, "o", ms=4.5, color=col, zorder=3)
    ax.set_yticks(range(len(pairs)))
    ax.set_yticklabels([p[0] for p in pairs][::-1])
    ax.set_xlim(0.72, 1.0)
    ax.set_xlabel("Out-of-fold AUC: all phases → without non-contrast")
    grid_x(ax)
    ax.legend(
        handles=[
            Line2D([], [], color=S1, marker="o", lw=1.3, ms=4.5, label="HCC vs ICC"),
            Line2D([], [], color=S3, marker="o", lw=1.3, ms=4.5, label="cHCC-CCA vs rest"),
        ],
        loc="lower left",
        bbox_to_anchor=(0, 1.06),
        ncol=2,
        handlelength=1.6,
        borderaxespad=0,
    )
    panel(ax, "D", "")
    save(fig, "Figure5_dataset_artifacts")


# =================================================================================================
# Figure — tumour size and crop truncation (E4a, E4b; E4d panel added when available)
# =================================================================================================
def figure_size():
    tr = f("E47", "E4a_truncation_per_patient_phase.csv", dtype={"patient_id": str})
    st = f("E47", "E4b_internal_by_size_and_truncation.csv")
    e4d = sorted(p for p in REV.glob("E4d_*") if (p / "summary.json").exists())
    fig = plt.figure(figsize=(174 * MM, (130 if e4d else 64) * MM))
    gs = fig.add_gridspec(
        2 if e4d else 1, 2, hspace=0.75, wspace=0.42, height_ratios=[1, 0.8] if e4d else [1]
    )
    axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])] + (
        [fig.add_subplot(gs[1, :])] if e4d else []
    )
    ax = axes[0]
    tr["cls"] = tr["patient_id"].map(lambda p: CLASSES[LABEL.loc[p]])
    c2 = tr[tr["phase"] == "C2"]
    rcol = [c for c in tr.columns if "retention" in c][0]
    rng = np.random.default_rng(2)
    for j, c in enumerate(CLASSES):
        v = c2[c2["cls"] == c][rcol].to_numpy()
        ax.scatter(
            j + rng.uniform(-0.2, 0.2, len(v)), v, s=7, color=CLASS_COL[c], alpha=0.6, linewidths=0
        )
        ax.text(j, 1.05, f"{(v < 0.9).sum()}/{len(v)}", ha="center", fontsize=6.5, color=INK2)
    ax.axhline(0.9, color=MUTED, lw=0.8, ls=(0, (3, 2)))
    ax.set_xticks(range(3))
    ax.set_xticklabels(CLASSES)
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("Tumor fraction inside the 96³ crop")
    grid_y(ax)
    panel(ax, "A", "Crop truncation, portal venous (numbers: < 90% in crop)")
    ax = axes[1]
    order = [("small", "Small"), ("medium", "Medium"), ("large", "Large")]
    for key, name, col in [
        ("phase_dropout_CNN", "CNN", S1),
        ("radiomics_noshape", "Radiomics", S2),
        ("cnn_plus_radiomics [phase_dropout_CNN]", "CNN + radiomics", S3),
        ("full_fusion [phase_dropout_CNN]", "Full fusion", S4),
    ]:
        d = st[
            (st["model"] == key) & (st["split"] == "oof_222") & (st["grouping"] == "size_third")
        ].set_index("group")
        ax.plot(
            range(3),
            [d.loc[g, "macro_auc"] for g, _ in order],
            "-o",
            color=col,
            lw=1.6,
            ms=4.5,
            label=name,
        )
    ax.set_xticks(range(3))
    ax.set_xticklabels([o[1] for o in order])
    ax.set_xlabel("Portal-venous tumor size (thirds)")
    ax.set_ylabel("Out-of-fold macro-AUC (222)")
    ax.set_ylim(0.85, 1.0)
    grid_y(ax)
    ax.legend(
        loc="lower left",
        bbox_to_anchor=(0, 1.06),
        ncol=2,
        handlelength=1.4,
        borderaxespad=0,
        columnspacing=0.8,
    )
    panel(ax, "B", "")
    if e4d:
        ax = axes[2]
        r = pd.read_csv(e4d[-1] / "E4d_internal_results.csv").set_index("model")
        m = pd.read_csv(e4d[-1] / "E4d_mct203_results.csv").set_index("model")
        z = (
            pd.read_csv(e4d[-1] / "E4d_internal_by_size_third.csv")
            .query("third == 'large'")
            .set_index("model")
        )
        rows = [
            (
                "CNN, held-out",
                "CNN phase_dropout_CNN [complete]",
                "CNN adaptive_CNN [complete]",
                r,
                "test_macro_auc",
            ),
            (
                "CNN, cross-validation",
                "CNN phase_dropout_CNN [complete]",
                "CNN adaptive_CNN [complete]",
                r,
                "cv_mean",
            ),
            (
                "CNN, largest third (OOF)",
                "CNN phase_dropout_CNN [complete]",
                "CNN adaptive_CNN [complete]",
                z,
                "oof_macro_auc",
            ),
            (
                "CNN + radiomics, held-out",
                "cnn_plus_radiomics: phase_dropout_CNN",
                "cnn_plus_radiomics: adaptive_CNN",
                r,
                "test_macro_auc",
            ),
            ("CNN, MCT-LTDiag (external)", "CNN phase_dropout_CNN", "CNN adaptive_CNN", m, "auc"),
        ]
        for i, (_lab, a_, b_, src, col_) in enumerate(rows):
            yy = len(rows) - 1 - i
            va, vb = src.loc[a_, col_], src.loc[b_, col_]
            ax.plot([va, vb], [yy, yy], color=BASE, lw=1.4, zorder=1)
            ax.plot(va, yy, "o", ms=5, color=S1, zorder=3)
            ax.plot(vb, yy, "o", ms=5, color=S2, zorder=3)
        ax.set_yticks(range(len(rows)))
        ax.set_yticklabels([r_[0] for r_ in rows][::-1])
        ax.set_xlim(0.5, 1.0)
        ax.set_xlabel("AUC (macro-AUC internally)")
        grid_x(ax)
        ax.legend(
            handles=[
                Line2D([], [], color=S1, marker="o", lw=0, label="Fixed 96³ crop (main)"),
                Line2D([], [], color=S2, marker="o", lw=0, label="Adaptive crop"),
            ],
            loc="lower left",
            bbox_to_anchor=(0, 1.04),
            ncol=2,
            borderaxespad=0,
        )
        panel(ax, "C", "")
    save(fig, "Figure4_size_truncation")


# =================================================================================================
# Figure — external validation on MCT-LTDiag (HCC vs ICC)
# =================================================================================================
def figure_external():
    p80 = f("E8a", "E8_0_E6_203_predictions.csv", dtype={"patient_id": str})
    p80 = p80[p80["variant"] == "primary"]
    fig = plt.figure(figsize=(174 * MM, 165 * MM))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.45], hspace=0.45, wspace=1.05)
    ax = fig.add_subplot(gs[0, 0])
    for key, name, col in [
        ("phase_dropout_CNN", "CNN", S1),
        ("radiomics_noshape", "Radiomics", S2),
        ("cnn_plus_radiomics [phase_dropout_CNN]", "CNN + radiomics", S3),
        ("full_fusion [phase_dropout_CNN]", "Full fusion", S4),
    ]:
        d = p80[p80["model"] == key]
        y = (d["true_class"] == "HCC").to_numpy()
        s = (d["p_HCC"] / (d["p_HCC"] + d["p_ICC"])).to_numpy()
        fpr, tpr, _ = roc_curve(y, s)
        ax.plot(fpr, tpr, color=col, lw=1.6, label=f"{name}  {roc_auc_score(y, s):.3f}")
    sel = pd.read_csv(
        LP / "external_validation" / "MCT-LTDiag" / "metadata" / "selected_HCC_ICC_patients.csv",
        dtype=str,
    )
    male = sel["patient_sex"].str.strip().str.upper().eq("M").astype(int).to_numpy()
    yh = (sel["type"] == "HCC").to_numpy()
    fpr, tpr, _ = roc_curve(yh, male)
    ax.plot(
        fpr,
        tpr,
        color=INK2,
        lw=1.0,
        ls=(0, (1, 1.5)),
        marker="o",
        ms=3,
        label=f"Sex alone  {roc_auc_score(yh, male):.3f}",
    )
    ax.plot([0, 1], [0, 1], color=MUTED, lw=0.8, ls=(0, (3, 2)))
    ax.set_xlabel("1 − specificity (ICC called HCC)")
    ax.set_ylabel("Sensitivity (HCC)")
    ax.set_aspect("equal")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.legend(
        loc="upper left",
        bbox_to_anchor=(1.03, 1.0),
        title="AUC",
        title_fontsize=7,
        handlelength=1.4,
        alignment="left",
        borderaxespad=0,
    )
    panel(ax, "A", "MCT-LTDiag, 103 HCC vs 100 ICC")

    ax = fig.add_subplot(gs[0, 1])
    rel = f("E47", "E7c_reliability_tables.csv")
    cal = f("E47", "E7c_calibration.csv")
    key = "cnn_plus_radiomics [phase_dropout_CNN]"
    for cohort, target, col, name in [
        ("internal_test_56", "HCC_vs_rest", S1, "Internal held-out (HCC vs rest)"),
        ("MCT_LTDiag_203", "HCC_vs_ICC (renormalised)", S2, "MCT-LTDiag (HCC vs ICC)"),
    ]:
        d = rel[
            (rel["model"] == key)
            & (rel["cohort"] == cohort)
            & (rel["target"] == target)
            & (rel["n"] > 0)
        ]
        c = cal[(cal["model"] == key) & (cal["cohort"] == cohort) & (cal["target"] == target)].iloc[
            0
        ]
        ax.plot(
            d["mean_predicted"],
            d["observed"],
            "-o",
            color=col,
            lw=1.6,
            ms=4.5,
            label=f"{name}\nintercept {c['intercept']:.2f}, slope {c['slope']:.2f}",
        )
    ax.plot([0, 1], [0, 1], color=MUTED, lw=0.8, ls=(0, (3, 2)))
    ax.set_xlabel("Predicted probability of HCC")
    ax.set_ylabel("Observed proportion HCC")
    ax.set_aspect("equal")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.legend(
        loc="upper left",
        bbox_to_anchor=(1.03, 1.0),
        handlelength=1.4,
        fontsize=6.3,
        borderaxespad=0,
        labelspacing=1.0,
    )
    panel(ax, "B", "Calibration, CNN + radiomics")

    ax = fig.add_subplot(gs[1, :])
    r8 = f("E8b", "E8b_E9_mct203_results.csv").set_index("model")
    r8a = f("E8a", "E8a_mct203_results.csv").set_index("model")
    groups = [
        (
            "CNN",
            [
                ("Phase-dropout CNN (reference)", r8, "CNN phase_dropout_CNN"),
                ("+ test-time harmonization", r8, "CNN phase_dropout_CNN + harmonisation"),
                ("Scanner-variation training", r8, "CNN DR_CNN"),
                ("Scanner-variation + harmonization", r8, "CNN DR_CNN + harmonisation"),
                ("Without non-contrast phase", r8, "CNN noP_CNN"),
            ],
        ),
        (
            "Radiomics",
            [
                ("No-shape radiomics (reference)", r8, "radiomics radiomics_noshape"),
                ("ComBat harmonization", r8a, "radiomics_noshape_ComBat"),
                ("Perturbation-robust features", r8, "radiomics radiomics_robust"),
                ("Robust + ComBat", r8, "radiomics radiomics_robust_ComBat"),
                ("Without non-contrast phase", r8, "radiomics radiomics_noP"),
            ],
        ),
        (
            "CNN + radiomics",
            [
                (
                    "Reference (pre-specified primary)",
                    r8,
                    "cnn_plus_radiomics: [ref] phase_dropout_CNN + radiomics_noshape",
                ),
                (
                    "Scanner-variation CNN + harmonization",
                    r8,
                    "cnn_plus_radiomics: E8b: DR_CNN + harmonisation + radiomics_noshape",
                ),
                (
                    "Mitigated fusion (pre-specified)",
                    r8,
                    "cnn_plus_radiomics: E8c (pre-specified): DR_CNN + radiomics_robust_ComBat",
                ),
                (
                    "Mitigated fusion without ComBat (post hoc)",
                    r8,
                    "cnn_plus_radiomics: E8c (post hoc): DR_CNN + radiomics_robust",
                ),
                (
                    "Without non-contrast phase",
                    r8,
                    "cnn_plus_radiomics: E9: noP_CNN + radiomics_noP",
                ),
            ],
        ),
        (
            "Full fusion (+ age, sex)",
            [
                ("Reference", r8, "full_fusion: [ref] phase_dropout_CNN + radiomics_noshape"),
                (
                    "Scanner-variation CNN + harmonization",
                    r8,
                    "full_fusion: E8b: DR_CNN + harmonisation + radiomics_noshape",
                ),
                (
                    "Mitigated fusion (pre-specified)",
                    r8,
                    "full_fusion: E8c (pre-specified): DR_CNN + radiomics_robust_ComBat",
                ),
                ("Without non-contrast phase", r8, "full_fusion: E9: noP_CNN + radiomics_noP"),
            ],
        ),
    ]
    y, ticks, labels = 0, [], []
    for _gi, (gname, items) in enumerate(groups):
        y += 1  # the group heading gets its own row
        ax.text(
            0.302,
            -y,
            gname,
            fontsize=7.2,
            fontweight="bold",
            color=INK,
            va="center",
            transform=ax.transData,
        )
        for lab, src, key in items:
            y += 1
            row = src.loc[key]
            est, lo, hi = (
                row["auc"],
                row["delong_low" if "delong_low" in row else "auc_delong_low"],
                row["delong_high" if "delong_high" in row else "auc_delong_high"],
            )
            ref = lab.startswith(
                ("Phase-dropout CNN (reference)", "No-shape radiomics (reference)", "Reference")
            )
            col = S1 if ref else INK2
            ax.plot([lo, hi], [-y, -y], color=col, lw=1.5, solid_capstyle="round")
            ax.plot(est, -y, "o", ms=4.8, color=col, zorder=3)
            ax.text(
                0.905, -y, f"{est:.3f} ({lo:.3f}–{hi:.3f})", va="center", fontsize=6.4, color=INK2
            )
            ticks.append(-y)
            labels.append(lab)
        y += 0.4
    ax.axvline(0.5, color=MUTED, lw=0.8, ls=(0, (3, 2)))
    ax.set_yticks(ticks)
    ax.set_yticklabels(labels, fontsize=6.6)
    ax.set_xlim(0.3, 1.0)
    ax.set_ylim(-(y + 0.3), -0.4)
    ax.set_xlabel("MCT-LTDiag HCC-vs-ICC AUC (DeLong 95% CI); every variant evaluated once")
    grid_x(ax)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    panel(
        ax,
        "C",
        "Mitigation attempts: none improves external discrimination significantly "
        "(smallest BH-adjusted p = 0.29)",
    )
    save(fig, "Figure7_external_MCT")


# =================================================================================================
# Figure — HCC-TACE-Seg: effect of the pipeline corrections (HCC sensitivity, clean 89)
# =================================================================================================
def figure_tace():
    t = f("E5c", "E5c_results.csv")
    t = t[t["subset"] == "clean_89"]
    variants = [
        ("corrected_-200_200", "Repaired pipeline (E5),\nintensity window corrected"),
        ("axis_fixed_iso1mm", "+ axis order fixed\n(1 mm isotropic, as submitted)"),
        ("axis_fixed_E6rules", "+ axis order fixed\n(internal geometry; E5c primary)"),
    ]
    series = [
        ("phase_dropout_CNN", "CNN", S1),
        ("radiomics_noshape", "Radiomics", S2),
        ("cnn_plus_radiomics [phase_dropout_CNN]", "CNN + radiomics", S3),
        ("full_fusion [phase_dropout_CNN] {observed_TCIA}", "Full fusion (observed age, sex)", S4),
    ]
    fig, ax = plt.subplots(figsize=(140 * MM, 72 * MM))
    for k, (key, name, col) in enumerate(series):
        d = t[t["model"] == key].set_index("variant")
        xs = np.arange(len(variants)) + (k - 1.5) * 0.17
        pts = [
            (x, d.loc[v]) for x, (v, _) in zip(xs, variants, strict=False) if v in d.index
        ]  # radiomics/fusions never used the historical window
        for x, r in pts:
            ax.plot([x, x], [r["ci_low"], r["ci_high"]], color=col, lw=1.5, solid_capstyle="round")
        ax.plot(
            [x for x, _ in pts],
            [r["hcc_sensitivity"] for _, r in pts],
            "o",
            ms=5,
            color=col,
            label=name,
            zorder=3,
        )
    ax.set_xticks(range(len(variants)))
    ax.set_xticklabels([v[1] for v in variants])
    ax.set_ylim(0, 1.02)
    ax.set_ylabel("HCC sensitivity (n = 89;\nClopper–Pearson 95% CI)")
    grid_y(ax)
    ax.legend(
        loc="lower left",
        bbox_to_anchor=(0, 1.02),
        ncol=4,
        handletextpad=0.3,
        columnspacing=1.0,
        borderaxespad=0,
    )
    ax.text(
        1.0,
        -0.32,
        "HCC-TACE-Seg contains only HCC: sensitivity alone cannot show discrimination "
        "(see MCT-LTDiag).",
        transform=ax.transAxes,
        ha="right",
        fontsize=6.4,
        color=MUTED,
    )
    save(fig, "Figure_HCC_TACE_Seg")


# =================================================================================================
# Figure 1 — study design, drawn to match the Methods (replaces the submitted Figures 1, 2 and 4)
# =================================================================================================
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

TINT_INT, TINT_EXT, TINT_M = "#e9f1fb", "#fdefe7", "#f3f2ee"


def _box(ax, x, y, w, h, lines, fc, ec=BASE, title_col=INK, fs=6.4):
    ax.add_patch(
        FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.4", fc=fc, ec=ec, lw=0.7)
    )
    yy = y + 2.6
    for i, ln in enumerate(lines):
        bold = i == 0
        ax.text(
            x + 1.8,
            yy,
            ln,
            fontsize=fs + (0.3 if bold else 0),
            fontweight="bold" if bold else "normal",
            color=title_col if bold else INK2,
            va="top",
            ha="left",
        )
        yy += 3.35 if bold else 3.05


def _arrow(ax, x0, y0, x1, y1, col=MUTED):
    ax.add_patch(
        FancyArrowPatch(
            (x0, y0),
            (x1, y1),
            arrowstyle="-|>",
            mutation_scale=7,
            lw=0.9,
            color=col,
            shrinkA=0,
            shrinkB=0,
        )
    )


def _path_arrow(ax, pts, col=MUTED):
    xs, ys = zip(*pts, strict=False)
    ax.plot(xs[:-1] + (xs[-1],), ys[:-1] + (ys[-1],), color=col, lw=0.9, solid_capstyle="butt")
    _arrow(ax, xs[-2], ys[-2], xs[-1], ys[-1], col)


def figure_design():
    W, H = 174, 99
    fig = plt.figure(figsize=(W * MM, H * MM))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")
    cols = [
        (1.5, 43, "1  Cohorts"),
        (48.5, 38, "2  Preprocessing"),
        (90.5, 41, "3  Models"),
        (135.5, 37.5, "4  Evaluation"),
    ]
    for x, w, t in cols:
        ax.text(x, 3.2, t, fontsize=7.6, fontweight="bold", va="center", color=INK)
        ax.plot([x, x + w], [6.2, 6.2], color=BASE, lw=0.8)
    # 1 cohorts
    _box(
        ax,
        1.5,
        9,
        43,
        19,
        [
            "PLC-CECT (internal; one hospital)",
            "278: 94 HCC, 99 ICC, 85 cHCC-CCA",
            "non-contrast, arterial, portal venous",
            "and delayed CT (public, 0–255)",
            "age and sex",
        ],
        TINT_INT,
        S1,
    )
    _box(
        ax,
        1.5,
        30.5,
        22.5,
        12.5,
        ["Development 222", "5 folds; 5 × 5", "repeated CV"],
        TINT_INT,
        S1,
    )
    _box(
        ax,
        26,
        30.5,
        18.5,
        12.5,
        ["Held-out 56", "never used for", "fitting or tuning"],
        TINT_INT,
        S1,
    )
    _box(
        ax,
        1.5,
        47,
        43,
        19,
        [
            "MCT-LTDiag (external hospital)",
            "203: 103 HCC, 100 ICC",
            "four registered phases, 5 mm slices",
            "observed age and sex",
            "no cHCC-CCA: HCC vs ICC only",
        ],
        TINT_EXT,
        S2,
    )
    _box(
        ax,
        1.5,
        68.5,
        43,
        16,
        [
            "HCC-TACE-Seg (stress test)",
            "89 HCC (clean); all 103 reported",
            "HCC only; no delayed phase",
            "phases from series descriptions",
        ],
        TINT_EXT,
        S2,
    )
    ax.text(
        1.5,
        88.5,
        "External cohorts: frozen models; no fitting,\n"
        "threshold tuning or recalibration\non external data.",
        fontsize=6.1,
        color=MUTED,
        va="top",
        linespacing=1.35,
    )
    # 2 preprocessing
    _box(
        ax,
        48.5,
        9,
        38,
        21.5,
        [
            "Per phase, internal",
            "CT × liver mask (as released)",
            "96³-voxel crop centred on that",
            "phase's tumor (no registration;",
            "no resampling)",
        ],
        TINT_M,
    )
    _box(
        ax,
        53,
        33,
        33.5,
        14,
        ["CNN input", "4 phases stacked: 4 × 96³", "per-phase z-score"],
        TINT_M,
    )
    _box(
        ax,
        48.5,
        49.5,
        38,
        15.5,
        [
            "Radiomics input",
            "tumor mask inside each crop",
            "107 features per phase; 56 shape",
            "features removed → 372",
        ],
        TINT_M,
    )
    _box(
        ax,
        48.5,
        68.5,
        38,
        22,
        [
            "External adapter",
            "orientation matched to training",
            "in-plane 0.78 mm, slices kept",
            "−200…200 HU → 0–255",
            "one crop for registered phases",
        ],
        TINT_EXT,
        S2,
    )
    # 3 models
    _box(
        ax,
        90.5,
        9,
        35,
        21.5,
        [
            "CNN (main)",
            "MONAI 3D ResNet-18",
            "phase dropout: random phases",
            "zeroed in training; inner-split",
            "checkpoint; 5 fold models",
        ],
        TINT_M,
    )
    _box(
        ax,
        90.5,
        33,
        35,
        16.5,
        [
            "Radiomics",
            "per training fold: variance,",
            "|r| > 0.95, top 30 ANOVA-F",
            "→ LightGBM; 5 fold models",
        ],
        TINT_M,
    )
    _box(
        ax,
        90.5,
        53,
        41,
        16.5,
        [
            "Late fusion (logistic, out-of-fold)",
            "CNN + radiomics: 6 probabilities",
            "(pre-specified primary model)",
            "Full fusion: + age and sex (8 inputs)",
        ],
        TINT_M,
    )
    _box(
        ax,
        90.5,
        72,
        41,
        18.5,
        [
            "Also reported",
            "original CNN; CNN without the",
            "non-contrast phase; adaptive-crop",
            "and scanner-variation CNNs;",
            "robust and ComBat radiomics",
        ],
        "white",
    )
    # 4 evaluation
    _box(
        ax,
        135.5,
        9,
        37.5,
        25,
        [
            "Internal",
            "held-out macro-AUC, bootstrap CI",
            "DeLong + Benjamini–Hochberg",
            "paired bootstrap; calibration",
            "5 × 5 repeated CV; size thirds",
            "missing-phase patterns",
        ],
        TINT_INT,
        S1,
    )
    _box(
        ax,
        135.5,
        37,
        37.5,
        25,
        [
            "Dataset audit (1,112 scans)",
            "file and mask census",
            "slice-thickness estimate",
            "models without non-contrast",
            "counterfactual resampling test",
            "Grad-CAM attention measures",
        ],
        TINT_INT,
        S1,
    )
    _box(
        ax,
        135.5,
        65,
        37.5,
        25.5,
        [
            "External",
            "MCT-LTDiag: HCC-vs-ICC AUC",
            "(DeLong CI), calibration,",
            "each mitigation once",
            "HCC-TACE-Seg: HCC sensitivity",
            "after each pipeline correction",
        ],
        TINT_EXT,
        S2,
    )
    # arrows
    _arrow(ax, 44.8, 18.5, 48.2, 18.5)
    _arrow(ax, 44.8, 76.5, 48.2, 79.5)
    _arrow(ax, 69, 30.7, 69, 32.8)
    _path_arrow(ax, [(50.7, 30.7), (50.7, 49.3)])
    _arrow(ax, 86.8, 40, 90.2, 19.5)
    _arrow(ax, 86.8, 57, 90.2, 41)
    _path_arrow(ax, [(125.7, 19.5), (128.5, 19.5), (128.5, 52.8)])
    ax.plot([125.7, 128.5], [41, 41], color=MUTED, lw=0.9)
    _arrow(ax, 131.8, 61, 135.2, 21.5)
    _arrow(ax, 131.8, 61, 135.2, 49.5)
    _arrow(ax, 131.8, 61, 135.2, 77.5)
    save(fig, "Figure1_study_design")


# =================================================================================================
# Figure 2 — example model inputs (patients nearest the class median tumor size)
# =================================================================================================
PHASE_NAMES = [
    ("P", "Non-contrast"),
    ("C1", "Arterial"),
    ("C2", "Portal venous"),
    ("C3", "Delayed"),
]


def _tile(ax, img, mask, contour_col=S4, vmax=255):
    ax.imshow(img, cmap="gray", vmin=0, vmax=vmax, interpolation="nearest")
    if mask is not None and mask.any():
        ax.contour(mask.astype(float), levels=[0.5], colors=[contour_col], linewidths=0.7)
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)


def figure_examples():
    ex = np.load(REV / RUN["F2"] / "F2_examples.npz")
    meta = {m["tag"]: m for m in json.loads((REV / RUN["F2"] / "F2_examples.json").read_text())}
    H = f("E8b", "E9a_internal_header_shapes.csv", dtype={"patient_id": str}).pivot(
        index="patient_id", columns="phase", values="n_slices"
    )
    mct = f("E4d", "E4d_mct_facts.csv", dtype={"patient_id": str}).set_index("patient_id")
    cols = [
        ("fig2_internal_HCC", "PLC-CECT\nHCC"),
        ("fig2_internal_ICC", "PLC-CECT\nICC"),
        ("fig2_internal_CHCC", "PLC-CECT\ncHCC-CCA"),
        ("fig2_mct_HCC", "MCT-LTDiag\nHCC"),
        ("fig2_mct_ICC", "MCT-LTDiag\nICC"),
    ]
    fig, axes = plt.subplots(
        4, 5, figsize=(150 * MM, 132 * MM), gridspec_kw={"wspace": 0.06, "hspace": 0.06}
    )
    for c, (tag, head) in enumerate(cols):
        pid = meta[tag]["patient_id"]
        ct, tm = ex[f"{tag}_ct"], ex[f"{tag}_tm"]
        internal = "internal" in tag
        for r, (ph, phname) in enumerate(PHASE_NAMES):
            ax = axes[r, c]
            _tile(ax, ct[r], tm[r])
            if internal:
                lab = f"{int(H.loc[pid, ph])} slices"
            else:
                lab = f"{int(json.loads(mct.loc[pid, 'size'])[2])} × 5 mm"
            ax.text(
                0.03,
                0.03,
                lab,
                transform=ax.transAxes,
                fontsize=5.8,
                color="white",
                va="bottom",
                ha="left",
                bbox={"boxstyle": "round,pad=0.15", "fc": (0, 0, 0, 0.55), "ec": "none"},
            )
            if c == 0:
                ax.set_ylabel(phname, fontsize=7, color=INK, labelpad=4)
        axes[0, c].set_title(f"{head}\n{pid}", fontsize=7, color=INK, pad=4, linespacing=1.15)
    save(fig, "Figure2_example_inputs")


# =================================================================================================
# Figure 6 — counterfactual slice-resampling test with stored-voxel evidence (seeded patients)
# =================================================================================================
def _load_nii(path):
    import gzip
    import struct

    raw = gzip.open(path, "rb").read()
    h = raw[:348]
    dim = struct.unpack("<8h", h[40:56])
    dt = struct.unpack("<h", h[70:72])[0]
    off = int(struct.unpack("<f", h[108:112])[0])
    dtype = {2: np.uint8, 4: np.int16, 8: np.int32, 16: np.float32, 64: np.float64, 512: np.uint16}[
        dt
    ]
    shape = tuple(dim[1 : dim[0] + 1])
    n = int(np.prod(shape))
    a = (
        np.frombuffer(raw[off : off + n * np.dtype(dtype).itemsize], dtype=dtype)
        .reshape(shape, order="F")
        .astype(np.float32)
    )
    while a.ndim > 3:
        a = a.mean(axis=-1)  # 3-channel files: the Week 2 loader averages the channels
    return a


def figure_counterfactual(raw_dir=None, e10_dir=None):
    raw_dir = raw_dir or ARGS.raw_dir
    e10_dir = e10_dir or (REV / "E10_20261019T031225Z")
    E = pd.read_csv(Path(e10_dir) / "E10c_effects.csv")
    E = E[E["subset"] == "all 278"]
    Pr = pd.read_csv(Path(e10_dir) / "E10c_predictions.csv", dtype={"patient_id": str})
    Pr["y"] = Pr["patient_id"].map(LABEL)
    fig = plt.figure(figsize=(174 * MM, 168 * MM))
    gs = fig.add_gridspec(
        2, 2, height_ratios=[0.9, 1.25], width_ratios=[1.12, 1], hspace=0.32, wspace=0.62
    )
    # A: stored-voxel coronal views through the tumor centre of the first seeded evidence
    # patient of each class (the run's evidence folder lists them as <id>_<class>_P_vs_C2.png)
    first = {}
    for path in sorted((Path(e10_dir) / "evidence").glob("*_P_vs_C2.png")):
        pid, cls = path.name.split("_")[:2]
        first.setdefault(cls, pid)
    sub = gs[0, :].subgridspec(2, 2, wspace=0.08, hspace=0.25)
    for c, (pid, cname) in enumerate([(first["HCC"], "HCC"), (first["CHCC"], "cHCC-CCA")]):
        for r, (ph, phname) in enumerate([("P", "non-contrast"), ("C2", "portal venous")]):
            ct = _load_nii(Path(raw_dir) / f"{pid}_{ph}_ct.nii.gz")
            tm = _load_nii(Path(raw_dir) / f"{pid}_{ph}_mask.nii.gz") > 0
            jj = int(round(np.nonzero(tm)[1].mean()))
            img, msk = ct[40:472, jj, :].T, tm[40:472, jj, :].T
            ax = fig.add_subplot(sub[r, c])
            ax.imshow(img, cmap="gray", vmin=0, vmax=255, aspect="equal", interpolation="nearest")
            if msk.any():
                ax.contour(msk.astype(float), levels=[0.5], colors=[S4], linewidths=0.7)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_ylim(140, 0)
            for sp in ax.spines.values():
                sp.set_visible(False)
            ax.set_title(
                f"{cname} {pid}, {phname}: {ct.shape[2]} slices",
                fontsize=6.8,
                color=INK,
                loc="left",
                pad=2,
            )
            if r == 0 and c == 0:
                ax.text(
                    -0.02,
                    1.25,
                    "A",
                    transform=ax.transAxes,
                    fontsize=10,
                    fontweight="bold",
                    ha="right",
                    va="bottom",
                )
    # B: effect sizes in the expected direction
    ax = fig.add_subplot(gs[1, 0])
    tests = [
        ("slice density: HCC scans made ICC-like", "HCC → ICC-like slice density"),
        ("slice density: ICC scans made HCC-like", "ICC → HCC-like slice density"),
        ("non-contrast artefact injected (HCC, ICC)", "Non-contrast artifact injected"),
        ("non-contrast artefact repaired (cHCC-CCA)", "Non-contrast artifact repaired"),
    ]
    mods = [("CNN", S1), ("radiomics", S2), ("CNN + radiomics", S3)]
    y, ticks, labels = 0, [], []
    for t, tname in tests:
        y += 0.7
        ax.text(
            -0.5,
            -y,
            tname,
            fontsize=6.8,
            fontweight="bold",
            va="center",
            ha="left",
            color=INK,
            transform=ax.get_yaxis_transform(),
        )
        for m, col in mods:
            y += 1
            r = E[(E["model"] == m) & (E["test"] == t)].iloc[0]
            sg = r["expected_sign"]
            est = sg * r["mean_shift_vs_smoothing_control"]
            lo, hi = sorted([sg * r["ci_low"], sg * r["ci_high"]])
            passes = bool(r["meets_rule"]) and bool(r["smoothing_control_ok"])
            ax.plot([lo, hi], [-y, -y], color=col, lw=1.5, solid_capstyle="round")
            ax.plot(est, -y, "o", ms=5, mfc=col if passes else "white", mec=col, mew=1.3, zorder=3)
            ax.plot(
                r["smoothing_control_mean_abs_change"],
                -y,
                marker="|",
                ms=7,
                mew=1.4,
                color=INK2,
                zorder=4,
            )
            ticks.append(-y)
            labels.append({"radiomics": "Radiomics"}.get(m, m))
        y += 0.3
    ax.axvline(0, color=MUTED, lw=0.8)
    ax.axvline(0.05, color=MUTED, lw=0.8, ls=(0, (3, 2)))
    ax.set_yticks(ticks)
    ax.set_yticklabels(labels, fontsize=6.6)
    ax.set_xlim(-0.4, 1.1)
    ax.set_ylim(-(y + 0.4), -0.2)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    grid_x(ax)
    ax.set_xlabel(
        "Shift toward the simulated class vs matched\n"
        "smoothing control (mean, bootstrap 95% CI; n = 278)"
    )
    ax.legend(
        handles=[
            Line2D(
                [],
                [],
                color=INK2,
                marker="o",
                lw=0,
                ms=5,
                label="meets every pre-specified criterion",
            ),
            Line2D([], [], color=INK2, marker="o", mfc="white", lw=0, ms=5, label="not claimed"),
            Line2D(
                [],
                [],
                color=INK2,
                marker="|",
                lw=0,
                ms=7,
                mew=1.4,
                label="smoothing control alone (|change|)",
            ),
        ],
        loc="lower left",
        bbox_to_anchor=(-0.5, 1.0),
        ncol=1,
        borderaxespad=0,
        handletextpad=0.4,
        labelspacing=0.3,
    )
    ax.text(
        -0.52,
        1.19,
        "B",
        transform=ax.transAxes,
        fontsize=10,
        fontweight="bold",
        ha="right",
        va="bottom",
    )
    # C: what the CNN predicted
    ax = fig.add_subplot(gs[1, 1])
    conds = [
        ("swap", [0], "HCC scans → ICC-like density (94)"),
        ("swap", [1], "ICC scans → HCC-like density (99)"),
        ("inject", [0, 1], "Artifact injected, HCC + ICC (193)"),
        ("repair", [2], "Artifact repaired, cHCC-CCA (85)"),
    ]
    y, ticks, labels = 0, [], []
    for cond, cls, cname in conds:
        y += 0.8
        ax.text(0, -y, cname, fontsize=6.6, fontweight="bold", va="center", color=INK, zorder=5)
        for state, sname in [
            ("control", "unchanged"),
            (cond + "_smooth", "smoothing control"),
            (cond, "counterfactual"),
        ]:
            y += 1
            q = Pr[(Pr["model"] == "CNN") & (Pr["condition"] == state) & (Pr["y"].isin(cls))]
            cnt = np.bincount(q[P3].to_numpy().argmax(1), minlength=3)
            left = 0
            for k in range(3):
                ax.barh(
                    -y,
                    cnt[k],
                    left=left,
                    height=0.72,
                    color=CLASS_COL[CLASSES[k]],
                    edgecolor="white",
                    lw=0.4,
                )
                if cnt[k] >= 9:
                    ax.text(
                        left + cnt[k] / 2,
                        -y,
                        str(cnt[k]),
                        ha="center",
                        va="center",
                        fontsize=5.8,
                        color="white",
                    )
                left += cnt[k]
            ticks.append(-y)
            labels.append(sname)
        y += 0.3
    ax.set_yticks(ticks)
    ax.set_yticklabels(labels, fontsize=6.6)
    ax.set_ylim(-(y + 0.4), -0.2)
    ax.set_xlim(0, 196)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Patients by CNN-predicted class")
    ax.legend(
        handles=[plt.Rectangle((0, 0), 1, 1, color=CLASS_COL[c]) for c in CLASSES],
        labels=[f"predicted {c}" for c in CLASSES],
        loc="lower left",
        bbox_to_anchor=(0, 1.0),
        ncol=3,
        handlelength=1.0,
        borderaxespad=0,
        columnspacing=0.8,
    )
    ax.text(
        -0.42,
        1.02,
        "C",
        transform=ax.transAxes,
        fontsize=10,
        fontweight="bold",
        ha="right",
        va="bottom",
    )
    save(fig, "Figure6_counterfactual_test")


# =================================================================================================
# Figure 8 — Grad-CAM of the main CNN with pre-specified measures (replaces submitted Figs 13–15)
# =================================================================================================
def figure_gradcam(census_wide=None):
    census_wide = census_wide or ARGS.census_wide
    from matplotlib.colors import LinearSegmentedColormap

    ex = np.load(REV / RUN["F2"] / "F2_examples.npz")
    meta = {m["tag"]: m for m in json.loads((REV / RUN["F2"] / "F2_examples.json").read_text())}
    A = f("F2", "F2_attention_per_patient_phase.csv", dtype={"patient_id": str})
    Sh = f("F2", "F2_phase_share_per_patient.csv", dtype={"patient_id": str})
    heat = LinearSegmentedColormap.from_list(
        "heat",
        [(1, 1, 1, 0), (0.93, 0.63, 0.0, 0.55), (0.92, 0.41, 0.2, 0.85), (0.75, 0.1, 0.1, 0.95)],
    )
    fig = plt.figure(figsize=(174 * MM, 150 * MM))
    gs = fig.add_gridspec(2, 1, height_ratios=[0.62, 1], hspace=0.28)
    top = gs[0].subgridspec(2, 7, wspace=0.05, hspace=0.06)
    tiles = [
        ("fig8_internal_HCC", "cam_pred", "PLC-CECT HCC"),
        ("fig8_internal_ICC", "cam_pred", "PLC-CECT ICC"),
        ("fig8_internal_CHCC", "cam_pred", "PLC-CECT\ncHCC-CCA"),
        ("fig8_internal_misclassified", "cam_pred", "cHCC-CCA called\nHCC: HCC map"),
        ("fig8_internal_misclassified", "cam_true", "same case:\ncHCC-CCA map"),
        ("fig8_mct_HCC", "cam_pred", "MCT-LTDiag HCC"),
        ("fig8_mct_ICC", "cam_pred", "MCT-LTDiag ICC"),
    ]
    names3 = ["HCC", "ICC", "cHCC-CCA"]
    for c, (tag, cam, head) in enumerate(tiles):
        m = meta[tag]
        ct, tm, cm = ex[f"{tag}_ct"][2], ex[f"{tag}_tm"][2], ex[f"{tag}_{cam}"]
        pr = m["probabilities"]
        k = int(np.argmax(pr))
        for r in range(2):
            ax = fig.add_subplot(top[r, c])
            _tile(ax, ct, tm)
            if r == 1:
                ax.imshow(cm / cm.max(), cmap=heat, vmin=0, vmax=1, interpolation="bilinear")
            if r == 0:
                ax.set_title(
                    f"{head}\n{m['patient_id']}", fontsize=6.2, color=INK, pad=3, linespacing=1.1
                )
            else:
                lab_ = (
                    f"pred. {names3[k]} {pr[k]:.2f}"
                    if cam == "cam_pred"
                    else f"map for true class ({pr[2]:.2f})"
                )
                ax.text(
                    0.5,
                    -0.06,
                    lab_,
                    transform=ax.transAxes,
                    ha="center",
                    va="top",
                    fontsize=5.8,
                    color=INK2,
                )
            if r == 0 and tag == "fig8_mct_ICC":
                ax.text(
                    0.5,
                    0.1,
                    "tumor 99% outside " + chr(10) + "the liver mask",
                    transform=ax.transAxes,
                    ha="center",
                    va="bottom",
                    fontsize=5.2,
                    color="white",
                )
            if c == 0:
                ax.set_ylabel("portal venous" if r == 0 else "Grad-CAM", fontsize=6.6, color=INK)
    fig.text(0.07, 0.985, "A", fontsize=10, fontweight="bold", va="top")
    bot = gs[1].subgridspec(1, 2, wspace=0.95, width_ratios=[1.2, 0.85])
    # B: attention enrichment over chance, portal-venous crop, per patient
    ax = fig.add_subplot(bot[0])
    w = (
        pd.read_csv(census_wide, dtype={"patient_id": str}).set_index("patient_id")["C2"]
        if census_wide and Path(census_wide).exists()
        else None
    )
    a = A[(A["phase"] == "C2") & (~A["black_crop"]) & A["enrichment"].notna()].copy()
    groups = [
        ("internal_held_out", "HCC", "PLC-CECT HCC", None),
        ("internal_held_out", "ICC", "PLC-CECT ICC", None),
        ("internal_held_out", "CHCC", "PLC-CECT cHCC-CCA", None),
        ("MCT_LTDiag", "HCC", "MCT-LTDiag HCC", None),
        ("MCT_LTDiag", "ICC", "MCT-LTDiag ICC", None),
    ]
    if w is not None:
        groups[2:2] = [
            ("internal_held_out", "ICC", "  ICC, tumor ≥ 90% inside liver mask", "in"),
            ("internal_held_out", "ICC", "  ICC, tumor < 90% inside liver mask", "out"),
        ]
    rng = np.random.default_rng(3)
    for i, (coh, cl, _lab, sub_) in enumerate(groups):
        yy = len(groups) - 1 - i
        v = a[(a["cohort"] == coh) & (a["class"] == cl)]
        if sub_ is not None:
            share = v["patient_id"].map(w)
            v = v[share >= 0.9] if sub_ == "in" else v[share < 0.9]
        col = CLASS_COL[{"CHCC": "cHCC-CCA"}.get(cl, cl)]
        e = v["enrichment"].to_numpy()
        ax.scatter(
            e,
            yy + rng.uniform(-0.18, 0.18, len(e)),
            s=7 if coh == "MCT_LTDiag" else 10,
            color=col,
            alpha=0.5 if coh == "MCT_LTDiag" else 0.75,
            linewidths=0,
            zorder=2,
        )
        q1, md, q3 = np.percentile(e, [25, 50, 75])
        ax.plot([q1, q3], [yy, yy], color=INK, lw=1.6, zorder=3)
        ax.plot(md, yy, "o", ms=5, color=INK, zorder=4)
        ax.text(
            1.005,
            yy,
            f"{md:.2f} (n = {len(e)})",
            transform=ax.get_yaxis_transform(),
            va="center",
            fontsize=6.3,
            color=INK2,
        )
    ax.axvline(1, color=MUTED, lw=0.9, ls=(0, (3, 2)))
    ax.set_yticks(range(len(groups)))
    ax.set_yticklabels([g[2] for g in groups][::-1], fontsize=6.6)
    ax.set_xlim(0, 3.2)
    ax.set_xlabel(
        "Attention inside the tumor ÷ tumor share of the crop\n"
        "(portal venous; 1 = chance; dot = median, bar = IQR)"
    )
    grid_x(ax)
    panel(ax, "B", "Attention on the tumor")
    # C: per-phase share of |gradient × input|
    ax = fig.add_subplot(bot[1])
    sh = Sh[~Sh["black_crop"]] if "black_crop" in Sh.columns else Sh
    rows = [
        ("internal_held_out", "HCC", "PLC-CECT HCC"),
        ("internal_held_out", "ICC", "PLC-CECT ICC"),
        ("internal_held_out", "CHCC", "PLC-CECT cHCC-CCA"),
        ("MCT_LTDiag", "HCC", "MCT-LTDiag HCC"),
        ("MCT_LTDiag", "ICC", "MCT-LTDiag ICC"),
    ]
    pcols = ["#184f95", "#3987e5", "#9ec5f4", "#c3c2b7"]
    for i, (coh, cl, _lab) in enumerate(rows):
        yy = len(rows) - 1 - i
        v = (
            sh[(sh["cohort"] == coh) & (sh["class"] == cl)][
                [f"share_{p}" for p in ["P", "C1", "C2", "C3"]]
            ]
            .median()
            .to_numpy()
        )
        left = 0
        for k, (_pp, pn) in enumerate(PHASE_NAMES):
            ax.barh(
                yy,
                v[k],
                left=left,
                height=0.62,
                color=pcols[k],
                edgecolor="white",
                lw=0.5,
                label=pn if i == 0 else None,
            )
            ax.text(
                left + v[k] / 2,
                yy,
                f"{v[k]:.2f}",
                ha="center",
                va="center",
                fontsize=5.9,
                color="white" if k < 2 else INK,
            )
            left += v[k]
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r_[2] for r_ in rows][::-1], fontsize=6.6)
    ax.set_xlim(0, 1)
    ax.set_xlabel("Median share of |gradient × input|")
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.45, -0.17),
        ncol=2,
        handlelength=1.0,
        borderaxespad=0,
        columnspacing=1.0,
    )
    panel(ax, "C", "Contribution of each phase channel")
    save(fig, "Figure8_gradcam")


FIGURES = {
    "design": figure_design,
    "examples": figure_examples,
    "internal": figure_internal,
    "size": figure_size,
    "artifacts": figure_artefacts,
    "counterfactual": figure_counterfactual,
    "external": figure_external,
    "gradcam": figure_gradcam,
    "tace": figure_tace,
}

if __name__ == "__main__":
    for key in ARGS.figures:
        FIGURES[key]()
