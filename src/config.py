"""Project-wide paths and constants."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DATASET_URL = (
    "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/"
    "master/data/Telco-Customer-Churn.csv"
)
DATASET_PAGE = (
    "https://github.com/IBM/telco-customer-churn-on-icp4d/blob/master/data/"
    "Telco-Customer-Churn.csv"
)

DATA_DIR = ROOT / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "Telco-Customer-Churn.csv"

MODELS_DIR = ROOT / "models"
MODEL_PATH = MODELS_DIR / "churn_pipeline.joblib"
METADATA_PATH = MODELS_DIR / "model_metadata.json"

REPORTS_DIR = ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
RESULTS_PATH = REPORTS_DIR / "evaluation_results.json"

RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_FOLDS = 5
