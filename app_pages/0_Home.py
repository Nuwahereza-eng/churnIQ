"""Home / overview page."""

import streamlit as st

from src.config import DATASET_PAGE
from ui.common import (
    DATA_LIMITATIONS,
    PREDICTION_DISCLAIMER,
    get_results,
    pct,
    require_dataset,
    setup_page,
)

setup_page("Telco Churn Insight", "📉")

st.markdown(
    "Decision-support dashboard for the research project **Development and Evaluation of a "
    "Machine Learning Model for Predicting Customer Churn in the Telecommunications Industry**. "
    "It presents customer churn patterns and estimates the probability that a customer will leave, "
    "using models trained on the public IBM Telco Customer Churn dataset."
)

df = require_dataset()
results = get_results()

st.subheader("Dataset")
c1, c2, c3, c4 = st.columns(4)
churn_rate = (df["Churn"] == "Yes").mean()
c1.metric("Customers", f"{len(df):,}")
c2.metric("Features used by the model", "19")
c3.metric("Churned customers", f"{(df['Churn'] == 'Yes').sum():,}")
c4.metric("Overall churn rate", pct(churn_rate))
st.caption(f"Source: IBM Telco Customer Churn sample dataset ([GitHub]({DATASET_PAGE})).")

st.subheader("Deployed model")
if results is None:
    st.warning("No trained model yet. Run `python -m src.train` to train and evaluate the models.")
else:
    meta = results["metadata"]
    dep = results["deployed_model"]
    m = dep["test"]["metrics"]
    st.markdown(
        f"**{meta['selected_model']}** with probability calibration, chosen by "
        f"{meta['selection_metric']}. Decision threshold: **{meta['decision_threshold']:.2f}** "
        f"(churn predicted when the estimated probability is at or above this value). "
        f"Trained {meta['trained_at'][:10]} on {meta['n_train']:,} customers; "
        f"evaluated on {meta['n_test']:,} held-out customers."
    )
    cols = st.columns(5)
    cols[0].metric("ROC-AUC", f"{m['roc_auc']:.3f}")
    cols[1].metric("Recall (churners found)", pct(m["recall"]))
    cols[2].metric("Precision (flags correct)", pct(m["precision"]))
    cols[3].metric("F1-score", f"{m['f1']:.3f}")
    cols[4].metric("Accuracy", pct(m["accuracy"]))
    st.caption(
        "Measured on the held-out test set, which was not used for training, tuning, model "
        "selection or threshold choice. These values are loaded from "
        "`reports/evaluation_results.json`, written by the training script."
    )

st.subheader("What you can do here")
st.markdown(
    """
- **Data Exploration**: dataset structure, quality checks and churn rates across customer groups.
- **Predict Churn**: estimate the churn probability for one customer.
- **Batch Prediction**: upload a CSV of customers and download their predictions.
- **Model Performance**: compare Logistic Regression, Decision Tree and Random Forest.
- **Insights**: what the data and the model suggest, and what they cannot tell you.
"""
)

st.subheader("Limitations of the data")
for item in DATA_LIMITATIONS:
    st.markdown(f"- {item}")

st.subheader("Responsible use")
st.markdown(PREDICTION_DISCLAIMER)
