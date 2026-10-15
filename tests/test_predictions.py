import json

import numpy as np
import pandas as pd
import pytest
from sklearn.model_selection import train_test_split

from src.config import METADATA_PATH, MODEL_PATH, RANDOM_STATE, RAW_DATA_PATH, RESULTS_PATH, TEST_SIZE
from src.data_loader import load_dataset, split_features_target
from src.predict import (
    PREDICTION_COLUMN,
    PROBABILITY_COLUMN,
    RISK_BAND_COLUMN,
    ModelNotFoundError,
    load_model,
    predict_one,
    predict_records,
)
from src.schema import FEATURE_COLUMNS
from src.validation import InputValidationError
from synthetic import make_feature_records


# ---------- Training (SYNTHETIC data, quick grids) ----------

def test_training_produces_three_models_and_metrics(trained_synthetic):
    report = trained_synthetic["outcome"]["report"]
    assert set(report["models"]) == {"Logistic Regression", "Decision Tree", "Random Forest"}
    for res in report["models"].values():
        m = res["test"]["metrics"]
        for key in ["accuracy", "precision", "recall", "f1", "roc_auc"]:
            assert 0.0 <= m[key] <= 1.0
        assert np.array(res["test"]["confusion_matrix"]).sum() == trained_synthetic["outcome"]["metadata"]["n_test"]
    assert report["metadata"]["selected_model"] in report["models"]
    assert 0 < report["deployed_model"]["decision_threshold"] < 1


def test_saved_files_are_valid(trained_synthetic):
    meta = json.loads(trained_synthetic["metadata_path"].read_text())
    assert meta["feature_columns"] == FEATURE_COLUMNS
    results = json.loads(trained_synthetic["results_path"].read_text())
    assert "permutation_importance" in results


def test_missing_model_raises(tmp_path):
    with pytest.raises(ModelNotFoundError):
        load_model(tmp_path / "missing.joblib", tmp_path / "missing.json")


# ---------- Prediction output ----------

def test_batch_prediction_format(trained_synthetic):
    model = trained_synthetic["model"]
    records = make_feature_records(20, seed=5)
    out, _ = predict_records(model, records)
    assert len(out) == 20
    # original columns, including the identifier, are preserved unchanged
    pd.testing.assert_frame_equal(out[records.columns], records.reset_index(drop=True))
    assert out[PROBABILITY_COLUMN].between(0, 1).all()
    assert set(out[PREDICTION_COLUMN]) <= {"Yes", "No"}
    assert set(out[RISK_BAND_COLUMN]) <= {"Low", "Medium", "High"}


def test_prediction_consistent_with_threshold(trained_synthetic):
    model = trained_synthetic["model"]
    out, _ = predict_records(model, make_feature_records(30, seed=6))
    expected = np.where(out[PROBABILITY_COLUMN] >= model.threshold, "Yes", "No")
    # probabilities are rounded for display; allow ties at the boundary
    near = (out[PROBABILITY_COLUMN] - model.threshold).abs() < 1e-3
    assert (out[PREDICTION_COLUMN].to_numpy()[~near] == expected[~near]).all()


def test_threshold_override(trained_synthetic):
    model = trained_synthetic["model"]
    records = make_feature_records(30, seed=7)
    low, _ = predict_records(model, records, threshold=0.01)
    high, _ = predict_records(model, records, threshold=0.99)
    assert (low[PREDICTION_COLUMN] == "Yes").sum() >= (high[PREDICTION_COLUMN] == "Yes").sum()
    with pytest.raises(ValueError):
        predict_records(model, records, threshold=1.5)


def test_predict_one(trained_synthetic):
    model = trained_synthetic["model"]
    record = make_feature_records(1, seed=8).iloc[0].to_dict()
    result = predict_one(model, record)
    assert 0 <= result["probability"] <= 1
    assert result["prediction"] in {"Yes", "No"}


def test_invalid_batch_rejected(trained_synthetic):
    model = trained_synthetic["model"]
    records = make_feature_records(5, seed=9)
    records.loc[2, "Contract"] = "Lifetime"
    with pytest.raises(InputValidationError) as exc:
        predict_records(model, records)
    assert any("row 4" in e for e in exc.value.errors)


def test_incompatible_file_rejected(trained_synthetic):
    model = trained_synthetic["model"]
    with pytest.raises(InputValidationError, match="Missing required column"):
        predict_records(model, pd.DataFrame({"a": [1, 2], "b": [3, 4]}))


def test_identifier_does_not_affect_prediction(trained_synthetic):
    model = trained_synthetic["model"]
    records = make_feature_records(10, seed=10)
    other = records.copy()
    other["customerID"] = "DIFFERENT"
    a, _ = predict_records(model, records)
    b, _ = predict_records(model, other)
    assert np.allclose(a[PROBABILITY_COLUMN], b[PROBABILITY_COLUMN])


def test_save_load_round_trip_is_identical(trained_synthetic):
    original = trained_synthetic["outcome"]["pipeline"]
    loaded = trained_synthetic["model"].pipeline
    X = make_feature_records(15, seed=11)
    from src.validation import validate_or_raise
    X = validate_or_raise(X)
    assert np.allclose(original.predict_proba(X), loaded.predict_proba(X))


# ---------- Reproducibility of the real, saved results ----------

@pytest.mark.skipif(
    not (RAW_DATA_PATH.exists() and MODEL_PATH.exists() and RESULTS_PATH.exists()),
    reason="real dataset or trained model not available",
)
def test_saved_test_metrics_reproduce_from_saved_model():
    """Rebuild the documented test split and check the stored metrics match."""
    model = load_model(MODEL_PATH, METADATA_PATH)
    X, y = split_features_target(load_dataset())
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )
    assert len(X_test) == model.metadata["n_test"]
    from sklearn.metrics import roc_auc_score
    proba = model.pipeline.predict_proba(X_test)[:, 1]
    assert roc_auc_score(y_test, proba) == pytest.approx(model.metadata["test_metrics"]["roc_auc"], abs=1e-4)
    preds = (proba >= model.threshold).astype(int)
    assert int(((preds == 1) & (y_test == 1)).sum()) == model.metadata["test_metrics"]["tp"]
