"""Train, compare and save churn prediction models.

Experimental design
-------------------
1. Stratified 80/20 train/test split with a fixed seed.
2. For each algorithm, hyperparameters are tuned with stratified 5-fold
   cross-validation on the training set only (scoring: ROC-AUC).
3. The final model is selected by mean cross-validated ROC-AUC, so the test
   set plays no part in model selection.
4. All tuned models are then evaluated once on the same held-out test set.
5. Class weighting inflates predicted probabilities, so the selected pipeline
   is wrapped in sigmoid (Platt) calibration fitted on the training set with
   internal cross-validation. The decision threshold for the deployed model is
   chosen to maximise F1 on out-of-fold training predictions.
6. The calibrated pipeline (preprocessing + classifier + calibration) is saved
   with its metadata and evaluated on the same test set.

Run:  python -m src.train
"""

from __future__ import annotations

import argparse
import json
import platform
import time
from datetime import datetime, timezone

import joblib
import numpy as np
import sklearn
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.dummy import DummyClassifier
from sklearn.metrics import brier_score_loss
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_predict, train_test_split
from sklearn.tree import DecisionTreeClassifier

from src.config import (
    CV_FOLDS,
    METADATA_PATH,
    MODEL_PATH,
    MODELS_DIR,
    RANDOM_STATE,
    RAW_DATA_PATH,
    REPORTS_DIR,
    RESULTS_PATH,
    TEST_SIZE,
)
from src.data_loader import check_quality, file_sha256, load_dataset, read_raw_csv, split_features_target
from src.evaluate import (
    best_f1_threshold,
    evaluate_probabilities,
    model_coefficients,
    permutation_feature_importance,
)
from src.preprocessing import build_pipeline
from src.schema import CATEGORICAL_FEATURES, FEATURE_COLUMNS, NUMERIC_FEATURES

SELECTION_METRIC = "roc_auc"


def model_specs(random_state: int = RANDOM_STATE) -> dict:
    """Candidate algorithms and their hyperparameter grids.

    class_weight="balanced" is used for every model: churners are ~27% of
    customers, and without weighting the models favour the majority class at
    the default 0.5 threshold, missing many churners. Weighting is preferred
    over resampling (e.g. SMOTE) because it creates no synthetic records and
    works cleanly inside cross-validation.
    """
    return {
        "Logistic Regression": {
            "estimator": LogisticRegression(
                class_weight="balanced", max_iter=5000, random_state=random_state
            ),
            "param_grid": {"model__C": [0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0]},
            "description": "Linear model of the log-odds of churn; interpretable baseline.",
        },
        "Decision Tree": {
            "estimator": DecisionTreeClassifier(class_weight="balanced", random_state=random_state),
            "param_grid": {
                "model__max_depth": [3, 4, 5, 6, 8, 10, None],
                "model__min_samples_leaf": [1, 10, 25, 50, 100, 150, 250],
            },
            "description": "Single tree of if/then splits; readable rules but high variance.",
        },
        "Random Forest": {
            "estimator": RandomForestClassifier(
                # n_jobs=1: the grid search already parallelises across folds
                n_estimators=300, class_weight="balanced", random_state=random_state, n_jobs=1
            ),
            "param_grid": {
                "model__max_depth": [6, 10, 14, None],
                "model__min_samples_leaf": [5, 10, 20, 40, 80],
                "model__max_features": ["sqrt", 0.5],
            },
            "description": "Ensemble of decorrelated trees; reduces the variance of a single tree.",
        },
    }


def _jsonable_params(params: dict) -> dict:
    return {k.replace("model__", ""): (v if v is None or isinstance(v, (int, float, str)) else str(v)) for k, v in params.items()}


