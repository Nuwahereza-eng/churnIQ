"""Read the saved experiment results (reports/evaluation_results.json).

These are the metrics produced by ``python -m src.train``; the API only
reshapes them for the frontend and never computes or invents values here.
"""

from __future__ import annotations

import json
import threading

from ..core.config import Settings
from ..core.errors import ServiceUnavailable

REPORT_LABELS = [("No churn", "No churn"), ("Churn", "Churn"), ("macro avg", "Macro average"),
                 ("weighted avg", "Weighted average")]


def _curve(c: dict) -> list[dict]:
    th = c.get("threshold") or [None] * len(c["x"])
    return [{"x": x, "y": y, "threshold": t} for x, y, t in zip(c["x"], c["y"], th)]


def _evaluation(ev: dict) -> dict:
    report = ev["classification_report"]
    return {
        "metrics": ev["metrics"],
        "confusion_matrix": ev["confusion_matrix"],
        "classification_report": [
            {"label": label, "precision": report[key]["precision"], "recall": report[key]["recall"],
             "f1": report[key]["f1-score"], "support": int(report[key]["support"])}
            for key, label in REPORT_LABELS if key in report
        ],
        "roc_curve": _curve(ev["roc_curve"]),
        "pr_curve": _curve(ev["pr_curve"]),
        "calibration_curve": [
            {"mean_predicted": m, "fraction_positive": f}
            for m, f in zip(ev["calibration_curve"]["mean_predicted"], ev["calibration_curve"]["fraction_positive"])
        ],
        "threshold_table": ev["threshold_table"],
    }


class ResultsService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._lock = threading.Lock()
        self._raw: dict | None = None

    @property
    def available(self) -> bool:
        return self.settings.results_path.exists()

    @property
    def raw(self) -> dict:
        if self._raw is None:
            with self._lock:
                if self._raw is None:
                    if not self.available:
                        raise ServiceUnavailable(
                            "Evaluation results are not available. Train the models with `python -m src.train`."
                        )
                    self._raw = json.loads(self.settings.results_path.read_text())
        return self._raw

    def model_metrics(self) -> dict:
        r = self.raw
        meta = r["metadata"]
        dep = r["deployed_model"]
        return {
            "selected_model": meta["selected_model"],
            "methodology": {
                "n_train": meta["n_train"], "n_test": meta["n_test"], "test_size": meta["test_size"],
                "cv_folds": meta["cv_folds"], "random_state": meta["random_state"],
                "train_churn_rate": meta["train_churn_rate"], "test_churn_rate": meta["test_churn_rate"],
                "selection_metric": meta["selection_metric"], "trained_at": meta["trained_at"],
                "sklearn_version": meta["sklearn_version"],
            },
            "models": [
                {"name": name, "description": m["description"], "best_params": m["best_params"],
                 "n_candidates": m["n_candidates"], "cv": m["cv"], "test": _evaluation(m["test"])}
                for name, m in r["models"].items()
            ],
            "baseline": r["baseline_majority_class"],
            "deployed": {**{k: v for k, v in dep.items() if k != "test"}, "test": _evaluation(dep["test"])},
        }

    def importance(self) -> dict:
        r = self.raw
        lr = r.get("model_importances", {}).get("Logistic Regression")
        return {
            "permutation_importance": r.get("permutation_importance"),
            "importance_model": f"Calibrated {r['metadata']['selected_model']} (deployed)",
            "logistic_coefficients": lr,
        }
