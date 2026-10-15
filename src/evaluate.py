"""Evaluation metrics, curves and interpretation for fitted churn pipelines.

Everything here is computed from real model outputs; nothing is hard-coded.
Results are returned as plain JSON-serialisable dicts so the Streamlit app can
display them without re-running the experiments.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

from src.preprocessing import transformed_feature_names

THRESHOLD_GRID = [round(t, 2) for t in np.arange(0.05, 0.96, 0.05)]


def _r(x: float, nd: int = 4) -> float:
    return float(round(float(x), nd))


def threshold_metrics(y_true, proba, threshold: float = 0.5) -> dict:
    """Classification metrics after converting probabilities with ``threshold``."""
    y_true = np.asarray(y_true)
    y_pred = (np.asarray(proba) >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return {
        "threshold": _r(threshold, 3),
        "accuracy": _r(accuracy_score(y_true, y_pred)),
        "precision": _r(precision_score(y_true, y_pred, zero_division=0)),
        "recall": _r(recall_score(y_true, y_pred, zero_division=0)),
        "f1": _r(f1_score(y_true, y_pred, zero_division=0)),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "predicted_positive_rate": _r(y_pred.mean()),
    }


def _downsample_curve(xs, ys, thresholds=None, max_points: int = 200) -> dict:
    """Keep curves small enough to store in JSON while preserving their shape."""
    xs, ys = np.asarray(xs), np.asarray(ys)
    idx = np.unique(np.linspace(0, len(xs) - 1, min(len(xs), max_points)).astype(int))
    out = {"x": [_r(v) for v in xs[idx]], "y": [_r(v) for v in ys[idx]]}
    if thresholds is not None:
        th = np.asarray(thresholds, dtype=float)
        th = np.where(np.isfinite(th), th, 1.0)
        out["threshold"] = [_r(v) for v in th[np.minimum(idx, len(th) - 1)]]
    return out


def evaluate_probabilities(y_true, proba, threshold: float = 0.5) -> dict:
    """Full evaluation of predicted churn probabilities on one dataset."""
    y_true = np.asarray(y_true)
    proba = np.asarray(proba)
    y_pred = (proba >= threshold).astype(int)

    fpr, tpr, roc_th = roc_curve(y_true, proba)
    prec, rec, pr_th = precision_recall_curve(y_true, proba)
    frac_pos, mean_pred = calibration_curve(y_true, proba, n_bins=10, strategy="quantile")

    return {
        "metrics": {
            **threshold_metrics(y_true, proba, threshold),
            "roc_auc": _r(roc_auc_score(y_true, proba)),
            "average_precision": _r(average_precision_score(y_true, proba)),
            "brier_score": _r(brier_score_loss(y_true, proba)),
        },
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=[0, 1]).tolist(),
        "classification_report": classification_report(
            y_true, y_pred, labels=[0, 1], target_names=["No churn", "Churn"],
            output_dict=True, zero_division=0,
        ),
        "roc_curve": _downsample_curve(fpr, tpr, roc_th),
        # precision_recall_curve returns recall decreasing; plot recall on x
        "pr_curve": _downsample_curve(rec, prec, np.append(pr_th, 1.0)),
        "calibration_curve": {
            "mean_predicted": [_r(v) for v in mean_pred],
            "fraction_positive": [_r(v) for v in frac_pos],
        },
        "threshold_table": [threshold_metrics(y_true, proba, t) for t in THRESHOLD_GRID],
        "positive_rate": _r(y_true.mean()),
    }


def best_f1_threshold(y_true, proba) -> float:
    """Threshold that maximises F1. Use only on training/out-of-fold predictions."""
    scores = [(f1_score(y_true, (proba >= t).astype(int), zero_division=0), t) for t in np.arange(0.05, 0.951, 0.01)]
    return float(round(max(scores)[1], 2))


def model_coefficients(pipeline, top_n: int = 20) -> list[dict] | None:
    """Model-specific importance on the one-hot encoded features.

    Logistic Regression: standardised coefficients (log-odds per unit /
    per standard deviation). Trees: impurity-based importances.
    """
    model = pipeline.named_steps["model"]
    names = transformed_feature_names(pipeline)
    if hasattr(model, "coef_"):
        values = model.coef_.ravel()
        kind = "coefficient"
    elif hasattr(model, "feature_importances_"):
        values = model.feature_importances_
        kind = "impurity_importance"
    else:
        return None
    order = np.argsort(-np.abs(values))[:top_n]
    return [
        {"feature": _clean_name(names[i]), "value": _r(values[i]), "kind": kind}
        for i in order
    ]


def _clean_name(name: str) -> str:
    for prefix in ("num__", "bin__", "cat__"):
        if name.startswith(prefix):
            name = name[len(prefix):]
    return name


def permutation_feature_importance(
    pipeline, X: pd.DataFrame, y, n_repeats: int = 10, random_state: int = 42
) -> list[dict]:
    """Permutation importance on the original (pre-encoding) columns.

    Measures how much ROC-AUC drops when one column's values are shuffled,
    breaking its relationship with the target. Reflects what the model relies
    on, not what causes churn.
    """
    result = permutation_importance(
        pipeline, X, y, scoring="roc_auc", n_repeats=n_repeats,
        random_state=random_state, n_jobs=-1,
    )
    rows = [
        {"feature": col, "mean": _r(m), "std": _r(s)}
        for col, m, s in zip(X.columns, result.importances_mean, result.importances_std)
    ]
    return sorted(rows, key=lambda r: -r["mean"])
