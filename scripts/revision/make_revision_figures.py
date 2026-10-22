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

Each figure is written as PNG, PDF, and TIFF (600 dpi). The repository publishes PNG copies of
Figures 1, 3, 4, 5, and 7 in ``results/revision_2026-10/figures``; Figures 2, 6, and 8 show
patient images and stay private.
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
    help="figures to draw (keys of FIGURES; design_public is the repository copy of Figure 1)",
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
INK, INK2, MUTED, GRID, BASE = "#000000", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
TEXT = "#000000"  # journal rule: every label is black
S1, S2, S3, S4 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"  # categorical slots 1-4 (validated)
CLASS_COL = {"HCC": S1, "ICC": S2, "cHCC-CCA": S3}
BLUES = ["#ffffff", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Liberation Sans", "DejaVu Sans"],
        "font.size": 8,
        "axes.titlesize": 9,
        "axes.labelsize": 8,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "axes.edgecolor": BASE,
        "axes.linewidth": 0.8,
        "xtick.color": INK2,
        "ytick.color": INK2,
        "xtick.labelcolor": TEXT,
        "ytick.labelcolor": TEXT,
        "axes.labelcolor": TEXT,
        "text.color": TEXT,
        "legend.labelcolor": TEXT,
        "mathtext.fontset": "custom",
        "mathtext.rm": "Arial",
        "mathtext.it": "Arial:italic",
        "mathtext.bf": "Arial:bold",
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
WIDTH = 165  # mm; the manuscript inserts every figure 16.5 cm wide (JIMH maximum 16.51 cm x 20 cm)
PAD = 0.02  # inches of white margin kept around the trimmed figure


def panel(ax, letter, title):
    ax.set_title(title, loc="left", fontsize=9, color=TEXT, pad=6)
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
    fit_width(fig)
    from matplotlib.text import Text

    for txt in fig.findobj(Text):  # journal rule: every label is black
        if txt.get_text().strip():
            txt.set_color(TEXT)
    journal_check(fig, name)
    for ext in ("png", "pdf"):
        fig.savefig(dest / f"{name}.{ext}", dpi=600, bbox_inches="tight", pad_inches=PAD)
    # TIFF for the journal upload: RGB without alpha, 600 dpi (JIMH prefers .tif at 500+ dpi)
    fig.savefig(
        dest / f"{name}.tif",
        dpi=600,
        bbox_inches="tight",
        pad_inches=PAD,
        pil_kwargs={"compression": "tiff_lzw"},
    )
    from PIL import Image

    with Image.open(dest / f"{name}.tif") as im:
        if im.mode != "RGB":
            im.convert("RGB").save(dest / f"{name}.tif", compression="tiff_lzw", dpi=(600, 600))
    plt.close(fig)
    print("saved", name)


def fit_width(fig):
    """Resize the figure so that its tight bounding box is exactly WIDTH mm wide.

    Font sizes in the code are then the printed sizes: text keeps its point size and the axes take
    the remaining width.
    """
    target = WIDTH / 25.4 - 2 * PAD
    if getattr(fig, "journal_fixed", False):
        return
    engine = fig.get_layout_engine()
    if engine is not None and "Constrained" in type(engine).__name__:
        # constrained layout fills the figure; anything wider than the page is an overflow to fix
        fig.set_size_inches(WIDTH / 25.4 - 2 * PAD, fig.get_size_inches()[1])
        fig.canvas.draw()
        width = fig.get_tightbbox(fig.canvas.get_renderer()).width
        if width > target + 0.02:
            from matplotlib.text import Text

            r = fig.canvas.get_renderer()
            fw = fig.bbox.width
            out = [
                f"{x.get_text()[:30]!r} ({x.get_window_extent(r).x0 / fig.dpi * 25.4:.0f}–"
                f"{x.get_window_extent(r).x1 / fig.dpi * 25.4:.0f} mm)"
                for x in fig.findobj(Text)
                if x.get_text().strip()
                and (x.get_window_extent(r).x0 < -0.5 or x.get_window_extent(r).x1 > fw + 0.5)
            ]
            raise SystemExit(
                f"fit_width: content is {(width - target) * 25.4:.1f} mm wider than the page: "
                + "; ".join(out)
            )
        return
    for _ in range(10):
        fig.canvas.draw()
        width = fig.get_tightbbox(fig.canvas.get_renderer()).width
        if abs(width - target) < 0.003:
            return
        w, h = fig.get_size_inches()
        if w + (target - width) < 0.5 * target:
            raise SystemExit(
                "fit_width: labels outside the panels are wider than the page; shorten them"
            )
        fig.set_size_inches(w + (target - width), h)


LOWER_OK = ("cHCC-CCA", "cHCC", "p(", "n ", "n=", "mm", "vs")


def journal_check(fig, name):
    """Check the JIMH figure rules at the printed size (16.5 cm wide).

    Every label is at least 8 pt and at most 11 pt (the main text), black, and starts with a capital
    letter (defined lowercase terms excepted); p values are italic; the figure is no taller than
    20 cm. Raises with a list of every violation.
    """
    import re as _re

    from matplotlib.colors import to_hex
    from matplotlib.text import Text

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    tight = fig.get_tightbbox(renderer)
    scale = (WIDTH / 25.4) / (tight.width + 2 * PAD)  # printed size / drawn size
    bad = []
    if (tight.height + 2 * PAD) * scale > 200 / 25.4 + 1e-6:
        bad.append(f"height {(tight.height + 2 * PAD) * scale * 25.4:.0f} mm > 200 mm")
    for t in fig.findobj(Text):
        s = t.get_text()
        if not s.strip() or not t.get_visible():
            continue
        ext = t.get_window_extent(renderer)
        if ext.width == 0 or ext.height == 0:
            continue
        size = t.get_fontsize() * scale
        if size < 7.95 or size > 11.05:
            bad.append(f"size {size:.1f} pt: {s[:40]!r}")
        if to_hex(t.get_color()) != "#000000":
            bad.append(f"colour {to_hex(t.get_color())}: {s[:40]!r}")
        first = _re.sub(r"\$[^$]*\$", "P", s.split("\n")[0]).lstrip(" ([|·•")
        if first and first[0].isalpha() and first[0].islower() and not first.startswith(LOWER_OK):
            bad.append(f"lowercase start: {first[:40]!r}")
        if _re.search(r"(?<![\w$(])p\s*[=<>]", _re.sub(r"\$[^$]*\$", "", s)):
            bad.append(f"p value not italic: {s[:40]!r}")
    if bad:
        raise SystemExit(f"{name}: {len(bad)} journal-rule violations\n  " + "\n  ".join(bad))


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
        figsize=(WIDTH * MM, 150 * MM),
        layout="constrained",
        gridspec_kw={"width_ratios": [1.1, 1]},
    )
    fig.get_layout_engine().set(w_pad=0.04, h_pad=0.06, wspace=0.04, hspace=0.08)

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
                1.01,
                y + dy,
                f"{est:.3f}",
                transform=ax.get_yaxis_transform(),
                va="center",
                fontsize=8,
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
        bbox_to_anchor=(0, 1.04),
        ncol=1,
        handlelength=1.6,
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
            fontsize=8,
            color=INK2,
        )
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([o[1] for o in order][::-1])
    ax.set_xlim(0.8, 1.0)
    ax.set_xlabel("Macro-AUC per fold (25 folds; bar = mean)")
    grid_x(ax)
    panel(ax, "B", "Repeated CV, 5 × 5 folds")

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

    ax.imshow(cm, cmap=LinearSegmentedColormap.from_list("b", BLUES[:4]), vmin=0, vmax=cm.max())
    for i in range(3):
        for j in range(3):
            ax.text(
                j,
                i,
                str(cm[i, j]),
                ha="center",
                va="center",
                fontsize=8,
                color=TEXT,
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
    panel(ax, "C", f"CNN + radiomics, held-out ({int(np.trace(cm))}/56 correct)")

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
        bbox_to_anchor=(0, 1.04),
        ncol=1,
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
    fig = plt.figure(figsize=(WIDTH * MM, 140 * MM), layout="constrained")
    sf_top, sf_bot = fig.subfigures(2, 1, height_ratios=[1, 1.1])
    axes = np.array(
        [
            sf_top.subplots(1, 2, gridspec_kw={"width_ratios": [1.6, 1]}),
            sf_bot.subplots(1, 2, gridspec_kw={"width_ratios": [1.45, 1]}),
        ]
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
    ax.set_xticklabels(["Non-\ncontrast", "Arterial", "Portal\nvenous", "Delayed"])
    ax.set_ylabel("Slices per scan")
    grid_y(ax)
    ax.legend(
        handles=[plt.Rectangle((0, 0), 1, 1, color=CLASS_COL[c]) for c in CLASSES],
        labels=CLASSES,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.25),
        ncol=3,
        handlelength=1.0,
        borderaxespad=0,
        columnspacing=1.2,
    )
    fig.get_layout_engine().set(w_pad=0.04, h_pad=0.06, wspace=0.06, hspace=0.1)
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
    panel(ax, "B", "MCT-LTDiag (203)")

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
            "Slice counts, 3 classes, held-out\n(logistic / random forest)",
            [held["logistic"], held["random forest"]],
            MUTED,
        ),
        (
            "CNN + radiomics, 3 classes, held-out",
            [m47.loc["cnn_plus_radiomics [phase_dropout_CNN]", "test_macro_auc"]],
            S1,
        ),
        ("Slice counts, HCC vs ICC, out-of-fold", [roc_auc_score(yh, s_only)], MUTED),
        ("CNN + radiomics, HCC vs ICC, out-of-fold", [roc_auc_score(yh, sh)], S1),
        (
            f"CNN + radiomics, HCC vs ICC,\nambiguous slice counts (n = {int(mid.sum())})",
            [roc_auc_score(yh[mid], sh[mid])],
            S1,
        ),
        ("Slice counts, MCT-LTDiag, HCC vs ICC", [a], MUTED),
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
            fontsize=8,
            color=INK2,
        )
    ax.set_yticks(range(len(items)))
    ax.set_yticklabels([it[0] for it in items][::-1], fontsize=8)
    ax.set_xlim(0.5, 1.04)
    ax.set_xlabel("AUC (macro-AUC for 3 classes)")
    grid_x(ax)
    panel(ax, "C", "Acquisition alone predicts the class (post hoc)")

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
    ax.set_xlabel("Out-of-fold AUC; arrow:\nnon-contrast removed")
    grid_x(ax)
    ax.legend(
        handles=[
            Line2D([], [], color=S1, marker="o", lw=1.3, ms=4.5, label="HCC vs ICC"),
            Line2D([], [], color=S3, marker="o", lw=1.3, ms=4.5, label="cHCC-CCA vs rest"),
        ],
        loc="lower left",
        bbox_to_anchor=(0, 1.04),
        ncol=1,
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
    fig = plt.figure(figsize=(WIDTH * MM, (140 if e4d else 70) * MM), layout="constrained")
    fig.get_layout_engine().set(w_pad=0.04, h_pad=0.06, wspace=0.06, hspace=0.08)
    gs = fig.add_gridspec(2 if e4d else 1, 2, height_ratios=[1, 0.8] if e4d else [1])
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
        ax.text(j, 1.05, f"{(v < 0.9).sum()}/{len(v)}", ha="center", fontsize=8, color=INK2)
    ax.axhline(0.9, color=MUTED, lw=0.8, ls=(0, (3, 2)))
    ax.set_xticks(range(3))
    ax.set_xticklabels(CLASSES)
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("Tumor fraction inside the 96³ crop")
    grid_y(ax)
    panel(ax, "A", "Crop truncation (portal venous)")
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
    fig = plt.figure(figsize=(WIDTH * MM, 195 * MM), layout="constrained")
    fig.get_layout_engine().set(w_pad=0.04, h_pad=0.06, wspace=0.08, hspace=0.06)
    sf_top, sf_bot = fig.subfigures(2, 1, height_ratios=[1, 1.2])
    gs_top = sf_top.add_gridspec(1, 2)
    ax = sf_top.add_subplot(gs_top[0, 0])
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
        bbox_to_anchor=(0.0, -0.27),
        title="AUC",
        title_fontsize=8,
        handlelength=1.4,
        alignment="left",
        borderaxespad=0,
        labelspacing=0.3,
    )
    panel(ax, "A", "MCT-LTDiag, 103 HCC vs 100 ICC")

    ax = sf_top.add_subplot(gs_top[0, 1])
    rel = f("E47", "E7c_reliability_tables.csv")
    cal = f("E47", "E7c_calibration.csv")
    key = "cnn_plus_radiomics [phase_dropout_CNN]"
    for cohort, target, col, name in [
        ("internal_test_56", "HCC_vs_rest", S1, "Held-out (HCC vs rest)"),
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
            label=f"{name}\nIntercept {c['intercept']:.2f}, slope {c['slope']:.2f}".replace(
                "t -", "t −"
            ),
        )
    ax.plot([0, 1], [0, 1], color=MUTED, lw=0.8, ls=(0, (3, 2)))
    ax.set_xlabel("Predicted probability of HCC")
    ax.set_ylabel("Observed proportion HCC")
    ax.set_aspect("equal")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.legend(
        loc="upper left",
        bbox_to_anchor=(0.0, -0.27),
        handlelength=1.4,
        fontsize=8,
        borderaxespad=0,
        labelspacing=0.6,
    )
    panel(ax, "B", "Calibration, CNN + radiomics")

    ax = sf_bot.add_subplot()
    r8 = f("E8b", "E8b_E9_mct203_results.csv").set_index("model")
    r8a = f("E8a", "E8a_mct203_results.csv").set_index("model")
    # The CNN reference is the Table 5 value (E8.0, 203 patients). E8b recomputed the same model's
    # predictions (largest difference about 1e-4), which moved the upper CI bound across a rounding
    # boundary (0.607 vs 0.608).
    r80 = f("E8a", "E8_0_E6_203_results.csv")
    r80 = r80[(r80["variant"] == "primary") & (r80["subset"] == "all")].set_index("model")
    groups = [
        (
            "CNN",
            [
                ("Phase-dropout CNN (reference)", r80, "phase_dropout_CNN"),
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
            0.3,
            -y,
            gname,
            fontsize=8,
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
            ax.text(0.81, -y, f"{est:.3f} ({lo:.3f}–{hi:.3f})", va="center", fontsize=8, color=TEXT)
            ticks.append(-y)
            labels.append(lab)
        y += 0.4
    ax.axvline(0.5, color=MUTED, lw=0.8, ls=(0, (3, 2)))
    ax.set_yticks(ticks)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlim(0.3, 1.02)
    ax.set_xticks([0.3, 0.4, 0.5, 0.6, 0.7, 0.8])
    ax.set_ylim(-(y + 0.3), -0.4)
    ax.set_xlabel("MCT-LTDiag HCC-vs-ICC AUC (DeLong 95% CI); every variant evaluated once")
    grid_x(ax)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    panel(ax, "C", "Mitigation strategies: none improved external discrimination significantly")
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
        fontsize=8,
        color=MUTED,
    )
    save(fig, "Figure_HCC_TACE_Seg")


# =================================================================================================
# Figure 1 — study design (cohorts, pipeline with the real inputs of one patient, evaluation)
# =================================================================================================
from matplotlib.patches import (  # noqa: E402
    Arc,
    Circle,
    Ellipse,
    FancyArrowPatch,
    FancyBboxPatch,
    Polygon,
    Rectangle,
)

CARD, CARD2 = "#f6f5f2", "#e9e8e2"


def figure_design(public=False):
    """Draw Figure 1 in millimetres at the printed width.

    Every label is black and at least 8 pt, and colour encodes the tumor class only. The CT tiles
    and the feature strip are the real inputs of the Figure 2 cHCC-CCA patient.
    """
    W, H = WIDTH - 2 * PAD * 25.4, 170
    fig = plt.figure(figsize=(W * MM, H * MM))
    fig.journal_fixed = True  # drawn at the printed size; fit_width leaves it alone
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")

    def txt(x, y, s, size=8, weight="normal", ha="left", va="center", **kw):
        ax.text(x, y, s, fontsize=size, fontweight=weight, ha=ha, va=va, color=TEXT, **kw)

    def card(x, y, w, h, fill=CARD, edge=None, lw=0.0, r=1.4):
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                w,
                h,
                boxstyle=f"round,pad=0,rounding_size={r}",
                fc=fill,
                ec=edge or "none",
                lw=lw,
            )
        )

    def tag(x, y, s):  # right-aligned role tag
        ax.text(
            x,
            y,
            s,
            fontsize=8,
            ha="right",
            va="center",
            color=TEXT,
            bbox={
                "boxstyle": "round,pad=0.25,rounding_size=0.8",
                "fc": "white",
                "ec": INK2,
                "lw": 0.6,
            },
        )

    def arrow(x0, y0, x1, y1, ls="-", conn="arc3"):
        ax.add_patch(
            FancyArrowPatch(
                (x0, y0),
                (x1, y1),
                arrowstyle="-|>",
                mutation_scale=6,
                lw=0.8,
                color=INK2,
                linestyle=ls,
                connectionstyle=conn,
                shrinkA=0,
                shrinkB=0,
                zorder=4,
            )
        )

    def classbar(x, y, counts, scale, h=4.4):  # stacked class bar, labels inside in black
        cx = x
        for n, c, name in zip(counts, [S1, S2, S3], CLASSES, strict=True):
            if n == 0:
                continue
            ax.add_patch(
                FancyBboxPatch(
                    (cx, y),
                    n * scale - 0.5,
                    h,
                    boxstyle="round,pad=0,rounding_size=0.5",
                    fc=c,
                    ec="none",
                )
            )
            txt(cx + 1.2, y + h / 2, f"{n} {name}")
            cx += n * scale

    def prob(x, y, w, h, heights):  # schematic class probabilities
        bw = w / 3.6
        for i, (hh, c) in enumerate(zip(heights, [S1, S2, S3], strict=True)):
            bx = x + i * (bw + (w - 3 * bw) / 2)
            ax.add_patch(
                FancyBboxPatch(
                    (bx, y + h * (1 - hh)),
                    bw,
                    h * hh,
                    boxstyle="round,pad=0,rounding_size=0.35",
                    fc=c,
                    ec="none",
                )
            )
        ax.plot([x - 0.3, x + w + 0.3], [y + h, y + h], color=BASE, lw=0.6)

    def lock(x, y, r=0.85):
        ax.add_patch(
            Arc((x, y - 0.5), 2.2 * r, 2.6 * r, theta1=180, theta2=360, ec=INK2, lw=0.8, zorder=6)
        )
        ax.add_patch(
            FancyBboxPatch(
                (x - 1.4 * r, y - 0.5),
                2.8 * r,
                2.0 * r,
                boxstyle="round,pad=0,rounding_size=0.3",
                fc=INK2,
                ec="none",
                zorder=6,
            )
        )

    # ---------------------------------------------------------- A: cohorts and data partition
    txt(0.5, 4, "A", size=10, weight="bold")
    txt(5, 4, "Cohorts and data partition", size=9, weight="bold")
    for k, (name, c) in enumerate(zip(CLASSES, [S1, S2, S3], strict=True)):
        kx = [116.0, 129.0, 141.5][k]
        ax.add_patch(
            FancyBboxPatch(
                (kx, 2.6), 2.8, 2.8, boxstyle="round,pad=0,rounding_size=0.4", fc=c, ec="none"
            )
        )
        txt(kx + 3.8, 4, name)
    sc = 74 / 278  # mm per patient, the same for every cohort
    card(0.5, 8, 80, 45.5)
    txt(3, 12.5, "PLC-CECT", size=9, weight="bold")
    tag(78.5, 12.5, "Development")
    txt(3, 17.5, "Chongqing Yubei District People's Hospital")
    txt(3, 21.5, "2015–2022 · 278 patients · four phases")
    classbar(3, 24.2, [94, 99, 85], sc)
    card(3, 33, 42, 18, fill="white")
    card(47.5, 33, 31, 18, fill="white")
    arrow(24, 28.8, 24, 32.8)
    arrow(63, 28.8, 63, 32.8)
    txt(5, 37, "Development (222)", size=8.5, weight="bold")
    for k in range(5):
        ax.add_patch(
            FancyBboxPatch(
                (5 + k * 4.4, 40.6),
                3.9,
                2.8,
                boxstyle="round,pad=0,rounding_size=0.4",
                fc=INK2 if k == 4 else BASE,
                ec="none",
            )
        )
    txt(28, 42, "5 folds")
    txt(5, 47.5, "Fitting; 5 × 5 repeated CV")
    txt(49.5, 37, "Held-out (56)", size=8.5, weight="bold")
    xb = 49.5
    for n, c in zip([19, 20, 17], [S1, S2, S3], strict=True):
        ax.add_patch(
            FancyBboxPatch(
                (xb, 40.6),
                n * 26.5 / 56 - 0.5,
                2.8,
                boxstyle="round,pad=0,rounding_size=0.4",
                fc=c,
                ec="none",
            )
        )
        xb += n * 26.5 / 56
    txt(49.5, 47.9, "Never used for\nfitting or tuning", linespacing=1.15)
    ax.plot([83.2, 83.2], [9, 52.5], color=BASE, lw=0.7, ls=(0, (2, 2)))
    ax.add_patch(Circle((83.2, 30.5), 3.0, fc="white", ec=BASE, lw=0.7, zorder=5))
    lock(83.2, 30.6)
    arrow(80.7, 18.5, 85.8, 18.5)
    arrow(80.7, 42, 85.8, 42)
    card(86, 8, W - 86.5, 21.5)
    txt(88.5, 12.5, "MCT-LTDiag", size=9, weight="bold")
    tag(W - 2.5, 12.5, "External validation")
    txt(88.5, 17.3, "Peking Union Medical College Hospital")
    txt(88.5, 21.2, "2014–2024 · 203 patients · 5 mm slices")
    classbar(88.5, 23.6, [103, 100, 0], sc)
    txt(W - 2.5, 25.8, "HCC vs ICC", ha="right")
    card(86, 31.5, W - 86.5, 22)
    txt(88.5, 36, "HCC-TACE-Seg", size=9, weight="bold")
    tag(W - 2.5, 36, "Stress test")
    txt(88.5, 40.8, "MD Anderson Cancer Center, USA")
    txt(88.5, 44.7, "2002–2012 · 89 HCC (103 in total)")
    classbar(88.5, 47.2, [89, 0, 0], sc)
    txt(W - 2.5, 49.4, "HCC sensitivity only", ha="right")

    # ------------------------------------------------------------------ B: model pipeline
    txt(0.5, 59.5, "B", size=10, weight="bold")
    txt(5, 59.5, "Model pipeline (fitted on the development folds only)", size=9, weight="bold")
    if not public:
        ex = np.load(REV / RUN["F2"] / "F2_examples.npz")
        meta = {m["tag"]: m for m in json.loads((REV / RUN["F2"] / "F2_examples.json").read_text())}
        ct, tm = ex["fig2_internal_CHCC_ct"], ex["fig2_internal_CHCC_tm"]
    ts = 14.5
    for i, name in enumerate(["NC", "AP", "PV", "DP"]):
        r, c = divmod(i, 2)
        x0, y0 = 0.5 + c * (ts + 2.5), 67 + r * (ts + 4.5)
        if public:  # schematic tile: grey square with a tumor outline
            fc = ["#8f8e89", "#a7a6a0", "#b9b8b2", "#a9a8a2"][i]
            ax.add_patch(Rectangle((x0, y0), ts, ts, fc=fc, ec="none"))
            ax.add_patch(
                Ellipse((x0 + ts / 2, y0 + ts / 2), ts * 0.62, ts * 0.5, fc="none", ec=S4, lw=0.6)
            )
        else:
            ax.imshow(
                ct[i],
                cmap="gray",
                vmin=0,
                vmax=255,
                extent=(x0, x0 + ts, y0 + ts, y0),
                interpolation="nearest",
            )
            g = (np.arange(ct.shape[1]) + 0.5) / ct.shape[1] * ts
            ax.contour(
                x0 + g, y0 + g, tm[i].astype(float), levels=[0.5], colors=[S4], linewidths=0.6
            )
        txt(x0 + ts / 2, y0 - 1.9, name, ha="center")
    txt(0.5, 104.5, "Liver-masked")
    txt(0.5, 108.3, "96³ crops")
    arrow(33.2, 84, 36.8, 75.5, conn="arc3,rad=-0.25")
    arrow(33.2, 84, 36.8, 99.5, conn="arc3,rad=0.25")
    # CNN branch
    card(37.5, 63, 81, 24)
    txt(40, 66.8, "CNN", size=8.5, weight="bold")
    for k in range(4):
        ox, oy = 40.0 + k * 1.1, 70.0 + k * 1.0
        ax.add_patch(
            Rectangle(
                (ox, oy),
                7.0,
                7.0,
                fc=["#3a3a38", "#545450", "#6e6e69", "#898781"][k],
                ec="white",
                lw=0.5,
                zorder=3 + k,
            )
        )
    txt(44.5, 83.5, "4 × 96³", ha="center")
    arrow(49.6, 75.5, 52.4, 75.5)
    for k, kept in enumerate([True, False, True, False]):
        bx = 53.2 + k * 3.3
        ax.add_patch(
            FancyBboxPatch(
                (bx, 72.5),
                2.8,
                6.0,
                boxstyle="round,pad=0,rounding_size=0.4",
                fc="#6e6e69" if kept else "white",
                ec="none" if kept else INK2,
                lw=0.4,
            )
        )
        if not kept:
            ax.plot([bx + 0.5, bx + 2.3], [73.3, 77.7], color=INK2, lw=0.5)
            ax.plot([bx + 0.5, bx + 2.3], [77.7, 73.3], color=INK2, lw=0.5)
    txt(59.0, 69.6, "Phase dropout", ha="center")
    arrow(66.8, 75.5, 69.6, 75.5)
    for bx, bh, bw, bd in [
        (70.4, 10.0, 2.0, 3.0),
        (74.6, 8.6, 2.2, 3.4),
        (79.1, 7.2, 2.6, 3.8),
        (84.0, 5.8, 3.0, 4.2),
        (89.4, 4.4, 3.4, 4.6),
    ]:
        y_ = 75.5 - bh / 2 + 0.6
        dx, dy = bd * 0.6, -bd * 0.45
        ax.add_patch(
            Polygon(
                [(bx, y_), (bx + bw, y_), (bx + bw + dx, y_ + dy), (bx + dx, y_ + dy)],
                closed=True,
                fc="#ecebe6",
                ec=INK2,
                lw=0.35,
            )
        )
        ax.add_patch(
            Polygon(
                [
                    (bx + bw, y_),
                    (bx + bw + dx, y_ + dy),
                    (bx + bw + dx, y_ + bh + dy),
                    (bx + bw, y_ + bh),
                ],
                closed=True,
                fc="#c3c2b7",
                ec=INK2,
                lw=0.35,
            )
        )
        ax.add_patch(Rectangle((bx, y_), bw, bh, fc="#d9d8d2", ec=INK2, lw=0.35))
    txt(82.5, 83.5, "3D ResNet-18", ha="center")
    arrow(97.0, 75.5, 100.4, 75.5)
    prob(101.5, 71.0, 8.0, 7.5, (0.25, 0.15, 0.6))
    # radiomics branch
    card(37.5, 89.5, 81, 23)
    txt(40, 93.3, "Radiomics", size=8.5, weight="bold")
    if public:
        ax.add_patch(Ellipse((44.5, 101.5), 8.0, 6.4, fc="#b9b8b2", ec=S4, lw=0.6, zorder=3))
    else:
        m2 = tm[2].astype(bool)
        roi = np.where(m2, ct[2], 0).astype(float)
        ys, xs = np.nonzero(m2)
        y0_, y1_ = max(ys.min() - 3, 0), min(ys.max() + 4, ct.shape[1])
        x0_, x1_ = max(xs.min() - 3, 0), min(xs.max() + 4, ct.shape[2])
        sub = roi[y0_:y1_, x0_:x1_]
        s_ = 9.0 / max(sub.shape)
        hh, ww = sub.shape[0] * s_, sub.shape[1] * s_
        ax.imshow(
            sub,
            cmap="gray",
            vmin=0,
            vmax=255,
            extent=(40.0, 40.0 + ww, 97.0 + hh, 97.0),
            interpolation="nearest",
            zorder=3,
        )
        ax.contour(
            40.0 + (np.arange(sub.shape[1]) + 0.5) * s_,
            97.0 + (np.arange(sub.shape[0]) + 0.5) * s_,
            m2[y0_:y1_, x0_:x1_].astype(float),
            levels=[0.5],
            colors=[S4],
            linewidths=0.6,
            zorder=4,
        )
    txt(44.5, 109, "Tumor mask", ha="center")
    arrow(50.4, 101.5, 53.2, 101.5)
    if public:  # schematic strip: seeded noise, not patient values
        zz = np.clip(np.random.default_rng(0).normal(0.0, 1.0, (4, 93)), -2.5, 2.5)
    else:
        feats = pd.read_parquet(LP / "radiomics" / "radiomics_features.parquet")
        feats["patient_id"] = feats["patient_id"].astype(str)
        pid = meta["fig2_internal_CHCC"]["patient_id"]
        rows = []
        for ph in ["P", "C1", "C2", "C3"]:
            cols = [
                col
                for col in feats.columns
                if col.startswith(ph + "_original_") and "_shape_" not in col
            ]
            z = (feats[cols] - feats[cols].mean()) / feats[cols].std(ddof=0).replace(0, 1)
            rows.append(z.loc[feats["patient_id"] == pid, cols].to_numpy(dtype=float)[0])
        zz = np.clip(np.nan_to_num(np.vstack(rows)), -2.5, 2.5)
    ax.imshow(
        zz,
        cmap="Greys",
        vmin=-2.5,
        vmax=2.5,
        extent=(54.0, 80.0, 105.0, 98.0),
        interpolation="nearest",
        aspect="auto",
        zorder=3,
    )
    ax.add_patch(Rectangle((54.0, 98.0), 26.0, 7.0, fc="none", ec=INK2, lw=0.35, zorder=4))
    txt(67.0, 109, "372 features", ha="center")
    arrow(80.8, 101.5, 83.6, 101.5)
    ax.add_patch(
        Polygon(
            [(84.2, 97.6), (92.0, 99.8), (92.0, 103.2), (84.2, 105.4)],
            closed=True,
            fc="#d9d8d2",
            ec=INK2,
            lw=0.35,
        )
    )
    txt(88.1, 95.2, "Top 30", ha="center")
    arrow(92.6, 101.5, 94.6, 101.5)
    for k in range(3):
        bx, by = 95.2 + k * 2.6, 98.6
        for (xa, ya), (xb_, yb) in [
            ((1.0, 0), (0.4, 2.4)),
            ((1.0, 0), (1.6, 2.4)),
            ((0.4, 2.4), (0.1, 4.6)),
            ((0.4, 2.4), (0.8, 4.6)),
        ]:
            ax.plot([bx + xa, bx + xb_], [by + ya, by + yb], color=INK2, lw=0.4)
        for px, py in [(1.0, 0), (0.4, 2.4), (1.6, 2.4), (0.1, 4.6), (0.8, 4.6)]:
            ax.add_patch(Circle((bx + px, by + py), 0.42, fc="#6e6e69", ec="none"))
    txt(98.6, 109, "LightGBM", ha="center")
    arrow(102.6, 101.5, 105.0, 101.5)
    prob(106.0, 97.0, 8.0, 7.5, (0.3, 0.2, 0.5))
    # late fusion
    card(121, 63, W - 121.5, 49.5, fill="white", edge=BASE, lw=0.6)
    txt(123.5, 66.8, "Late fusion", size=8.5, weight="bold")
    nx, ny = 131.5, 87.0
    arrow(110.6, 74.0, nx - 2.9, ny - 1.6, conn="arc3,rad=-0.2")
    arrow(115.0, 101.5, nx - 2.9, ny + 1.6, conn="arc3,rad=0.2")
    card(124.5, 70.5, 14.0, 5.6, fill=CARD2, r=1.0)
    txt(131.5, 73.3, "Age, sex", ha="center")
    arrow(131.5, 76.4, 131.5, ny - 3.4, ls=(0, (2, 1.5)))
    ax.add_patch(Circle((nx, ny), 3.2, fc=INK2, ec="none", zorder=5))
    xx = np.linspace(-1.9, 1.9, 40)
    ax.plot(nx + xx, ny + 1.2 - 2.4 / (1 + np.exp(-3.2 * xx)), color="white", lw=0.9, zorder=6)
    txt(nx + 4.0, ny - 1.6, "Logistic\nregression", ha="left", va="bottom", linespacing=1.15)
    arrow(nx + 3.5, ny, 143.0, ny)
    prob(144.0, 79.5, 15.0, 10.0, (0.2, 0.12, 0.68))
    txt(151.5, 93.2, "Probabilities", ha="center")
    txt(123.5, 104.0, "CNN + radiomics (primary)")
    txt(123.5, 108.0, "Full fusion: + age, sex")

    # ------------------------------------------------------------------ C: evaluation
    txt(0.5, 119, "C", size=10, weight="bold")
    txt(5, 119, "Evaluation", size=9, weight="bold")
    cw = (W - 1 - 2 * 2.5) / 3
    cards = [
        (
            "Internal performance",
            "56 held-out; development CV",
            [
                "Macro-AUC, bootstrap CI",
                "DeLong tests, BH-adjusted",
                "Calibration, Brier score",
                "5 × 5 repeated CV",
                "Size thirds; missing phases",
            ],
        ),
        (
            "Dataset audit",
            "All 1,112 PLC-CECT scans",
            [
                "File and mask census",
                "Slice-thickness estimate",
                "Models without non-contrast",
                "Counterfactual resampling",
                "Grad-CAM measures",
            ],
        ),
        (
            "External evaluation",
            "Frozen models, no refitting",
            [
                "Inputs matched to training",
                "MCT-LTDiag: AUC, calibration",
                "Mitigation strategies",
                "HCC-TACE-Seg: HCC sensitivity",
            ],
        ),
    ]
    for i, (head, subhead, bullets) in enumerate(cards):
        x = 0.5 + i * (cw + 2.5)
        card(x, 123, cw, 44.5)
        ix, iy = x + 5.0, 128.8
        ax.add_patch(Circle((ix, iy), 3.3, fc="white", ec=BASE, lw=0.6))
        if i == 0:  # ROC glyph
            ax.plot(
                [ix - 1.7, ix - 1.7, ix + 1.7], [iy - 1.7, iy + 1.7, iy + 1.7], color=INK2, lw=0.5
            )
            u = np.linspace(0, 1, 30)
            ax.plot(ix - 1.7 + 3.4 * u, iy + 1.7 - 3.4 * (1 - (1 - u) ** 3), color=INK2, lw=0.8)
            ax.plot([ix - 1.7, ix + 1.7], [iy + 1.7, iy - 1.7], color=BASE, lw=0.5, ls=(0, (1, 1)))
        elif i == 1:  # thick versus thin slices
            for k in range(3):
                ax.add_patch(
                    Rectangle((ix - 2.0, iy - 1.7 + k * 1.2), 1.6, 0.9, fc=INK2, ec="none")
                )
            for k in range(7):
                ax.add_patch(
                    Rectangle((ix + 0.4, iy - 1.7 + k * 0.52), 1.6, 0.3, fc=INK2, ec="none")
                )
        else:
            lock(ix, iy + 0.2)
        txt(x + 10.2, 127.0, head, size=8.5, weight="bold")
        txt(x + 10.2, 131.2, subhead)
        for k, b in enumerate(bullets):
            yy = 137.5 + k * 5.6
            if not b.startswith("  "):
                ax.add_patch(Circle((x + 3.0, yy), 0.5, fc=INK2, ec="none"))
            txt(x + 5.0, yy, b.strip())
    save(fig, "Figure1_study_design_public" if public else "Figure1_study_design")


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
        4, 5, figsize=(WIDTH * MM, 160 * MM), gridspec_kw={"wspace": 0.06, "hspace": 0.22}
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
                0.5,
                -0.03,
                lab,
                transform=ax.transAxes,
                fontsize=8,
                color=TEXT,
                va="top",
                ha="center",
            )
            if c == 0:
                ax.set_ylabel(phname, fontsize=8, color=INK, labelpad=4)
        axes[0, c].set_title(f"{head}\n{pid}", fontsize=8, color=INK, pad=4, linespacing=1.15)
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
    fig = plt.figure(figsize=(WIDTH * MM, 172 * MM), layout="constrained")
    fig.get_layout_engine().set(w_pad=0.04, h_pad=0.06, wspace=0.06, hspace=0.06)
    gs = fig.add_gridspec(2, 2, height_ratios=[0.62, 1.35], width_ratios=[1.0, 1.0])
    # A: stored-voxel coronal views through the tumor centre of the first seeded evidence
    # patient of each class (the run's evidence folder lists them as <id>_<class>_P_vs_C2.png)
    first = {}
    for path in sorted((Path(e10_dir) / "evidence").glob("*_P_vs_C2.png")):
        pid, cls = path.name.split("_")[:2]
        first.setdefault(cls, pid)
    # the four strips share one panel (stored voxels: one row per slice, 140 rows shown, as before)
    axa = fig.add_subplot(gs[0, :])
    sw, sh, gx, gy, top = 432, 140, 40, 42, 46  # strip width and height, gaps, title band (pixels)
    for c, (pid, cname) in enumerate([(first["HCC"], "HCC"), (first["CHCC"], "cHCC-CCA")]):
        for r, (ph, phname) in enumerate([("P", "non-contrast"), ("C2", "portal venous")]):
            ct = _load_nii(Path(raw_dir) / f"{pid}_{ph}_ct.nii.gz")
            tm = _load_nii(Path(raw_dir) / f"{pid}_{ph}_mask.nii.gz") > 0
            jj = int(round(np.nonzero(tm)[1].mean()))
            img, msk = ct[40:472, jj, :].T[:sh], tm[40:472, jj, :].T[:sh]
            x0, y0 = c * (sw + gx), top + r * (sh + gy)
            n = img.shape[0]
            axa.imshow(
                img,
                cmap="gray",
                vmin=0,
                vmax=255,
                extent=(x0, x0 + sw, y0 + n, y0),
                interpolation="nearest",
            )
            if msk.any():
                axa.contour(
                    x0 + np.arange(sw) + 0.5,
                    y0 + np.arange(n) + 0.5,
                    msk.astype(float),
                    levels=[0.5],
                    colors=[S4],
                    linewidths=0.7,
                )
            head = f"{cname} {pid}\n" if r == 0 else ""
            axa.text(
                x0,
                y0 - 4,
                f"{head}{phname.capitalize()}: {ct.shape[2]} slices",
                fontsize=8,
                ha="left",
                va="bottom",
            )
    axa.set_xlim(0, 2 * sw + gx)
    axa.set_ylim(top + 2 * sh + gy, 0)
    axa.set_aspect("equal")
    axa.axis("off")
    axa.text(
        -0.01,
        1.0,
        "A",
        transform=axa.transAxes,
        fontsize=10,
        fontweight="bold",
        ha="right",
        va="top",
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
            fontsize=8,
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
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlim(-0.4, 1.1)
    ax.set_ylim(-(y + 0.4), -0.2)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    grid_x(ax)
    ax.set_xlabel("Shift toward the simulated class\n(vs smoothing control; mean, 95% CI)")
    ax.legend(
        handles=[
            Line2D(
                [],
                [],
                color=INK2,
                marker="o",
                lw=0,
                ms=5,
                label="Meets every pre-specified criterion",
            ),
            Line2D([], [], color=INK2, marker="o", mfc="white", lw=0, ms=5, label="Not claimed"),
            Line2D(
                [],
                [],
                color=INK2,
                marker="|",
                lw=0,
                ms=7,
                mew=1.4,
                label="Smoothing control alone (|change|)",
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
        ax.text(0, -y, cname, fontsize=8, fontweight="bold", va="center", color=INK, zorder=5)
        for state, sname in [
            ("control", "Unchanged"),
            (cond + "_smooth", "Smoothing control"),
            (cond, "Counterfactual"),
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
                if cnt[k] >= 15:
                    ax.text(
                        left + cnt[k] / 2,
                        -y,
                        str(cnt[k]),
                        ha="center",
                        va="center",
                        fontsize=8,
                        color="white",
                    )
                left += cnt[k]
            ticks.append(-y)
            labels.append(sname)
        y += 0.3
    ax.set_yticks(ticks)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_ylim(-(y + 0.4), -0.2)
    ax.set_xlim(0, 196)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Patients by CNN-predicted class")
    ax.legend(
        handles=[plt.Rectangle((0, 0), 1, 1, color=CLASS_COL[c]) for c in CLASSES],
        labels=CLASSES,
        title="Predicted class",
        title_fontsize=8,
        alignment="left",
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
    fig = plt.figure(figsize=(WIDTH * MM, 180 * MM), layout="constrained")
    fig.get_layout_engine().set(w_pad=0.03, h_pad=0.05, wspace=0.03, hspace=0.04)
    sf_top, sf_bot = fig.subfigures(2, 1, height_ratios=[0.66, 1])
    sf_int, sf_ext = sf_top.subfigures(1, 2, width_ratios=[5, 2.05])
    sf_int.suptitle("PLC-CECT, held-out patients", fontsize=8)
    sf_ext.suptitle("MCT-LTDiag", fontsize=8)
    grid_int, grid_ext = sf_int.add_gridspec(2, 5), sf_ext.add_gridspec(2, 2)
    sf_top.text(0.0, 1.0, "A", fontsize=10, fontweight="bold", ha="left", va="top")
    tiles = [
        ("fig8_internal_HCC", "cam_pred", "HCC"),
        ("fig8_internal_ICC", "cam_pred", "ICC"),
        ("fig8_internal_CHCC", "cam_pred", "cHCC-CCA"),
        ("fig8_internal_misclassified", "cam_pred", "cHCC-CCA,\npredicted HCC"),
        ("fig8_internal_misclassified", "cam_true", "Same case,\ntrue-class map"),
        ("fig8_mct_HCC", "cam_pred", "HCC"),
        ("fig8_mct_ICC", "cam_pred", "ICC"),
    ]
    names3 = ["HCC", "ICC", "cHCC-CCA"]
    for c, (tag, cam, head) in enumerate(tiles):
        m = meta[tag]
        ct, tm, cm = ex[f"{tag}_ct"][2], ex[f"{tag}_tm"][2], ex[f"{tag}_{cam}"]
        pr = m["probabilities"]
        k = int(np.argmax(pr))
        for r in range(2):
            ax = (
                sf_int.add_subplot(grid_int[r, c])
                if c < 5
                else sf_ext.add_subplot(grid_ext[r, c - 5])
            )
            _tile(ax, ct, tm)
            if r == 1:
                ax.imshow(cm / cm.max(), cmap=heat, vmin=0, vmax=1, interpolation="bilinear")
            if r == 0:
                ax.set_title(
                    f"{head}\n{m['patient_id']}", fontsize=8, color=INK, pad=3, linespacing=1.1
                )
            else:
                lab_ = f"{names3[k]} {pr[k]:.2f}" if cam == "cam_pred" else f"cHCC-CCA {pr[2]:.2f}"
                ax.text(
                    0.5,
                    -0.06,
                    lab_,
                    transform=ax.transAxes,
                    ha="center",
                    va="top",
                    fontsize=8,
                    color=INK2,
                )
            if c == 0:
                ax.set_ylabel("Portal venous" if r == 0 else "Grad-CAM", fontsize=8, color=INK)
    bot = sf_bot.add_gridspec(1, 2, width_ratios=[1.3, 1])
    # B: attention enrichment over chance, portal-venous crop, per patient
    ax = sf_bot.add_subplot(bot[0])
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
            ("internal_held_out", "ICC", "ICC, ≥ 90% inside liver mask", "in"),
            ("internal_held_out", "ICC", "ICC, < 90% inside liver mask", "out"),
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
            fontsize=8,
            color=INK2,
        )
    ax.axvline(1, color=MUTED, lw=0.9, ls=(0, (3, 2)))
    ax.set_yticks(range(len(groups)))
    ax.set_yticklabels([g[2] for g in groups][::-1], fontsize=8)
    ax.set_xlim(0, 3.2)
    ax.set_xlabel("Tumor attention ÷ tumor share of crop\n(1 = chance; dot = median, bar = IQR)")
    grid_x(ax)
    panel(ax, "B", "Attention on the tumor")
    # C: per-phase share of |gradient × input|
    ax = sf_bot.add_subplot(bot[1])
    sh = Sh[~Sh["black_crop"]] if "black_crop" in Sh.columns else Sh
    rows = [
        ("internal_held_out", "HCC", "PLC-CECT HCC"),
        ("internal_held_out", "ICC", "PLC-CECT ICC"),
        ("internal_held_out", "CHCC", "PLC-CECT cHCC-CCA"),
        ("MCT_LTDiag", "HCC", "MCT-LTDiag HCC"),
        ("MCT_LTDiag", "ICC", "MCT-LTDiag ICC"),
    ]
    pcols = ["#3987e5", "#86b6ef", "#cde2fb", "#c3c2b7"]
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
                fontsize=8,
                color=TEXT,
            )
            left += v[k]
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r_[2] for r_ in rows][::-1], fontsize=8)
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
    panel(ax, "C", "Phase contribution")
    save(fig, "Figure8_gradcam")


FIGURES = {
    "design": figure_design,
    "design_public": lambda: figure_design(public=True),
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
