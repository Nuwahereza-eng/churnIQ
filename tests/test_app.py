"""Smoke tests that run each Streamlit page headlessly with the real data and model."""

import pytest

from src.config import MODEL_PATH, RAW_DATA_PATH, RESULTS_PATH, ROOT

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

pytestmark = pytest.mark.skipif(
    not (RAW_DATA_PATH.exists() and MODEL_PATH.exists() and RESULTS_PATH.exists()),
    reason="real dataset or trained model not available",
)

PAGES = [
    "app.py",
    "app_pages/0_Home.py",
    "app_pages/1_Data_Exploration.py",
    "app_pages/2_Predict_Churn.py",
    "app_pages/3_Batch_Prediction.py",
    "app_pages/4_Model_Performance.py",
    "app_pages/5_Insights.py",
]


@pytest.mark.parametrize("page", PAGES)
def test_page_renders_without_exceptions(page):
    at = AppTest.from_file(str(ROOT / page), default_timeout=120).run()
    assert not at.exception, at.exception
    assert not at.error, [e.value for e in at.error]


def test_single_prediction_end_to_end():
    at = AppTest.from_file(str(ROOT / "app_pages/2_Predict_Churn.py"), default_timeout=120).run()
    at.number_input[0].set_value(2)  # tenure
    at.button[0].click().run()
    assert not at.exception
    labels = [m.label for m in at.metric]
    assert "Estimated churn probability" in labels
    value = next(m.value for m in at.metric if m.label == "Estimated churn probability")
    assert value.endswith("%") and 0 <= float(value[:-1]) <= 100
