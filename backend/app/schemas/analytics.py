"""Response schemas for dataset, insight and model-evaluation endpoints."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel


class Health(BaseModel):
    status: Literal["ok", "degraded"]
    dataset_available: bool
    model_available: bool
    results_available: bool
    model_name: Optional[str] = None


# ---------- Shared building blocks ----------

class GroupRate(BaseModel):
    group: str
    customers: int
    churned: int
    churn_rate: float


class HistogramBin(BaseModel):
    start: float
    end: float
    stayed: int
    churned: int
    stayed_share: float
    churned_share: float


class NumericSummary(BaseModel):
    churn: Literal["Yes", "No"]
    count: int
    mean: float
    median: float
    q1: float
    q3: float
    min: float
    max: float


class QualityCheck(BaseModel):
    check: str
    result: str


# ---------- Overview ----------

class Overview(BaseModel):
    total_customers: int
    churned: int
    stayed: int
    churn_rate: float
    churn_by_contract: list[GroupRate]
    churn_by_tenure: list[GroupRate]
    monthly_charges_summary: list[NumericSummary]
    monthly_charges_histogram: list[HistogramBin]
    dataset_summary: dict[str, str | int | float]
    quality_checks: list[QualityCheck]


# ---------- Customer explorer ----------

class CustomerRow(BaseModel):
    customerID: str
    tenure: int
    Contract: str
    InternetService: str
    PaymentMethod: str
    TechSupport: str
    MonthlyCharges: float
    TotalCharges: float
    Churn: str


class CustomerPage(BaseModel):
    items: list[CustomerRow]
    total: int
    page: int
    page_size: int
    total_pages: int


# ---------- Insights ----------

class Association(BaseModel):
    feature: str
    measure: str
    strength: float
    p_value: float


class Importance(BaseModel):
    feature: str
    mean: float
    std: float


class Coefficient(BaseModel):
    feature: str
    value: float
    kind: str


class Insights(BaseModel):
    overall_churn_rate: float
    churn_by_contract: list[GroupRate]
    churn_by_tenure: list[GroupRate]
    churn_by_internet_service: list[GroupRate]
    churn_by_payment_method: list[GroupRate]
    churn_by_monthly_charge_band: list[GroupRate]
    monthly_charges_summary: list[NumericSummary]
    associations: list[Association]
    permutation_importance: Optional[list[Importance]] = None
    importance_model: Optional[str] = None
    logistic_coefficients: Optional[list[Coefficient]] = None


# ---------- Model metrics ----------

class Metrics(BaseModel):
    threshold: float
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: Optional[float] = None
    average_precision: Optional[float] = None
    brier_score: Optional[float] = None
    tp: int
    fp: int
    fn: int
    tn: int
    predicted_positive_rate: float


class CurvePoint(BaseModel):
    x: float
    y: float
    threshold: Optional[float] = None


class CalibrationPoint(BaseModel):
    mean_predicted: float
    fraction_positive: float


class ClassReportRow(BaseModel):
    label: str
    precision: float
    recall: float
    f1: float
    support: int


class Evaluation(BaseModel):
    metrics: Metrics
    confusion_matrix: list[list[int]]
    classification_report: list[ClassReportRow]
    roc_curve: list[CurvePoint]
    pr_curve: list[CurvePoint]
    calibration_curve: list[CalibrationPoint]
    threshold_table: list[Metrics]


class CVScore(BaseModel):
    mean: float
    std: float


class ModelResult(BaseModel):
    name: str
    description: str
    best_params: dict[str, str | int | float | None]
    n_candidates: int
    cv: dict[str, CVScore]
    test: Evaluation


class DeployedModel(BaseModel):
    base_model: str
    calibration: str
    decision_threshold: float
    threshold_rule: str
    brier_uncalibrated: float
    brier_calibrated: float
    mean_predicted_uncalibrated: float
    mean_predicted_calibrated: float
    observed_churn_rate_test: float
    test: Evaluation


class Methodology(BaseModel):
    n_train: int
    n_test: int
    test_size: float
    cv_folds: int
    random_state: int
    train_churn_rate: float
    test_churn_rate: float
    selection_metric: str
    trained_at: str
    sklearn_version: str


class ModelMetricsResponse(BaseModel):
    selected_model: str
    methodology: Methodology
    models: list[ModelResult]
    baseline: Metrics
    deployed: DeployedModel


class FeatureSpec(BaseModel):
    name: str
    type: Literal["categorical", "binary", "numeric"]
    description: str
    allowed_values: Optional[list[str | int]] = None
    min: Optional[float] = None
    max: Optional[float] = None
    training_min: Optional[float] = None
    training_max: Optional[float] = None


class ModelSchema(BaseModel):
    model_name: str
    decision_threshold: float
    features: list[FeatureSpec]
    max_upload_bytes: int
    max_batch_rows: int
