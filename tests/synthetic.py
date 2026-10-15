"""SYNTHETIC test data generator.

Records produced here are randomly generated for automated tests only. They are
not real customers and must never be presented as observations from the IBM
dataset.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.schema import CATEGORICAL_FEATURES, INTERNET_ADDONS, RAW_COLUMNS


def make_synthetic_raw(n: int = 400, seed: int = 0) -> pd.DataFrame:
    """Raw-format (string-valued) synthetic records that follow the dataset schema."""
    rng = np.random.default_rng(seed)
    pick = lambda col: rng.choice(CATEGORICAL_FEATURES[col], size=n)  # noqa: E731

    df = pd.DataFrame({"customerID": [f"SYN-{i:05d}" for i in range(n)]})
    for col in ["gender", "Partner", "Dependents", "PhoneService", "InternetService",
                "Contract", "PaperlessBilling", "PaymentMethod"]:
        df[col] = pick(col)
    df["SeniorCitizen"] = rng.integers(0, 2, size=n)
    df["MultipleLines"] = np.where(df["PhoneService"] == "No", "No phone service",
                                   rng.choice(["No", "Yes"], size=n))
    for col in INTERNET_ADDONS:
        df[col] = np.where(df["InternetService"] == "No", "No internet service",
                           rng.choice(["No", "Yes"], size=n))
    df["tenure"] = rng.integers(0, 73, size=n)
    df["MonthlyCharges"] = rng.uniform(18, 119, size=n).round(2)
    df["TotalCharges"] = (df["tenure"] * df["MonthlyCharges"]).round(2)

    # Churn depends on contract and tenure so the models have signal to learn.
    logit = -1.0 + 1.6 * (df["Contract"] == "Month-to-month") - 0.04 * df["tenure"] \
        + 0.6 * (df["InternetService"] == "Fiber optic")
    p = 1 / (1 + np.exp(-logit))
    df["Churn"] = np.where(rng.uniform(size=n) < p, "Yes", "No")

    df = df[RAW_COLUMNS].astype(str)
    # Mirror the real data quirk: blank TotalCharges for brand-new customers.
    df.loc[df["tenure"] == "0", "TotalCharges"] = " "
    return df


def make_feature_records(n: int = 5, seed: int = 1) -> pd.DataFrame:
    """Synthetic records in the format expected for prediction (no Churn column)."""
    return make_synthetic_raw(n, seed).drop(columns=["Churn"])