def run_training(data_path=RAW_DATA_PATH, quick: bool = False, verbose: bool = True) -> dict:
    log = print if verbose else (lambda *a, **k: None)
    t0 = time.time()

    raw = read_raw_csv(data_path)
    quality = check_quality(raw)
    df = load_dataset(data_path)
    X, y = split_features_target(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )
    log(f"Train: {len(X_train)} rows ({y_train.mean():.1%} churn) | Test: {len(X_test)} rows ({y_test.mean():.1%} churn)")

    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    specs = model_specs()
    if quick:  # tiny grids for automated tests
        for spec in specs.values():
            spec["param_grid"] = {k: v[:1] for k, v in spec["param_grid"].items()}

    results: dict[str, dict] = {}
    fitted: dict[str, object] = {}
    for name, spec in specs.items():
        log(f"Tuning {name} ...", end=" ", flush=True)
        start = time.time()
        search = GridSearchCV(
            build_pipeline(spec["estimator"]),
            spec["param_grid"],
            scoring={"roc_auc": "roc_auc", "f1": "f1", "recall": "recall",
                     "precision": "precision", "average_precision": "average_precision"},
            refit=SELECTION_METRIC,
            cv=cv,
            n_jobs=-1,
        )
        search.fit(X_train, y_train)
        best = search.best_index_
        cvr = search.cv_results_
        cv_scores = {
            m: {"mean": round(float(cvr[f"mean_test_{m}"][best]), 4),
                "std": round(float(cvr[f"std_test_{m}"][best]), 4)}
            for m in ["roc_auc", "f1", "recall", "precision", "average_precision"]
        }
        pipe = search.best_estimator_
        proba_test = pipe.predict_proba(X_test)[:, 1]
        results[name] = {
            "description": spec["description"],
            "best_params": _jsonable_params(search.best_params_),
            "n_candidates": len(cvr["params"]),
            "cv": cv_scores,
            "test": evaluate_probabilities(y_test, proba_test, threshold=0.5),
            "fit_seconds": round(time.time() - start, 1),
        }
        fitted[name] = pipe
        log(f"CV ROC-AUC {cv_scores['roc_auc']['mean']:.4f} ± {cv_scores['roc_auc']['std']:.4f} | "
            f"test ROC-AUC {results[name]['test']['metrics']['roc_auc']:.4f} ({results[name]['fit_seconds']}s)")

    # Reference baseline: always predicts the majority class.
    dummy = build_pipeline(DummyClassifier(strategy="prior")).fit(X_train, y_train)
    baseline = evaluate_probabilities(y_test, dummy.predict_proba(X_test)[:, 1], threshold=0.5)["metrics"]

    selected = max(results, key=lambda n: results[n]["cv"][SELECTION_METRIC]["mean"])
    log(f"Selected model (highest CV {SELECTION_METRIC}): {selected}")

    # Calibrate the selected pipeline on the training set only.
    log("Calibrating selected model and choosing decision threshold ...")

    def calibrated():
        return CalibratedClassifierCV(clone(fitted[selected]), method="sigmoid", cv=cv)

    deployed = calibrated().fit(X_train, y_train)
    # Out-of-fold calibrated probabilities on the training set -> threshold.
    oof = cross_val_predict(calibrated(), X_train, y_train, cv=cv, method="predict_proba", n_jobs=-1)[:, 1]
    decision_threshold = best_f1_threshold(y_train.to_numpy(), oof)

    proba_uncal = fitted[selected].predict_proba(X_test)[:, 1]
    proba_cal = deployed.predict_proba(X_test)[:, 1]
    deployed_eval = evaluate_probabilities(y_test, proba_cal, threshold=decision_threshold)
    deployed_info = {
        "base_model": selected,
        "calibration": "sigmoid (Platt scaling), 5-fold internal CV on the training set",
        "decision_threshold": decision_threshold,
        "threshold_rule": "maximises F1 on out-of-fold calibrated predictions for the training set",
        "brier_uncalibrated": round(float(brier_score_loss(y_test, proba_uncal)), 4),
        "brier_calibrated": round(float(brier_score_loss(y_test, proba_cal)), 4),
        "mean_predicted_uncalibrated": round(float(proba_uncal.mean()), 4),
        "mean_predicted_calibrated": round(float(proba_cal.mean()), 4),
        "observed_churn_rate_test": round(float(y_test.mean()), 4),
        "test": deployed_eval,
    }
    log(f"Brier score {deployed_info['brier_uncalibrated']} -> {deployed_info['brier_calibrated']} "
        f"after calibration; decision threshold {decision_threshold}")

    log("Computing permutation importance on the test set ...")
    perm = permutation_feature_importance(deployed, X_test, y_test)
    coefs = {name: model_coefficients(p) for name, p in fitted.items()}

    training_ranges = {
        c: (float(X_train[c].min()), float(X_train[c].max())) for c in NUMERIC_FEATURES
    }
    metadata = {
        "selected_model": selected,
        "selection_metric": f"mean {CV_FOLDS}-fold CV {SELECTION_METRIC} on the training set",
        "best_params": results[selected]["best_params"],
        "calibration": deployed_info["calibration"],
        "decision_threshold": decision_threshold,
        "threshold_rule": deployed_info["threshold_rule"],
        "cv_scores": results[selected]["cv"],
        "test_metrics": deployed_eval["metrics"],
        "feature_columns": FEATURE_COLUMNS,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "training_ranges": training_ranges,
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "train_churn_rate": round(float(y_train.mean()), 4),
        "test_churn_rate": round(float(y_test.mean()), 4),
        "random_state": RANDOM_STATE,
        "test_size": TEST_SIZE,
        "cv_folds": CV_FOLDS,
        "dataset_file": str(data_path.name if hasattr(data_path, "name") else data_path),
        "dataset_sha256": file_sha256(data_path),
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "python_version": platform.python_version(),
        "sklearn_version": sklearn.__version__,
        "quick_mode": quick,
    }
    report = {
        "metadata": metadata,
        "data_quality": quality.to_dict(),
        "models": results,
        "deployed_model": deployed_info,
        "baseline_majority_class": baseline,
        "permutation_importance": perm,
        "model_importances": coefs,
        "runtime_seconds": round(time.time() - t0, 1),
    }
    return {"pipeline": deployed, "metadata": metadata, "report": report, "fitted": fitted}


