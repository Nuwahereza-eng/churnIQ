"""Request/response schemas for predictions.

The customer schema is generated from ``src/schema.py`` so the API accepts
exactly the features (and category values) the trained pipeline expects.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, create_model, model_validator

from src.schema import CATEGORICAL_FEATURES, FEATURE_COLUMNS, FEATURE_DESCRIPTIONS, NUMERIC_LIMITS

_fields: dict = {}
for _name, _allowed in CATEGORICAL_FEATURES.items():
    _fields[_name] = (Literal[tuple(_allowed)], Field(description=FEATURE_DESCRIPTIONS[_name]))
_fields["SeniorCitizen"] = (Literal[0, 1], Field(description=FEATURE_DESCRIPTIONS["SeniorCitizen"]))
_fields["tenure"] = (int, Field(ge=NUMERIC_LIMITS["tenure"][0], le=NUMERIC_LIMITS["tenure"][1],
                                description=FEATURE_DESCRIPTIONS["tenure"]))
_fields["MonthlyCharges"] = (float, Field(ge=NUMERIC_LIMITS["MonthlyCharges"][0], le=NUMERIC_LIMITS["MonthlyCharges"][1],
                                          allow_inf_nan=False, description=FEATURE_DESCRIPTIONS["MonthlyCharges"]))
_fields["TotalCharges"] = (Optional[float], Field(default=None, ge=NUMERIC_LIMITS["TotalCharges"][0],
                                                  le=NUMERIC_LIMITS["TotalCharges"][1], allow_inf_nan=False,
                                                  description=FEATURE_DESCRIPTIONS["TotalCharges"]
                                                  + " May be omitted only when tenure is 0."))


class _CustomerBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def _total_charges_required_unless_new(self):
        if self.TotalCharges is None and self.tenure != 0:
            raise ValueError("TotalCharges is required unless tenure is 0")
        return self


CustomerFeatures = create_model("CustomerFeatures", __base__=_CustomerBase, **_fields)
assert set(CustomerFeatures.model_fields) == set(FEATURE_COLUMNS)


class PredictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    customer: CustomerFeatures  # type: ignore[valid-type]
    threshold: Optional[float] = Field(default=None, gt=0, lt=1,
                                       description="Decision threshold; defaults to the model's threshold.")


class PredictionResult(BaseModel):
    churn_probability: float = Field(description="Calibrated estimated probability of churn (0-1).")
    predicted_churn: bool
    predicted_label: Literal["Yes", "No"]
    risk_band: Literal["Low", "Medium", "High"]
    threshold: float
    warnings: list[str]
    model_name: str


class BatchValidation(BaseModel):
    filename: str
    n_rows: int
    columns: list[str]
    preview: list[dict[str, str]]
    valid: bool
    errors: list[str]
    warnings: list[str]
    extra_columns: list[str]


class BatchPredictionResponse(BaseModel):
    filename: str
    n_records: int
    n_predicted_churn: int
    mean_probability: float
    threshold: float
    columns: list[str]
    rows: list[dict[str, str | float]]
    warnings: list[str]
    model_name: str
