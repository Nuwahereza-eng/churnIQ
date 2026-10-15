"""Shared Streamlit helpers: page setup, cached loaders and standard messages."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import METADATA_PATH, MODEL_PATH, RAW_DATA_PATH, RESULTS_PATH  # noqa: E402
from src.data_loader import DatasetError, check_quality, load_dataset, read_raw_csv  # noqa: E402
from src.predict import ChurnModel, ModelNotFoundError, load_model  # noqa: E402

APP_TITLE = "Telco Churn Insight"

PREDICTION_DISCLAIMER = (
    "Predictions are statistical estimates from a model trained on historical, "
    "fictional telecom data. A churn probability is not a guarantee that a "
    "customer will or will not leave. Use it as decision support alongside "
    "human judgement, never as the sole basis for action, and never to "
    "penalise a customer."
)

DATA_LIMITATIONS = [
    "The IBM Telco Customer Churn dataset describes a **fictional** telecom "
    "provider created by IBM for demonstrations. It does not represent any real "
    "company, nor Ugandan or other specific markets.",
    "It is a single snapshot (about 7,000 customers, one quarter); there is no "
    "time dimension, so seasonality and changing behaviour cannot be studied.",
    "Only service, account and basic demographic fields are available; factors "
    "such as network quality, competitor offers or customer-service interactions "
    "are absent.",
    "Associations found in the data are not causal effects.",
]

_CSS = """
<style>
div[data-testid="stMetricValue"] { font-size: 1.6rem; }
.small-note { color: #52514e; font-size: 0.88rem; }
.result-card { border: 1px solid rgba(11,11,11,0.10); border-radius: 8px;
               padding: 1rem 1.25rem; background: #fcfcfb; }
</style>
"""


def setup_page(title: str, icon: str = "📉") -> None:
    st.set_page_config(page_title=f"{title} · {APP_TITLE}", page_icon=icon, layout="wide")
    st.markdown(_CSS, unsafe_allow_html=True)
    st.title(title)


@st.cache_data(show_spinner="Loading dataset ...")
def get_dataset() -> pd.DataFrame:
    return load_dataset(RAW_DATA_PATH)


@st.cache_data(show_spinner=False)
def get_quality_report() -> dict:
    return check_quality(read_raw_csv(RAW_DATA_PATH)).to_dict()


@st.cache_data(show_spinner=False)
def get_results() -> dict | None:
    if not RESULTS_PATH.exists():
        return None
    return json.loads(RESULTS_PATH.read_text())


@st.cache_resource(show_spinner="Loading model ...")
def get_model() -> ChurnModel:
    return load_model(MODEL_PATH, METADATA_PATH)


def require_dataset() -> pd.DataFrame:
    """Return the dataset, or show setup instructions and stop the page."""
    try:
        return get_dataset()
    except DatasetError:
        st.error("The dataset is not available yet.")
        st.markdown(
            "Download the public IBM Telco Customer Churn CSV (about 1 MB) with the button below, "
            "or run `python scripts/download_data.py`, or follow the manual instructions in `data/README.md`."
        )
        if st.button("Download dataset", type="primary"):
            from src.data_acquisition import download_dataset

            try:
                with st.spinner("Downloading ..."):
                    download_dataset()
                get_dataset.clear()
                get_quality_report.clear()
                st.rerun()
            except OSError:
                st.error("The download failed. Check the internet connection or download the file manually.")
        st.stop()
    except Exception:  # noqa: BLE001 - never show a stack trace to users
        st.error("The dataset could not be read. Check that the CSV file is the unmodified IBM file.")
        st.stop()


def require_model() -> ChurnModel:
    try:
        return get_model()
    except ModelNotFoundError:
        st.error("No trained model is available yet.")
        st.markdown("Train it by running `python -m src.train` from the project folder, then reload this page.")
        st.stop()
    except Exception:  # noqa: BLE001
        st.error("The saved model could not be loaded. Retrain it with `python -m src.train`.")
        st.stop()


def require_results() -> dict:
    results = get_results()
    if results is None:
        st.error("No evaluation results found. Run `python -m src.train` to train and evaluate the models.")
        st.stop()
    return results


def disclaimer() -> None:
    st.info(PREDICTION_DISCLAIMER, icon="ℹ️")


def pct(x: float, nd: int = 1) -> str:
    return f"{x * 100:.{nd}f}%"