def save_outputs(outcome: dict, model_path=MODEL_PATH, metadata_path=METADATA_PATH, results_path=RESULTS_PATH) -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(outcome["pipeline"], model_path, compress=3)
    metadata_path.write_text(json.dumps(outcome["metadata"], indent=2))
    results_path.write_text(json.dumps(outcome["report"], indent=2, default=_json_default))


def _json_default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    raise TypeError(f"Not JSON serialisable: {type(o)}")


def print_summary(report: dict) -> None:
    header = f"{'Model':<22}{'CV AUC':>8}{'Acc':>8}{'Prec':>8}{'Recall':>8}{'F1':>8}{'AUC':>8}{'AP':>8}"
    print("\nHeld-out test set results (threshold 0.5)")
    print(header)
    print("-" * len(header))
    for name, r in report["models"].items():
        m = r["test"]["metrics"]
        print(f"{name:<22}{r['cv']['roc_auc']['mean']:>8.4f}{m['accuracy']:>8.4f}{m['precision']:>8.4f}"
              f"{m['recall']:>8.4f}{m['f1']:>8.4f}{m['roc_auc']:>8.4f}{m['average_precision']:>8.4f}")
    b = report["baseline_majority_class"]
    print(f"{'Majority baseline':<22}{'':>8}{b['accuracy']:>8.4f}{b['precision']:>8.4f}{b['recall']:>8.4f}"
          f"{b['f1']:>8.4f}{b['roc_auc']:>8.4f}{b['average_precision']:>8.4f}")
    print(f"\nSelected: {report['metadata']['selected_model']}  ({report['metadata']['selection_metric']})")
    d = report["deployed_model"]
    m = d["test"]["metrics"]
    print(f"Deployed (calibrated, threshold {d['decision_threshold']}): acc {m['accuracy']:.4f}  "
          f"prec {m['precision']:.4f}  recall {m['recall']:.4f}  F1 {m['f1']:.4f}  "
          f"AUC {m['roc_auc']:.4f}  Brier {d['brier_uncalibrated']:.4f} -> {d['brier_calibrated']:.4f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train and evaluate churn models.")
    parser.add_argument("--quick", action="store_true", help="use minimal grids (for smoke tests)")
    args = parser.parse_args()
    outcome = run_training(quick=args.quick)
    save_outputs(outcome)
    print_summary(outcome["report"])
    print(f"\nSaved pipeline -> {MODEL_PATH.relative_to(MODELS_DIR.parent)}")
    print(f"Saved metadata -> {METADATA_PATH.relative_to(MODELS_DIR.parent)}")
    print(f"Saved results  -> {RESULTS_PATH.relative_to(REPORTS_DIR.parent)}")


if __name__ == "__main__":
    main()
