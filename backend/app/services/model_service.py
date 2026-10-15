"""Model inference, wrapping the existing ``src.predict`` module.

The fitted pipeline is loaded once and reused. Validation and prediction use
the same code as the Streamlit app and the tests, so results are identical.
"""

from __future__ import annotations

import io
import threading

import pandas as pd

from src.predict import (
    PREDICTION_COLUMN,
    PROBABILITY_COLUMN,
    RISK_BAND_COLUMN,
    ChurnModel,
    ModelNotFoundError,
    load_model,
    predict_one,
    predict_records,
)
from src.schema import BINARY_FEATURES, CATEGORICAL_FEATURES, FEATURE_COLUMNS, FEATURE_DESCRIPTIONS, NUMERIC_LIMITS
from src.validation import InputValidationError, validate_records

from ..core.config import Settings
from ..core.errors import APIError, ServiceUnavailable

PREVIEW_ROWS = 10


class ModelService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._lock = threading.Lock()
        self._model: ChurnModel | None = None

    @property
    def available(self) -> bool:
        return self.settings.model_path.exists() and self.settings.metadata_path.exists()

    @property
    def model(self) -> ChurnModel:
        if self._model is None:
            with self._lock:
                if self._model is None:
                    try:
                        self._model = load_model(self.settings.model_path, self.settings.metadata_path)
                    except ModelNotFoundError as exc:
                        raise ServiceUnavailable(
                            "The trained model is not available. Train it with `python -m src.train`."
                        ) from exc
        return self._model

    @property
    def model_name(self) -> str:
        return f"Calibrated {self.model.metadata['selected_model']}"

    # ---------- schema ----------

    def schema(self) -> dict:
        meta = self.model.metadata
        ranges = meta.get("training_ranges", {})
        features = []
        for name in FEATURE_COLUMNS:
            spec: dict = {"name": name, "description": FEATURE_DESCRIPTIONS[name]}
            if name in CATEGORICAL_FEATURES:
                spec.update(type="categorical", allowed_values=CATEGORICAL_FEATURES[name])
            elif name in BINARY_FEATURES:
                spec.update(type="binary", allowed_values=[0, 1])
            else:
                lo, hi = NUMERIC_LIMITS[name]
                spec.update(type="numeric", min=lo, max=hi)
                if name in ranges:
                    spec.update(training_min=ranges[name][0], training_max=ranges[name][1])
            features.append(spec)
        return {
            "model_name": self.model_name,
            "decision_threshold": self.model.threshold,
            "features": features,
            "max_upload_bytes": self.settings.max_upload_bytes,
            "max_batch_rows": self.settings.max_batch_rows,
        }

    def template_csv(self) -> str:
        return ",".join(["customerID"] + FEATURE_COLUMNS) + "\n"

    # ---------- single prediction ----------

    def predict(self, record: dict, threshold: float | None) -> dict:
        if record.get("TotalCharges") is None:
            record = {**record, "TotalCharges": ""}  # blank is valid only for tenure 0
        try:
            result = predict_one(self.model, record, threshold)
        except InputValidationError as exc:
            raise APIError(422, "invalid_customer", "The customer details are invalid.",
                           [e.replace("row 2: ", "") for e in exc.errors]) from exc
        return {
            "churn_probability": result["probability"],
            "predicted_churn": result["prediction"] == "Yes",
            "predicted_label": result["prediction"],
            "risk_band": result["risk_band"],
            "threshold": result["threshold"],
            "warnings": [w.replace("row 2: ", "") for w in result["warnings"]],
            "model_name": self.model_name,
        }

    # ---------- batch ----------

    def read_csv(self, filename: str, content: bytes) -> pd.DataFrame:
        if not filename.lower().endswith(".csv"):
            raise APIError(415, "unsupported_file", "Only .csv files are accepted.")
        if not content.strip():
            raise APIError(422, "empty_file", "The uploaded file is empty.")
        if len(content) > self.settings.max_upload_bytes:
            mb = self.settings.max_upload_bytes / (1024 * 1024)
            raise APIError(413, "file_too_large", f"The file is larger than {mb:g} MB.")
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise APIError(422, "malformed_file", "The file is not UTF-8 text. Save it as a UTF-8 CSV.") from exc
        try:
            df = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
        except (pd.errors.ParserError, pd.errors.EmptyDataError, ValueError) as exc:
            raise APIError(422, "malformed_file",
                           "The file could not be parsed as CSV. Check it is comma-separated with one header row.") from exc
        if df.empty:
            raise APIError(422, "empty_file", "The file has a header row but no customer records.")
        if len(df) > self.settings.max_batch_rows:
            raise APIError(413, "too_many_rows",
                           f"The file has {len(df):,} rows; the maximum is {self.settings.max_batch_rows:,}.")
        df.columns = [str(c).strip() for c in df.columns]
        return df

    def validate_batch(self, filename: str, content: bytes) -> dict:
        df = self.read_csv(filename, content)
        result = validate_records(df, self.model.training_ranges)
        return {
            "filename": filename,
            "n_rows": int(len(df)),
            "columns": list(df.columns),
            "preview": df.head(PREVIEW_ROWS).to_dict(orient="records"),
            "valid": result.ok,
            "errors": result.errors,
            "warnings": result.warnings,
            "extra_columns": [c for c in df.columns if c not in FEATURE_COLUMNS],
        }

    def predict_batch(self, filename: str, content: bytes, threshold: float | None) -> dict:
        df = self.read_csv(filename, content)
        try:
            out, warnings = predict_records(self.model, df, threshold)
        except InputValidationError as exc:
            raise APIError(422, "invalid_records", "The file was rejected; no predictions were made.",
                           exc.errors) from exc
        used = self.model.threshold if threshold is None else threshold
        return {
            "filename": filename,
            "n_records": int(len(out)),
            "n_predicted_churn": int((out[PREDICTION_COLUMN] == "Yes").sum()),
            "mean_probability": round(float(out[PROBABILITY_COLUMN].mean()), 4),
            "threshold": used,
            "columns": list(out.columns),
            "rows": out.to_dict(orient="records"),
            "warnings": warnings,
            "model_name": self.model_name,
        }


__all__ = ["ModelService", "PROBABILITY_COLUMN", "RISK_BAND_COLUMN"]
