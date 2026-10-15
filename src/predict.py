"""Load the trained pipeline and generate churn predictions.

Predictions always come from the saved, fitted pipeline. If no model has been
trained yet, ModelNotFoundError is raised; no placeholder results are returned.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import joblib
import pandas as pd

from src.config import METADATA_PATH, MODEL_PATH
from src.schema import FEATURE_COLUMNS, NEGATIVE_LABEL, POSITIVE_LABEL
from src.validation import InputValidationError, validate_records

PROBABILITY_COLUMN = "churn_probability"
PREDICTION_COLUMN = "predicted_churn"
RISK_BAND_COLUMN = "risk_band"


class ModelNotFoundError(FileNotFoundError):
    """Raised when the trained model has not been created yet."""


@dataclass
class ChurnModel:
    pipeline: object
    metadata: dict

    @property
    def threshold(self) -> float:
        return float(self.metadata.get("decision_threshold", 0.5))

    @property
    def training_ranges(self) -> dict:
        return {k: tuple(v) for k, v in self.metadata.get("training_ranges", {}).items()}


def load_model(model_path: Path = MODEL_PATH, metadata_path: Path = METADATA_PATH) -> ChurnModel:
    if not Path(model_path).exists() or not Path(metadata_path).exists():
        raise ModelNotFoundError(
            "No trained model found. Train one with `python -m src.train`."
        )
    pipeline = joblib.load(model_path)
    metadata = json.loads(Path(metadata_path).read_text())
    if metadata.get("feature_columns") != FEATURE_COLUMNS:
        raise ModelNotFoundError(
            "The saved model was trained with a different feature schema. Retrain it."
        )
    return ChurnModel(pipeline, metadata)


def risk_band(probability: float) -> str:
    """Coarse, human-readable grouping of a calibrated churn probability."""
    if probability >= 0.6:
        return "High"
    if probability >= 0.3:
        return "Medium"
    return "Low"


def predict_proba(model: ChurnModel, features: pd.DataFrame) -> pd.Series:
    """Churn probabilities for already validated feature rows."""
    proba = model.pipeline.predict_proba(features[FEATURE_COLUMNS])[:, 1]
    return pd.Series(proba, index=features.index, name=PROBABILITY_COLUMN)


def predict_records(
    model: ChurnModel, records: pd.DataFrame, threshold: float | None = None
) -> tuple[pd.DataFrame, list[str]]:
    """Validate records and append prediction columns.

    Returns (original records + predictions, warnings). The original columns,
    including any identifiers, are preserved unchanged; identifiers are never
    passed to the model. Raises InputValidationError if any record is invalid.
    """
    threshold = model.threshold if threshold is None else float(threshold)
    if not 0.0 < threshold < 1.0:
        raise ValueError("Threshold must be between 0 and 1.")

    result = validate_records(records, model.training_ranges)
    if not result.ok:
        raise InputValidationError(result.errors)

    proba = predict_proba(model, result.data)
    out = records.reset_index(drop=True).copy()
    out[PROBABILITY_COLUMN] = proba.round(4).to_numpy()
    out[PREDICTION_COLUMN] = [POSITIVE_LABEL if p >= threshold else NEGATIVE_LABEL for p in proba]
    out[RISK_BAND_COLUMN] = [risk_band(p) for p in proba]
    return out, result.warnings


def predict_one(model: ChurnModel, record: dict, threshold: float | None = None) -> dict:
    """Predict for a single customer given as a dict of feature values."""
    out, warnings = predict_records(model, pd.DataFrame([record]), threshold)
    row = out.iloc[0]
    return {
        "probability": float(row[PROBABILITY_COLUMN]),
        "prediction": row[PREDICTION_COLUMN],
        "risk_band": row[RISK_BAND_COLUMN],
        "threshold": model.threshold if threshold is None else float(threshold),
        "warnings": warnings,
    }
