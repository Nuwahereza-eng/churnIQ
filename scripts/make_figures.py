"""Create static evaluation figures for the written report from saved results.

Reads reports/evaluation_results.json (written by `python -m src.train`) and
saves PNGs to reports/figures/. No model is retrained and no values are typed in.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from src.config import FIGURES_DIR, RESULTS_PATH  # noqa: E402

COLORS = {"Logistic Regression": "#2a78d6", "Decision Tree": "#eb6834", "Random Forest": "#1baf7a"}
INK2, MUTED, GRID = "#52514e", "#898781", "#e1e0d9"
plt.rcParams.update({
    "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#c3c2b7",
    "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True, "axes.titlesize": 12,
})


def save(fig, name):
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES_DIR / name, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"saved reports/figures/{name}")


def main() -> None:
    if not RESULTS_PATH.exists():
        sys.exit("No results found. Run `python -m src.train` first.")
    r = json.loads(RESULTS_PATH.read_text())
    models, dep = r["models"], r["deployed_model"]
    base_rate = dep["observed_churn_rate_test"]

    # ROC + PR
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5))
    for name, res in models.items():
        roc, pr = res["test"]["roc_curve"], res["test"]["pr_curve"]
        a1.plot(roc["x"], roc["y"], color=COLORS[name], lw=2,
                label=f"{name} (AUC {res['test']['metrics']['roc_auc']:.3f})")
        a2.plot(pr["x"], pr["y"], color=COLORS[name], lw=2,
                label=f"{name} (AP {res['test']['metrics']['average_precision']:.3f})")
    a1.plot([0, 1], [0, 1], ls="--", color=MUTED, lw=1)
    a1.set(xlabel="False positive rate", ylabel="True positive rate (recall)", title="ROC curves (test set)")
    a2.axhline(base_rate, ls="--", color=MUTED, lw=1)
    a2.set(xlabel="Recall", ylabel="Precision", title="Precision–recall curves (test set)", ylim=(0, 1.02))
    a1.legend(frameon=False, loc="lower right"); a2.legend(frameon=False, loc="upper right")
    save(fig, "06_roc_pr_curves.png")

    # Metric comparison
    keys = [("accuracy", "Accuracy"), ("precision", "Precision"), ("recall", "Recall"), ("f1", "F1"), ("roc_auc", "ROC-AUC")]
    fig, ax = plt.subplots(figsize=(10, 4.5))
    w = 0.26
    x = np.arange(len(keys))
    for i, (name, res) in enumerate(models.items()):
        vals = [res["test"]["metrics"][k] for k, _ in keys]
        bars = ax.bar(x + (i - 1) * w, vals, w * 0.92, color=COLORS[name], label=name)
        ax.bar_label(bars, fmt="%.3f", fontsize=7, color=INK2, padding=2)
    ax.set_xticks(x, [label for _, label in keys]); ax.set_ylim(0, 1.05)
    ax.set_ylabel("Score (test set, threshold 0.5)"); ax.set_title("Algorithm comparison")
    ax.legend(frameon=False, ncol=3, loc="upper left"); ax.grid(axis="x", visible=False)
    save(fig, "07_metric_comparison.png")

    # Confusion matrices (3 models + deployed)
    panels = [(n, m["test"]["confusion_matrix"], 0.5) for n, m in models.items()]
    panels.append((f"Deployed: calibrated {dep['base_model']}", dep["test"]["confusion_matrix"], dep["decision_threshold"]))
    fig, axes = plt.subplots(1, 4, figsize=(17, 4))
    for ax, (title, cm, thr) in zip(axes, panels):
        cm = np.array(cm)
        ax.imshow(cm, cmap="Blues", vmin=0, vmax=cm.max() * 1.15)
        for i in range(2):
            for j in range(2):
                ax.text(j, i, f"{cm[i, j]:,}\n({cm[i, j] / cm.sum():.0%})", ha="center", va="center",
                        color="white" if cm[i, j] > cm.max() * 0.6 else "#0b0b0b")
        ax.set_xticks([0, 1], ["No churn", "Churn"]); ax.set_yticks([0, 1], ["No churn", "Churn"])
        ax.set_xlabel("Predicted"); ax.set_ylabel("Actual"); ax.grid(False)
        ax.set_title(f"{title}\n(threshold {thr:.2f})", fontsize=10)
    fig.tight_layout()
    save(fig, "08_confusion_matrices.png")

    # Threshold + calibration for deployed model
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.8))
    tt = [row for row in dep["test"]["threshold_table"] if row["tp"] + row["fp"] > 0]
    th = [t["threshold"] for t in tt]
    for key, label, color in [("precision", "Precision", "#2a78d6"), ("recall", "Recall", "#eb6834"), ("f1", "F1", "#1baf7a")]:
        a1.plot(th, [t[key] for t in tt], lw=2, color=color, label=label)
    a1.axvline(dep["decision_threshold"], ls="--", color="#0b0b0b", lw=1)
    a1.set(xlabel="Decision threshold", ylabel="Score", title="Deployed model: effect of threshold (test set)",
           xlim=(0, 1), ylim=(0, 1.02))
    a1.legend(frameon=False)
    sel = models[dep["base_model"]]["test"]["calibration_curve"]
    cal = dep["test"]["calibration_curve"]
    a2.plot([0, 1], [0, 1], ls="--", color=MUTED, lw=1)
    a2.plot(sel["mean_predicted"], sel["fraction_positive"], "o-", color="#eb6834", lw=2,
            label=f"{dep['base_model']} uncalibrated (Brier {dep['brier_uncalibrated']:.3f})")
    a2.plot(cal["mean_predicted"], cal["fraction_positive"], "o-", color="#2a78d6", lw=2,
            label=f"Calibrated (Brier {dep['brier_calibrated']:.3f})")
    a2.set(xlabel="Mean predicted probability", ylabel="Observed churn rate",
           title="Calibration (test set)", xlim=(0, 1), ylim=(0, 1))
    a2.legend(frameon=False, loc="upper left")
    save(fig, "09_threshold_calibration.png")

    # Permutation importance
    perm = r["permutation_importance"]
    fig, ax = plt.subplots(figsize=(7, 6))
    names = [p["feature"] for p in perm][::-1]
    ax.barh(names, [p["mean"] for p in perm][::-1], xerr=[p["std"] for p in perm][::-1],
            color="#2a78d6", height=0.6, error_kw={"ecolor": MUTED, "lw": 1})
    ax.set_xlabel("Mean drop in ROC-AUC when the column is shuffled (10 repeats)")
    ax.set_title(f"Permutation importance: deployed {dep['base_model']} (test set)")
    ax.grid(axis="y", visible=False)
    save(fig, "10_permutation_importance.png")


if __name__ == "__main__":
    main()
