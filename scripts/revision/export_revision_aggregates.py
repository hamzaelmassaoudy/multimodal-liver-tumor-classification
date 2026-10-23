#!/usr/bin/env python
"""Export the cohort-level results of the October 2026 revision from authorized run outputs.

The inputs are the run folders written by notebooks 15-33 (``liver_project/revision_2026-10``)
and the split and label files of the private project folder. Every output table is aggregated
over patients: no identifier, probability, label, or split membership is written.

Example::

    python scripts/revision/export_revision_aggregates.py \
        --project-root "$PRIVATE_ARTIFACT_ROOT/liver_project" \
        --mask-census-summary path/to/tumor_inside_liver_mask_by_class_phase.csv \
        --mask-census-performance path/to/performance_by_tumor_inside_liver_mask.csv \
        --hcc-tace-seg-catalog path/to/hcc_tace_seg_catalog \
        --output results/revision_2026-10
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

RUNS = {
    "E1_E2": "E1_E2_20261017T032941Z",
    "E3": "E3_20261017T041700Z",
    "E5": "E5_20261017T062958Z",
    "E5c": "E5c_20261017T143217Z",
    "E6": "E6_20261017T114646Z",
    "E7a": "E7a_20261017T191025Z",
    "E8a": "E8a_20261017T162800Z",
    "E8b": "E8b_20261018T025705Z",
    "E47": "E47_20261018T092239Z",
    "E4d": "E4d_20261019T030857Z",
    "E10": "E10_20261019T031225Z",
    "F2": "F2_20261019T090444Z",
    "E11": "E11_20261019T195325Z",
    "E12": "E12_20261022T025246Z",
    "E13": "E13_20261022T024552Z",
    "E14a": "E14a_20261023T052443Z",
    "E14b": "E14b_20261023T052254Z",
    "E15": "E15_20261023T052328Z",
}
MAIN = {
    "CNN": "phase_dropout_CNN",
    "radiomics": "radiomics_noshape",
    "CNN + radiomics": "cnn_plus_radiomics [phase_dropout_CNN]",
    "full fusion": "full_fusion [phase_dropout_CNN]",
}
CLASS_NAMES = {"HCC": "HCC", "ICC": "ICC", "CHCC": "cHCC-CCA"}


def read(runs: Path, run: str, name: str, **kwargs) -> pd.DataFrame:
    return pd.read_csv(runs / RUNS[run] / name, **kwargs)


def benjamini_hochberg(p_values: np.ndarray) -> np.ndarray:
    order = np.argsort(p_values)
    adjusted = np.empty_like(p_values, dtype=float)
    running = 1.0
    n = len(p_values)
    for rank, index in reversed(list(enumerate(order, start=1))):
        running = min(running, p_values[index] * n / rank)
        adjusted[index] = running
    return adjusted


def macro_auc(y: np.ndarray, p: np.ndarray) -> float:
    return float(np.mean([roc_auc_score(y == k, p[:, k]) for k in range(3)]))


def internal_models(runs: Path) -> pd.DataFrame:
    e2 = read(runs, "E1_E2", "E2_main_results.csv").query("analysis == 'E2_no_shape_main'")
    e2 = e2.set_index("model_key")
    e2_ci = read(runs, "E1_E2", "E2_bootstrap_ci.csv").query("analysis == 'E2_no_shape_main'")
    e2_ci = e2_ci.set_index("model_key")
    final = read(runs, "E47", "E7b_internal_final_metrics.csv").set_index("model")
    e3 = read(runs, "E3", "E3_all_cnns_by_pattern.csv").query("pattern == 'complete'")
    e3 = e3.set_index("model")
    e3f = read(runs, "E3", "E3C_fusion_by_cnn_and_pattern.csv").query("pattern == 'complete'")
    e3f = e3f.set_index("model")
    rcv = read(runs, "E7a", "E7a_summary.csv").set_index("model")
    nop = read(runs, "E8b", "E8b_E9_internal_results.csv").set_index("model")
    rows = []
    for name, key in [
        ("clinical (age, sex)", "clinical_only"),
        ("single-phase CNN", "single_phase_cnn"),
    ]:
        r, c = e2.loc[key], e2_ci.loc[key]
        rows.append(
            {
                "model": name,
                "heldout_macro_auc": r.test_macro_auc,
                "heldout_ci_low": c.ci_95_low,
                "heldout_ci_high": c.ci_95_high,
                "heldout_accuracy": r.test_accuracy,
                "heldout_macro_f1": r.test_macro_f1,
                "cv_original_folds_mean": r.cv_macro_auc_mean,
                "cv_original_folds_sd": r.cv_macro_auc_sd,
            }
        )
    spec = [
        ("original CNN", "original_CNN", ("cnn", "original"), None, None),
        (
            "phase-dropout CNN (main)",
            "phase_dropout_CNN",
            ("cnn", "D_phase_dropout"),
            "phase_dropout_CNN",
            "CNN noP_CNN [noP]",
        ),
        (
            "radiomics (no shape features)",
            "radiomics_noshape",
            ("e2", "radiomics"),
            "radiomics_noshape",
            "radiomics radiomics_noP",
        ),
        (
            "CNN + radiomics",
            "cnn_plus_radiomics [phase_dropout_CNN]",
            ("fusion", "cnn_plus_radiomics [D_phase_dropout CNN]"),
            "cnn_plus_radiomics",
            "cnn_plus_radiomics: E9: noP_CNN + radiomics_noP",
        ),
        (
            "full fusion (+ age, sex)",
            "full_fusion [phase_dropout_CNN]",
            ("fusion", "full_fusion [D_phase_dropout CNN]"),
            "full_fusion",
            "full_fusion: E9: noP_CNN + radiomics_noP",
        ),
    ]
    for name, key, (cv_source, cv_key), rcv_key, nop_key in spec:
        r = final.loc[key]
        cv = {"cnn": e3, "fusion": e3f, "e2": e2}[cv_source].loc[cv_key]
        row = {
            "model": name,
            "heldout_macro_auc": r.test_macro_auc,
            "heldout_ci_low": r.boot_low,
            "heldout_ci_high": r.boot_high,
            "heldout_accuracy": r.test_accuracy,
            "heldout_macro_f1": r.test_macro_f1,
            "cv_original_folds_mean": cv.cv_macro_auc_mean,
            "cv_original_folds_sd": cv.cv_macro_auc_sd,
        }
        if rcv_key:
            row["repeated_cv_oof_mean"] = rcv.loc[rcv_key, "oof_pooled_mean"]
            row["repeated_cv_oof_sd"] = rcv.loc[rcv_key, "oof_pooled_sd"]
            row["repeated_cv_heldout_mean"] = rcv.loc[rcv_key, "held_out_mean"]
            row["heldout_without_noncontrast"] = nop.loc[nop_key, "test_macro_auc"]
            row["heldout_without_noncontrast_ci_low"] = nop.loc[nop_key, "boot_low"]
            row["heldout_without_noncontrast_ci_high"] = nop.loc[nop_key, "boot_high"]
        rows.append(row)
    return pd.DataFrame(rows)


def internal_comparisons(runs: Path) -> pd.DataFrame:
    boot = read(runs, "E47", "E7b_paired_bootstrap_main_pairs.csv")
    delong = read(runs, "E47", "E7b_delong_main_pairs_bh.csv")
    rcv = read(runs, "E7a", "E7a_paired_differences.csv")
    rcv_keys = {
        "phase_dropout_CNN": "phase_dropout_CNN",
        "radiomics_noshape": "radiomics_noshape",
        "cnn_plus_radiomics [phase_dropout_CNN]": "cnn_plus_radiomics",
        "full_fusion [phase_dropout_CNN]": "full_fusion",
    }
    pairs = [
        ("full fusion", "CNN + radiomics"),
        ("CNN + radiomics", "radiomics"),
        ("CNN + radiomics", "CNN"),
        ("full fusion", "radiomics"),
        ("full fusion", "CNN"),
        ("CNN", "radiomics"),
    ]
    rows = []
    for a, b in pairs:
        ka, kb = MAIN[a], MAIN[b]
        hit = boot[(boot.model_a == ka) & (boot.model_b == kb)]
        sign = 1.0
        if hit.empty:
            hit, sign = boot[(boot.model_a == kb) & (boot.model_b == ka)], -1.0
        hit = hit.iloc[0]
        low, high = sorted([sign * hit.boot_low, sign * hit.boot_high])
        tests = delong[
            ((delong.model_a == ka) & (delong.model_b == kb))
            | ((delong.model_a == kb) & (delong.model_b == ka))
        ]
        best = tests.loc[tests.p_bh.idxmin()]
        row = {
            "comparison": f"{a} - {b}",
            "heldout_difference": sign * hit.difference,
            "ci_low": low,
            "ci_high": high,
            "bootstrap_p": hit.boot_two_sided_p,
            "smallest_bh_delong_p": best.p_bh,
            "smallest_bh_delong_class": CLASS_NAMES[best["class"]],
            "delong_tests_adjusted": len(delong),
        }
        rep = rcv[(rcv.model_a == rcv_keys[ka]) & (rcv.model_b == rcv_keys[kb])]
        rep_sign = 1.0
        if rep.empty:
            rep = rcv[(rcv.model_a == rcv_keys[kb]) & (rcv.model_b == rcv_keys[ka])]
            rep_sign = -1.0
        if not rep.empty:
            rep = rep.iloc[0]
            row["repeated_cv_oof_difference"] = rep_sign * rep.oof_diff_mean
            row["repeated_cv_heldout_difference"] = rep_sign * rep.held_out_diff_mean
            better_oof, better_held = rep.repeats_a_better_oof, rep.repeats_a_better_held_out
            row["repeats_first_higher_oof"] = better_oof if rep_sign > 0 else 5 - better_oof
            row["repeats_first_higher_heldout"] = better_held if rep_sign > 0 else 5 - better_held
        rows.append(row)
    primary = read(runs, "E1_E2", "E2_paired_bootstrap_deltas.csv").iloc[0]
    rows.append(
        {
            "comparison": "full fusion - CNN + radiomics (pre-specified, original CNN)",
            "heldout_difference": primary.delta,
            "ci_low": primary.ci_low,
            "ci_high": primary.ci_high,
            "bootstrap_p": primary.bootstrap_two_sided_p,
        }
    )
    return pd.DataFrame(rows)


def internal_per_class(runs: Path) -> pd.DataFrame:
    final = read(runs, "E47", "E7b_internal_final_metrics.csv").set_index("model")
    rows = []
    for name, key in MAIN.items():
        r = final.loc[key]
        for cls in ("HCC", "ICC", "CHCC"):
            for metric in ("sens", "spec"):
                rows.append(
                    {
                        "model": name,
                        "class": CLASS_NAMES[cls],
                        "metric": {"sens": "sensitivity", "spec": "specificity"}[metric],
                        "value": r[f"{metric}_{cls}"],
                        "ci_low": r[f"{metric}_{cls}_low"],
                        "ci_high": r[f"{metric}_{cls}_high"],
                    }
                )
    return pd.DataFrame(rows)


def acquisition_only(runs: Path, project: Path) -> pd.DataFrame:
    """Post hoc: how well slice counts alone predict the class (internal) and HCC vs ICC."""
    shapes = read(runs, "E8b", "E9a_internal_header_shapes.csv", dtype={"patient_id": str})
    features = np.log(
        shapes.pivot(index="patient_id", columns="phase", values="n_slices")[
            ["P", "C1", "C2", "C3"]
        ]
    )
    labels = pd.read_parquet(project / "radiomics" / "radiomics_features.parquet")
    labels = labels.assign(patient_id=labels.patient_id.astype(str)).set_index("patient_id")
    y = labels.loc[features.index, "label"].to_numpy()
    split = json.loads((project / "splits" / "train_val_test.json").read_text())
    dev = features.index.isin([str(x) for x in split["dev_ids"]])
    test = features.index.isin([str(x) for x in split["test_ids"]])
    rows = []
    for name, model in [
        ("logistic", make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))),
        ("random forest", RandomForestClassifier(300, min_samples_leaf=5, random_state=42)),
    ]:
        model.fit(features[dev].to_numpy(), y[dev])
        held = macro_auc(y[test], model.predict_proba(features[test].to_numpy()))
        rows.append({"analysis": f"slice counts only, 3 classes, held-out ({name})", "auc": held})
    preds = read(runs, "E8b", "E8b_E9_predictions.csv", dtype={"patient_id": str})
    key = "cnn_plus_radiomics: [ref] phase_dropout_CNN + radiomics_noshape"
    oof = preds[(preds.cohort == "internal_oof") & (preds.model == key)].set_index("patient_id")
    oof = oof.assign(label=labels.loc[oof.index, "label"].to_numpy())
    hi = oof[oof.label.isin([0, 1])]
    y_hi = (hi.label == 0).to_numpy().astype(int)
    p_hi = np.clip(hi.p_HCC / (hi.p_HCC + hi.p_ICC), 1e-6, 1 - 1e-6)
    score = np.log(p_hi / (1 - p_hi)).to_numpy()
    cv = StratifiedKFold(5, shuffle=True, random_state=42)
    slice_only = cross_val_predict(
        make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)),
        features.loc[hi.index].to_numpy(),
        y_hi,
        cv=cv,
        method="predict_proba",
    )[:, 1]
    middle = (slice_only > np.quantile(slice_only, 0.25)) & (
        slice_only < np.quantile(slice_only, 0.75)
    )
    rows += [
        {
            "analysis": "slice counts only, HCC vs ICC, out-of-fold",
            "auc": roc_auc_score(y_hi, slice_only),
        },
        {"analysis": "CNN + radiomics, HCC vs ICC, out-of-fold", "auc": roc_auc_score(y_hi, score)},
        {
            "analysis": "CNN + radiomics, HCC vs ICC, ambiguous slice counts "
            f"(n = {int(middle.sum())})",
            "auc": roc_auc_score(y_hi[middle], score[middle]),
        },
        {
            "analysis": "slice counts only, HCC vs ICC, ambiguous slice counts "
            f"(n = {int(middle.sum())})",
            "auc": roc_auc_score(y_hi[middle], slice_only[middle]),
        },
    ]
    return pd.DataFrame(rows).assign(post_hoc=True)


def dataset_audit(runs: Path) -> pd.DataFrame:
    rows = []
    census = read(runs, "E10", "E10a_census_by_class.csv").set_index("class")
    for cls, r in census.iterrows():
        rows += [
            {"class": CLASS_NAMES[cls], "phase": "all", "measure": m, "value": r[m]}
            for m in ("files", "three_channel_files", "patients_with_three_channel")
        ]
    empty = read(runs, "E10", "E10a_empty_masks.csv")
    for cls in CLASS_NAMES:
        sub = empty[empty["class"] == cls]
        rows.append(
            {
                "class": CLASS_NAMES[cls],
                "phase": "all",
                "measure": "scans_with_empty_liver_mask",
                "value": int(sub.liver_mask_empty.sum()),
            }
        )
        rows.append(
            {
                "class": CLASS_NAMES[cls],
                "phase": "all",
                "measure": "patients_with_empty_liver_mask",
                "value": int(sub[sub.liver_mask_empty].patient_id.nunique()),
            }
        )
        rows.append(
            {
                "class": CLASS_NAMES[cls],
                "phase": "all",
                "measure": "scans_with_empty_tumor_mask",
                "value": int(sub.tumour_mask_empty.sum()),
            }
        )
    anatomy = read(runs, "E10", "E10b_anatomy_by_class.csv")
    for _, r in anatomy.iterrows():
        for m, label in [
            ("median_slices", "median_slices"),
            ("median_liver_slices", "median_liver_slices"),
            ("median_ratio", "median_liver_slices_per_liver_width"),
            ("median_coverage", "median_share_of_slices_with_liver"),
        ]:
            rows.append(
                {
                    "class": CLASS_NAMES[r["class"]],
                    "phase": r.phase,
                    "measure": label,
                    "value": r[m],
                }
            )
    within = read(runs, "E10", "E10b_noncontrast_within_patient.csv").set_index("class")
    for cls, r in within.iterrows():
        rows.append(
            {
                "class": CLASS_NAMES[cls],
                "phase": "P/C2",
                "measure": "median_noncontrast_over_portal_venous_slices",
                "value": r.median_slices_P_over_C2,
            }
        )
        rows.append(
            {
                "class": CLASS_NAMES[cls],
                "phase": "P/C2",
                "measure": "median_noncontrast_over_portal_venous_liver_slices",
                "value": r.median_liver_slices_P_over_C2,
            }
        )
    return pd.DataFrame(rows)


def counterfactual(runs: Path, project: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    effects = read(runs, "E10", "E10c_effects.csv")
    preds = read(runs, "E10", "E10c_predictions.csv", dtype={"patient_id": str})
    labels = pd.read_parquet(project / "radiomics" / "radiomics_features.parquet")
    labels = labels.assign(patient_id=labels.patient_id.astype(str)).set_index("patient_id")[
        "label"
    ]
    preds["label"] = preds.patient_id.map(labels)
    preds["predicted"] = preds[["p_HCC", "p_ICC", "p_CHCC"]].to_numpy().argmax(1)
    groups = [
        ("HCC scans to ICC-like slice density", "swap", [0]),
        ("ICC scans to HCC-like slice density", "swap", [1]),
        ("non-contrast artifact injected (HCC and ICC)", "inject", [0, 1]),
        ("non-contrast artifact repaired (cHCC-CCA)", "repair", [2]),
    ]
    rows = []
    for model in preds.model.unique():
        for name, condition, classes in groups:
            for state in ("control", f"{condition}_smooth", condition):
                sub = preds[
                    (preds.model == model) & (preds.condition == state) & preds.label.isin(classes)
                ]
                counts = np.bincount(sub.predicted, minlength=3)
                rows.append(
                    {
                        "model": model,
                        "test": name,
                        "scans": {"control": "unchanged"}.get(
                            state,
                            "smoothing control" if state.endswith("smooth") else "counterfactual",
                        ),
                        "patients": len(sub),
                        "predicted_HCC": counts[0],
                        "predicted_ICC": counts[1],
                        "predicted_cHCC_CCA": counts[2],
                    }
                )
    return effects, pd.DataFrame(rows)


def external(runs: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    mct = read(runs, "E8a", "E8_0_E6_203_results.csv")
    calibration = read(runs, "E47", "E7c_calibration.csv")
    e8a = read(runs, "E8a", "E8a_mct203_results.csv").assign(source="radiomics mitigation")
    e8b = read(runs, "E8b", "E8b_E9_mct203_results.csv").assign(
        source="CNN mitigation and no non-contrast"
    )
    e8a_paired = read(runs, "E8a", "E8a_paired_differences.csv").rename(
        columns={
            "mitigated": "model",
            "reference": "reference_model",
            "difference": "auc_difference",
        }
    )
    e8a_paired["bh_adjusted_p"] = benjamini_hochberg(e8a_paired.delong_p.to_numpy())
    e8a_paired["comparison_family"] = "radiomics mitigation (9 comparisons)"
    e8b_paired = read(runs, "E8b", "E8b_E9_mct203_paired_differences.csv").rename(
        columns={"reference": "reference_model", "difference": "auc_difference"}
    )
    e8b_paired["bh_adjusted_p"] = benjamini_hochberg(e8b_paired.delong_p.to_numpy())
    e8b_paired["comparison_family"] = "CNN mitigation and no non-contrast (17 comparisons)"
    keep = [
        "comparison_family",
        "model",
        "reference_model",
        "auc_difference",
        "boot_low",
        "boot_high",
        "delong_p",
        "bh_adjusted_p",
    ]
    paired = pd.concat([e8a_paired[keep], e8b_paired[keep]], ignore_index=True)
    mitigation = pd.concat([e8a, e8b], ignore_index=True)
    return mct, calibration, mitigation, paired


def hcc_tace_seg(runs: Path) -> pd.DataFrame:
    e5c = read(runs, "E5c", "E5c_results.csv").assign(analysis="pipeline corrections")
    e5 = read(runs, "E5", "E5_results.csv").query(
        "model == 'radiomics_noshape_MEDIANS_ONLY_control'"
    )
    e5 = e5.rename(columns={"window": "variant"}).assign(analysis="medians-only imputation control")
    e8b = read(runs, "E8b", "E8b_E9_hcc_tace_seg_results.csv").assign(
        analysis="mitigation (primary corrected geometry)", variant="axis_fixed_E6rules"
    )
    e4d = read(runs, "E4d", "E4d_hcc_tace_seg_results.csv").assign(
        analysis="adaptive crop (primary corrected geometry)", variant="axis_fixed_E6rules"
    )
    return pd.concat([e5c, e5, e8b, e4d], ignore_index=True)


def _midrank(x: np.ndarray) -> np.ndarray:
    order = np.argsort(x)
    s = x[order]
    ranks = np.zeros(len(x))
    i = 0
    while i < len(x):
        j = i
        while j < len(x) and s[j] == s[i]:
            j += 1
        ranks[i:j] = 0.5 * (i + j - 1) + 1
        i = j
    out = np.empty(len(x))
    out[order] = ranks
    return out


def _delong(y: np.ndarray, s: np.ndarray) -> tuple[float, np.ndarray, np.ndarray]:
    pos, neg = s[y == 1], s[y == 0]
    m, n = len(pos), len(neg)
    tz = _midrank(np.concatenate([pos, neg]))
    auc = tz[:m].sum() / m / n - (m + 1) / 2 / n
    return auc, (tz[:m] - _midrank(pos)) / n, 1 - (tz[m:] - _midrank(neg)) / m


def mct_by_sex(runs: Path, project: Path) -> pd.DataFrame:
    """Post hoc: MCT-LTDiag HCC-vs-ICC AUC of CNN + radiomics and full fusion within each sex."""
    meta = (
        project
        / "external_validation"
        / "MCT-LTDiag"
        / "metadata"
        / "selected_HCC_ICC_patients.csv"
    )
    sel = pd.read_csv(meta, dtype=str).set_index("patient_id")
    preds = read(runs, "E8b", "E8b_E9_predictions.csv", dtype={"patient_id": str})
    preds = preds[preds.cohort == "MCT_LTDiag"]
    keys = {
        "CNN + radiomics": "cnn_plus_radiomics: [ref] phase_dropout_CNN + radiomics_noshape",
        "full fusion": "full_fusion: [ref] phase_dropout_CNN + radiomics_noshape",
    }
    ids = sorted(set(preds.patient_id) & set(sel.index))
    y = (sel.loc[ids, "type"] == "HCC").astype(int).to_numpy()
    sex = sel.loc[ids, "patient_sex"].str.strip().str.upper().to_numpy()
    score = {}
    for name, key in keys.items():
        t = preds[preds.model == key].set_index("patient_id").loc[ids]
        score[name] = (t.p_HCC / (t.p_HCC + t.p_ICC)).to_numpy()
    rows = []
    for group, keep in [
        ("all", np.ones(len(ids), bool)),
        ("men", sex == "M"),
        ("women", sex == "F"),
    ]:
        yy, comps = y[keep], {}
        for name in keys:
            auc, v01, v10 = _delong(yy, score[name][keep])
            se = np.sqrt(np.var(v01, ddof=1) / len(v01) + np.var(v10, ddof=1) / len(v10))
            comps[name] = (v01, v10)
            rows.append(
                {
                    "group": group,
                    "n_HCC": int(yy.sum()),
                    "n_ICC": int((1 - yy).sum()),
                    "model": name,
                    "auc": auc,
                    "delong_low": max(0.0, auc - 1.96 * se),
                    "delong_high": min(1.0, auc + 1.96 * se),
                    "post_hoc": True,
                }
            )
        (a01, a10), (b01, b10) = comps["full fusion"], comps["CNN + radiomics"]
        cov = np.cov(np.vstack([a01, b01])) / len(a01) + np.cov(np.vstack([a10, b10])) / len(a10)
        diff = rows[-1]["auc"] - rows[-2]["auc"]
        p = float(2 * norm.sf(abs(diff) / np.sqrt(cov[0, 0] + cov[1, 1] - 2 * cov[0, 1])))
        rows.append(
            {
                "group": group,
                "n_HCC": int(yy.sum()),
                "n_ICC": int((1 - yy).sum()),
                "model": "full fusion - CNN + radiomics",
                "auc": diff,
                "paired_delong_p": p,
                "post_hoc": True,
            }
        )
    return pd.DataFrame(rows)


P3 = ["p_HCC", "p_ICC", "p_CHCC"]
ORDER = ["HCC", "ICC", "CHCC"]
REF_FUSION = "cnn_plus_radiomics: [ref] phase_dropout_CNN + radiomics_noshape"


def _logit(p: np.ndarray) -> np.ndarray:
    """As in the calibration cell of notebook 22 (E7c)."""
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def _logistic_fit(x, y, offset=None, slope=True, iters=100):
    """As in the calibration cell of notebook 22 (E7c)."""
    a, b = 0.0, 1.0 if not slope else 0.0
    off = np.zeros_like(x) if offset is None else offset
    for _ in range(iters):
        eta = a + (b * x if slope else 0) + off
        p = 1 / (1 + np.exp(-eta))
        w = p * (1 - p) + 1e-12
        if slope:
            design = np.column_stack([np.ones_like(x), x])
            hess = design.T @ (design * w[:, None])
            step = np.linalg.solve(hess + 1e-9 * np.eye(2), design.T @ (y - p))
            a, b = a + step[0], b + step[1]
        else:
            step = (y - p).sum() / w.sum()
            a += step
        if np.max(np.abs(step)) < 1e-10:
            break
    return a, b


def _labels(project: Path) -> pd.Series:
    lab = pd.read_parquet(project / "radiomics" / "radiomics_features.parquet")
    lab = lab[["patient_id", "label"]].assign(patient_id=lambda d: d.patient_id.astype(str))
    lab = lab.drop_duplicates("patient_id").set_index("patient_id")["label"]
    return lab.map(dict(enumerate(ORDER)))


def _folds(project: Path) -> dict:
    return {
        str(pid): k
        for k in range(5)
        for pid in json.loads((project / "splits" / f"fold_{k}.json").read_text())["val_ids"]
    }


def _mct_meta(project: Path) -> pd.DataFrame:
    meta = project / "external_validation" / "MCT-LTDiag" / "metadata"
    return pd.read_csv(meta / "selected_HCC_ICC_patients.csv", dtype=str).set_index("patient_id")


def _hcc_icc(frame: pd.DataFrame, labels: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    y = labels.loc[frame.patient_id].to_numpy()
    keep = np.isin(y, ["HCC", "ICC"])
    s = (frame.p_HCC / (frame.p_HCC + frame.p_ICC)).to_numpy()
    return (y[keep] == "HCC").astype(int), s[keep]


def _delong_ci(y: np.ndarray, s: np.ndarray) -> tuple[float, float, float]:
    auc, v01, v10 = _delong(y, s)
    se = np.sqrt(np.var(v01, ddof=1) / len(v01) + np.var(v10, ddof=1) / len(v10))
    return auc, max(0.0, auc - 1.96 * se), min(1.0, auc + 1.96 * se)


def _macro(frame: pd.DataFrame, labels: pd.Series) -> float:
    y, p = labels.loc[frame.patient_id].to_numpy(), frame[P3].to_numpy()
    return float(np.mean([roc_auc_score(y == c, p[:, j]) for j, c in enumerate(ORDER)]))


def _calls(frame: pd.DataFrame) -> np.ndarray:
    return np.array(ORDER)[frame[P3].to_numpy().argmax(1)]


def manuscript_values(runs: Path, project: Path, catalog: Path | None) -> pd.DataFrame:
    """Values reported in the revised manuscript that no other table contains (aggregates only)."""
    labels, folds, meta = _labels(project), _folds(project), _mct_meta(project)
    mct = meta["type"]
    preds = read(runs, "E8b", "E8b_E9_predictions.csv", dtype={"patient_id": str})
    held = sorted(set(preds[preds.cohort == "internal_test"].patient_id))
    dev = sorted(folds)
    rows = []

    def add(section, quantity, value, low=np.nan, high=np.nan, n=np.nan, post_hoc=False, run=""):
        rows.append(
            {
                "section": section,
                "quantity": quantity,
                "value": value,
                "ci_low": low,
                "ci_high": high,
                "n": n,
                "post_hoc": post_hoc,
                "source_run": run,
            }
        )

    def pick(cohort, key):
        return preds[(preds.cohort == cohort) & (preds.model == key)]

    # Sections 4.3 and 4.4: one-versus-rest AUCs on the held-out set
    for name, key in [
        ("CNN + radiomics", REF_FUSION),
        ("radiomics", "radiomics radiomics_noshape"),
    ]:
        t = pick("internal_test", key)
        y, p = labels.loc[t.patient_id].to_numpy(), t[P3].to_numpy()
        for j, c in enumerate(ORDER):
            auc = roc_auc_score(y == c, p[:, j])
            add(
                "4.3",
                f"held-out one-vs-rest AUC, {name}, {CLASS_NAMES[c]}",
                auc,
                n=len(t),
                run="E8b",
            )
    # Section 4.8 and Figure 7B: calibration of the HCC-versus-ICC score
    for cohort, lab, tag in [
        ("internal_test", labels, "39 held-out HCC and ICC patients"),
        ("MCT_LTDiag", mct, "MCT-LTDiag"),
    ]:
        y, s = _hcc_icc(pick(cohort, REF_FUSION), lab)
        y = y.astype(float)
        intercept, _ = _logistic_fit(_logit(s), y, offset=_logit(s), slope=False)
        _, slope = _logistic_fit(_logit(s), y, slope=True)
        post = cohort == "internal_test"
        for q, v in [
            ("calibration-in-the-large", intercept),
            ("calibration slope", slope),
            ("Brier score", float(np.mean((s - y) ** 2))),
        ]:
            add("4.8", f"{q}, CNN + radiomics, {tag}", v, n=len(y), post_hoc=post, run="E8b")
    # Section 4.8: sex alone and the first run of the primary evaluation
    y = (meta["type"] == "HCC").astype(int).to_numpy()
    male = meta["patient_sex"].str.strip().str.upper().eq("M").astype(int).to_numpy()
    add(
        "4.8",
        "MCT-LTDiag HCC-vs-ICC AUC of sex alone",
        *_delong_ci(y, male),
        n=len(y),
        post_hoc=True,
    )
    e6 = read(runs, "E6", "E6_results.csv")
    e6 = e6[(e6.variant == "primary") & (e6.subset == "all")]
    r = e6[e6.model == MAIN["CNN + radiomics"]].iloc[0]
    add(
        "4.8",
        "first run of the primary MCT-LTDiag evaluation (two patients excluded "
        "contrary to the plan), CNN + radiomics HCC-vs-ICC AUC",
        r.auc,
        r.auc_delong_low,
        r.auc_delong_high,
        n=int(r.n),
        run="E6",
    )
    p80 = read(runs, "E8a", "E8_0_E6_203_predictions.csv", dtype={"patient_id": str})
    p80 = p80[(p80.model == "phase_dropout_CNN") & (p80.variant == "primary")].set_index(
        "patient_id"
    )
    p8b = pick("MCT_LTDiag", "CNN phase_dropout_CNN").set_index("patient_id").loc[p80.index]
    diff = np.abs(p80[P3].to_numpy() - p8b[P3].to_numpy()).max()
    add(
        "4.8",
        "largest probability difference between the two MCT-LTDiag inferences of the main CNN "
        "(external_mct_ltdiag.csv vs. the comparison tables)",
        diff,
        n=len(p80),
        run="E8a, E8b",
    )
    # Section 4.6: slice count alone on MCT-LTDiag; Section 3.3: tumor inside the liver mask
    geo = read(runs, "E12", "E12_mct_crop_geometry.csv", dtype={"patient_id": str})
    geo = geo[geo.variant == "primary"]
    slices = geo["shape"].map(lambda v: json.loads(v)[2]).to_numpy()
    auc = roc_auc_score((mct.loc[geo.patient_id] == "HCC").to_numpy(), slices)
    add(
        "4.6",
        "MCT-LTDiag HCC-vs-ICC AUC of the slice count alone, max(AUC, 1 - AUC)",
        max(auc, 1 - auc),
        n=len(geo),
        post_hoc=True,
        run="E12",
    )
    g11 = read(runs, "E11", "E11_mct_crop_geometry.csv", dtype={"patient_id": str})
    share = g11[g11.variant == "union"].set_index("patient_id").tumor_share_inside_liver
    for c in ["HCC", "ICC"]:
        v = share[(mct.loc[share.index] == c).to_numpy()]
        add(
            "3.3",
            f"MCT-LTDiag {c}: tumor at least 90% inside the liver mask",
            int((v >= 0.9).sum()),
            n=len(v),
            run="E11",
        )
        add(
            "3.3",
            f"MCT-LTDiag {c}: median tumor share inside the liver mask",
            float(v.median()),
            n=len(v),
            run="E11",
        )
    # Section 4.7: non-contrast artifact repaired in every cHCC-CCA scan (post hoc)
    p10 = read(runs, "E10", "E10c_predictions.csv", dtype={"patient_id": str})
    rep = {}
    for name in ["CNN", "CNN + radiomics"]:
        base = p10[(p10.model == name) & (p10.condition == "control") & p10.patient_id.isin(held)]
        base = base.set_index("patient_id").loc[held]
        for cond in ["repair", "repair_smooth"]:
            alt = p10[(p10.model == name) & (p10.condition == cond)].set_index("patient_id")
            out = base.copy()
            ch = [i for i in held if labels[i] == "CHCC"]
            out.loc[ch, P3] = alt.loc[ch, P3].to_numpy()
            rep[(name, cond)] = out.reset_index()
        rep[(name, "control")] = base.reset_index()
        for cond in ["control", "repair", "repair_smooth"]:
            add(
                "4.7",
                f"held-out macro-AUC, {name}, cHCC-CCA scans {cond.replace('_', ' ')}",
                _macro(rep[(name, cond)], labels),
                n=len(held),
                post_hoc=True,
                run="E10",
            )
        t = rep[(name, "repair")]
        y = labels.loc[t.patient_id].to_numpy()
        for cond in ["control", "repair"]:
            called = int(((y == "CHCC") & (_calls(rep[(name, cond)]) == "CHCC")).sum())
            add(
                "4.7",
                f"held-out cHCC-CCA patients called cHCC-CCA, {name}, {cond}",
                called,
                n=int((y == "CHCC").sum()),
                post_hoc=True,
                run="E10",
            )
    y = labels.loc[rep[("CNN + radiomics", "control")].patient_id].to_numpy()
    pb = rep[("CNN + radiomics", "control")][P3].to_numpy()
    pr = rep[("CNN + radiomics", "repair")][P3].to_numpy()
    rng, diffs = np.random.default_rng(42), []
    while len(diffs) < 2000:
        idx = rng.integers(0, len(y), len(y))
        if len(set(y[idx])) < 3:
            continue
        yy = y[idx]
        diffs.append(
            np.mean([roc_auc_score(yy == c, pr[idx, j]) for j, c in enumerate(ORDER)])
            - np.mean([roc_auc_score(yy == c, pb[idx, j]) for j, c in enumerate(ORDER)])
        )
    d0 = _macro(rep[("CNN + radiomics", "repair")], labels) - _macro(
        rep[("CNN + radiomics", "control")], labels
    )
    add(
        "4.7",
        "held-out macro-AUC difference, CNN + radiomics, repaired - unchanged",
        d0,
        *np.percentile(diffs, [2.5, 97.5]),
        n=len(held),
        post_hoc=True,
        run="E10",
    )
    # Section 4.9 and Table 6: acquisition-matched tests
    p14 = read(runs, "E14a", "E14a_predictions.csv", dtype={"patient_id": str})
    ye, se = _hcc_icc(pick("MCT_LTDiag", REF_FUSION), mct)
    for cohort, ids in [("held-out", held), ("out-of-fold", dev)]:
        c0 = p14[
            (p14.model == "CNN + radiomics")
            & (p14.condition == "control")
            & p14.patient_id.isin(ids)
        ]
        c0 = c0.set_index("patient_id")
        c1 = p14[(p14.model == "CNN + radiomics") & (p14.condition == "mct")].set_index(
            "patient_id"
        )
        y0, s0 = _hcc_icc(c0.reset_index(), labels)
        _, s1 = _hcc_icc(c1.loc[c0.index].reset_index(), labels)
        a0, a1, ext = roc_auc_score(y0, s0), roc_auc_score(y0, s1), roc_auc_score(ye, se)
        rng, shares = np.random.default_rng(42), []
        while len(shares) < 2000:
            i = rng.integers(0, len(y0), len(y0))
            j = rng.integers(0, len(ye), len(ye))
            if len(set(y0[i])) < 2 or len(set(ye[j])) < 2:
                continue
            b0, b1 = roc_auc_score(y0[i], s0[i]), roc_auc_score(y0[i], s1[i])
            shares.append((b0 - b1) / (b0 - roc_auc_score(ye[j], se[j])))
        add(
            "4.9",
            f"share of the external loss reproduced, CNN + radiomics, {cohort} "
            "(bootstrap CI over both cohorts, post hoc)",
            (a0 - a1) / (a0 - ext),
            *np.percentile(shares, [2.5, 97.5]),
            n=len(y0),
            post_hoc=cohort == "out-of-fold",
            run="E14a, E8b",
        )
    internal = {
        "main pipeline": preds[
            preds.cohort.isin(["internal_test", "internal_oof"]) & (preds.model == REF_FUSION)
        ],
        "frozen models, MCT-LTDiag spacing": p14[
            (p14.model == "CNN + radiomics") & (p14.condition == "mct")
        ],
        "frozen models, blur-only control": p14[
            (p14.model == "CNN + radiomics") & (p14.condition == "mct_smooth")
        ],
        "retrained, slice density equalized": read(
            runs, "E12", "E12_predictions_internal.csv", dtype={"patient_id": str}
        ).query("model == 'CNN + radiomics' and condition == 'control'"),
        "retrained, MCT-LTDiag spacing": read(
            runs, "E14b", "E14b_predictions_internal.csv", dtype={"patient_id": str}
        ).query("model == 'CNN + radiomics' and condition == 'control'"),
    }
    for name, t in internal.items():
        assert t.patient_id.is_unique and set(t.patient_id) == set(labels.index), name
        for cohort, ids in [("held-out", held), ("out-of-fold", dev)]:
            y, s = _hcc_icc(t[t.patient_id.isin(ids)], labels)
            add(
                "4.9",
                f"internal HCC-vs-ICC AUC, CNN + radiomics, {name}, {cohort}",
                roc_auc_score(y, s),
                n=len(y),
                run="E8b, E12, E14a, E14b",
            )
        y = labels.loc[t.patient_id].to_numpy()
        add(
            "4.9",
            f"internal ICC patients called ICC (all 99), CNN + radiomics, {name}",
            int(((y == "ICC") & (_calls(t) == "ICC")).sum()),
            n=int((y == "ICC").sum()),
            run="E8b, E12, E14a, E14b",
        )
    # Sections 4.1 and 4.5: size baseline and crop retention
    trunc = read(runs, "E47", "E4a_truncation_per_patient_phase.csv", dtype={"patient_id": str})
    c2 = trunc[trunc.phase == "C2"]
    ret = c2.retention
    add(
        "4.5",
        "patients with every portal-venous tumor voxel inside the crop",
        int((ret >= 1 - 1e-12).sum()),
        n=len(c2),
        run="E47",
    )
    add("4.5", "median portal-venous retention", float(ret.median()), n=len(c2), run="E47")
    add(
        "4.5",
        "volume-weighted portal-venous retention",
        float(c2.crop_voxels.sum() / c2.full_voxels.sum()),
        n=len(c2),
        run="E47",
    )
    d = c2[c2.patient_id.isin(folds)].set_index("patient_id")
    x = np.log(d.full_voxels.astype(float) + 1).to_numpy()[:, None]
    yy = np.array([ORDER.index(labels[i]) for i in d.index])
    ff = np.array([folds[i] for i in d.index])
    aucs = []
    for k in range(5):
        m = LogisticRegression(class_weight="balanced", max_iter=2000, random_state=42)
        m.fit(x[ff != k], yy[ff != k])
        pp = m.predict_proba(x[ff == k])
        aucs.append(np.mean([roc_auc_score(yy[ff == k] == j, pp[:, j]) for j in range(3)]))
    add(
        "4.1",
        "lesion-size baseline (log tumor voxel count), cross-validation macro-AUC, mean",
        float(np.mean(aucs)),
        n=len(d),
        run="E47",
    )
    add(
        "4.1",
        "lesion-size baseline, cross-validation macro-AUC, SD over five folds",
        float(np.std(aucs, ddof=1)),
        n=len(d),
        run="E47",
    )
    # Supplementary Methods S2: imputed radiomic cells on HCC-TACE-Seg
    selected = json.loads((runs / RUNS["E1_E2"] / "E2_selected_features_noshape.json").read_text())
    feats = read(runs, "E5c", "E5c_radiomics_features_axis_fixed_E6rules.csv")
    feats = feats.drop(columns=feats.columns[0])
    total = imputed = 0
    for names in selected.values():
        present = [c for c in names if c in feats.columns]
        total += len(names) * len(feats)
        imputed += int(feats[present].isna().sum().sum()) + (len(names) - len(present)) * len(feats)
    add(
        "S2",
        "HCC-TACE-Seg selected-feature cells filled with training-fold medians",
        imputed,
        n=total,
        run="E5c, E1_E2",
    )
    if catalog is not None:
        rows += hcc_tace_seg_inputs(catalog)
    return pd.DataFrame(rows)


def hcc_tace_seg_inputs(catalog: Path) -> list[dict]:
    """Supplementary Methods S1: the study of each HCC-TACE-Seg model input, from the DICOM
    catalog of the collection and the input manifest of the submitted pipeline."""
    man = pd.read_csv(
        catalog / "external_manifest_for_week10_tumor_only_FILTERED_liver_adapter.csv", dtype=str
    )
    cat = pd.read_csv(
        catalog / "dicom_catalog.csv",
        usecols=["PatientID", "StudyInstanceUID", "SeriesInstanceUID", "Modality", "ContentDate"],
        dtype=str,
    )
    study = cat.groupby("SeriesInstanceUID").StudyInstanceUID.first()
    date = cat[cat.Modality == "CT"].groupby("StudyInstanceUID").ContentDate.min()
    seg = cat[cat.Modality == "SEG"].groupby("PatientID").StudyInstanceUID.agg(set)
    rows = []
    for phase, label in [("P", "non-contrast"), ("C1", "arterial"), ("C2", "portal-venous")]:
        later = total = 0
        for _, r in man.iterrows():
            path = r["ct_" + phase]
            if not isinstance(path, str) or "__" not in path:
                continue
            studies = cat[(cat.PatientID == r.patient_id) & (cat.Modality == "CT")].StudyInstanceUID
            first = min(studies.unique(), key=lambda s: date[s])
            assert seg.get(r.patient_id, set()) == {first}
            total += 1
            later += study[path.split("__")[1]] != first
        rows.append(
            {
                "section": "S1",
                "quantity": f"HCC-TACE-Seg {label} inputs from a later study than the segmentation",
                "value": later,
                "n": total,
                "post_hoc": True,
                "source_run": "DICOM catalog, input manifest",
            }
        )
    return rows


def size_by_inplane_extent(runs: Path, project: Path) -> pd.DataFrame:
    """Supplementary Table S11 (post hoc): macro-AUC by thirds of in-plane tumor extent."""
    anatomy = read(runs, "E10", "E10b_anatomy_per_scan.csv", dtype={"patient_id": str})
    size = anatomy[anatomy.phase == "C2"].set_index("patient_id")["tumour_inplane_px"].astype(float)
    cuts = np.quantile(size[size > 0], [1 / 3, 2 / 3])
    split = json.loads((project / "splits" / "train_val_test.json").read_text())
    labels = _labels(project).map({c: k for k, c in enumerate(ORDER)})
    preds = read(runs, "E8b", "E8b_E9_predictions.csv", dtype={"patient_id": str})
    rng, rows = np.random.default_rng(42), []
    for key, name in [(REF_FUSION, "CNN + radiomics"), ("CNN phase_dropout_CNN [complete]", "CNN")]:
        for cohort, ids in [
            ("internal_oof", [str(x) for x in split["dev_ids"]]),
            ("internal_test", [str(x) for x in split["test_ids"]]),
        ]:
            t = (
                preds[(preds.model == key) & (preds.cohort == cohort)]
                .set_index("patient_id")
                .loc[ids]
            )
            for third in ["small", "medium", "large"]:
                sub = [
                    p
                    for p in ids
                    if {0: "small", 1: "medium", 2: "large"}[int(np.searchsorted(cuts, size[p]))]
                    == third
                ]
                y, pp = labels.loc[sub].to_numpy(), t.loc[sub, P3].to_numpy()
                boot = []
                for _ in range(2000):
                    b = rng.integers(0, len(y), len(y))
                    if len(np.unique(y[b])) == 3:
                        boot.append(roc_auc_score(y[b], pp[b], multi_class="ovr", average="macro"))
                counts = np.bincount(y, minlength=3)
                rows.append(
                    {
                        "model": name,
                        "cohort": "out-of-fold" if cohort == "internal_oof" else "held-out",
                        "third": third,
                        "cut_offs_px": f"{cuts[0]:.1f} / {cuts[1]:.1f}",
                        "patients": len(sub),
                        "HCC/ICC/CHCC": "/".join(map(str, counts)),
                        "macro_auc": roc_auc_score(y, pp, multi_class="ovr", average="macro"),
                        "boot_low": np.percentile(boot, 2.5),
                        "boot_high": np.percentile(boot, 97.5),
                        "accuracy": float((pp.argmax(1) == y).mean()),
                        "post_hoc": True,
                    }
                )
    return pd.DataFrame(rows)


def adaptive_crop_internal(runs: Path) -> pd.DataFrame:
    """The adaptive-crop run reported the population SD of the five fold AUCs; the sample SD,
    used in every other table, is added as cv_sd_sample."""
    table = read(runs, "E4d", "E4d_internal_results.csv")
    return table.assign(cv_sd_sample=table["cv_sd"] * np.sqrt(5 / 4))


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        required=True,
        help="private liver_project folder (contains revision_2026-10, splits, radiomics)",
    )
    parser.add_argument("--mask-census-summary", type=Path, required=True)
    parser.add_argument("--mask-census-performance", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("results/revision_2026-10"))
    parser.add_argument(
        "--hcc-tace-seg-catalog",
        type=Path,
        default=None,
        help="folder with the HCC-TACE-Seg DICOM catalog and input manifest (optional)",
    )
    args = parser.parse_args()
    project = args.project_root
    runs = project / "revision_2026-10"
    out = args.output
    out.mkdir(parents=True, exist_ok=True)

    tables = {
        "internal_models.csv": internal_models(runs),
        "internal_comparisons.csv": internal_comparisons(runs),
        "internal_per_class.csv": internal_per_class(runs),
        "internal_repeated_cv_summary.csv": read(runs, "E7a", "E7a_summary.csv"),
        "internal_repeated_cv_per_fold.csv": read(runs, "E7a", "E7a_per_fold.csv"),
        "internal_missing_phase_patterns.csv": read(runs, "E3", "E3_all_cnns_by_pattern.csv"),
        "internal_fusion_missing_phase_patterns.csv": read(
            runs, "E3", "E3C_fusion_by_cnn_and_pattern.csv"
        ),
        "internal_optimism.csv": read(runs, "E47", "E7d_optimism.csv"),
        "crop_truncation_by_class_phase.csv": read(runs, "E47", "E4a_truncation_summary.csv"),
        "tumor_size_strata_out_of_fold.csv": read(
            runs, "E47", "E4b_internal_by_size_and_truncation.csv"
        ).query("split == 'oof_222'"),
        "adaptive_crop_internal.csv": adaptive_crop_internal(runs),
        "adaptive_crop_size_strata.csv": read(runs, "E4d", "E4d_internal_by_size_third.csv"),
        "adaptive_crop_external.csv": read(runs, "E4d", "E4d_mct203_results.csv"),
        "adaptive_crop_paired_differences.csv": read(runs, "E4d", "E4d_paired_differences.csv"),
        "acquisition_only_discrimination.csv": acquisition_only(runs, project),
        "dataset_audit_by_class.csv": dataset_audit(runs),
        "tumor_inside_liver_mask_by_class_phase.csv": pd.read_csv(args.mask_census_summary),
        "performance_by_tumor_inside_liver_mask.csv": pd.read_csv(args.mask_census_performance),
        "attention_enrichment_summary.csv": read(runs, "F2", "F2_attention_summary.csv"),
        "attention_phase_share_summary.csv": read(runs, "F2", "F2_phase_share_summary.csv"),
        "external_hcc_tace_seg.csv": hcc_tace_seg(runs),
    }
    effects, counts = counterfactual(runs, project)
    tables["counterfactual_effects.csv"] = effects
    tables["counterfactual_predicted_classes.csv"] = counts
    mct, calibration, mitigation, paired = external(runs)
    tables["external_mct_ltdiag.csv"] = mct
    tables["calibration.csv"] = calibration
    tables["external_mct_ltdiag_mitigation.csv"] = mitigation
    tables["external_mct_ltdiag_mitigation_comparisons.csv"] = paired
    tables["external_mct_ltdiag_by_sex.csv"] = mct_by_sex(runs, project)
    tables["manuscript_values.csv"] = manuscript_values(runs, project, args.hcc_tace_seg_catalog)
    tables["tumor_size_by_inplane_extent.csv"] = size_by_inplane_extent(runs, project)
    for name, source in [
        ("corrected_mask_crops_by_class.csv", "E11_crop_summary_by_class.csv"),
        ("corrected_mask_internal.csv", "E11_internal_results.csv"),
        ("corrected_mask_internal_paired.csv", "E11_internal_paired_differences.csv"),
        ("corrected_mask_by_tumor_inside_liver.csv", "E11_by_tumour_inside_liver.csv"),
        ("corrected_mask_counterfactual_effects.csv", "E11_counterfactual_effects.csv"),
        ("corrected_mask_external.csv", "E11_mct_results.csv"),
        ("corrected_mask_external_paired.csv", "E11_mct_paired.csv"),
    ]:
        tables[name] = read(runs, "E11", source)
    for name, source in [
        ("equalized_density_by_class.csv", "E12_equalization_by_class.csv"),
        ("equalized_density_slice_count_model.csv", "E12_slice_count_only_model.csv"),
        ("equalized_density_internal.csv", "E12_internal_results.csv"),
        ("equalized_density_internal_paired.csv", "E12_internal_paired_differences.csv"),
        ("equalized_density_residual_artifact.csv", "E12_residual_artifact_effects.csv"),
        ("equalized_density_external.csv", "E12_mct_results.csv"),
        ("equalized_density_external_paired.csv", "E12_mct_paired.csv"),
    ]:
        tables[name] = read(runs, "E12", source)
    tables["nested_stacking_per_repeat.csv"] = read(
        runs, "E13", "E13_combined_per_repeat.csv"
    ).drop(columns=["run"])
    tables["nested_stacking_summary.csv"] = read(runs, "E13", "E13_combined_summary.csv")
    for name, run, source in [
        ("acquisition_matched_frozen_hcc_vs_icc.csv", "E14a", "E14a_OA_hcc_vs_icc.csv"),
        ("acquisition_matched_frozen_macro_auc.csv", "E14a", "E14a_OA_macro_auc.csv"),
        ("acquisition_matched_frozen_predicted_classes.csv", "E14a", "E14a_predicted_classes.csv"),
        (
            "acquisition_matched_frozen_thick_noncontrast.csv",
            "E14a",
            "E14a_OC_thick_noncontrast.csv",
        ),
        (
            "acquisition_matched_frozen_density_by_class.csv",
            "E14a",
            "E14a_mct_like_density_by_class.csv",
        ),
        ("acquisition_matched_retrained_by_class.csv", "E14b", "E14b_equalization_by_class.csv"),
        (
            "acquisition_matched_retrained_slice_count_model.csv",
            "E14b",
            "E14b_slice_count_only_model.csv",
        ),
        ("acquisition_matched_retrained_internal.csv", "E14b", "E14b_internal_results.csv"),
        (
            "acquisition_matched_retrained_internal_paired.csv",
            "E14b",
            "E14b_internal_paired_differences.csv",
        ),
        (
            "acquisition_matched_retrained_residual_artifact.csv",
            "E14b",
            "E14b_residual_artifact_effects.csv",
        ),
        ("acquisition_matched_retrained_external.csv", "E14b", "E14b_mct_results.csv"),
        ("acquisition_matched_retrained_external_paired.csv", "E14b", "E14b_mct_paired.csv"),
        ("seed_variability_per_seed.csv", "E15", "E15_results_per_seed.csv"),
        ("seed_variability_spread.csv", "E15", "E15_seed_spread.csv"),
        ("seed_variability_training.csv", "E15", "E15_training_per_fold.csv"),
    ]:
        tables[name] = read(runs, run, source)
    forbidden = {"patient_id", "case_id", "subject_id"}
    for name, table in tables.items():
        if forbidden & set(table.columns):
            raise SystemExit(f"{name} would contain patient-level columns")
        table.to_csv(out / name, index=False, float_format="%.6g", lineterminator="\n")
    print(f"Wrote {len(tables)} aggregate tables to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
