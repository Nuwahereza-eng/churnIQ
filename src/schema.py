"""Feature schema for the IBM Telco Customer Churn dataset.

This is the single source of truth for which columns the model uses, their
types and their allowed values. Training, validation, the prediction form and
batch prediction all read from here so the schema cannot drift between them.
"""

from __future__ import annotations

ID_COLUMN = "customerID"
TARGET_COLUMN = "Churn"
POSITIVE_LABEL = "Yes"
NEGATIVE_LABEL = "No"
TARGET_VALUES = (NEGATIVE_LABEL, POSITIVE_LABEL)

NUMERIC_FEATURES = ["tenure", "MonthlyCharges", "TotalCharges"]
BINARY_FEATURES = ["SeniorCitizen"]  # stored as 0/1 in the source data

_YES_NO = ["No", "Yes"]
_INTERNET_ADDON = ["No", "No internet service", "Yes"]

CATEGORICAL_FEATURES: dict[str, list[str]] = {
    "gender": ["Female", "Male"],
    "Partner": _YES_NO,
    "Dependents": _YES_NO,
    "PhoneService": _YES_NO,
    "MultipleLines": ["No", "No phone service", "Yes"],
    "InternetService": ["DSL", "Fiber optic", "No"],
    "OnlineSecurity": _INTERNET_ADDON,
    "OnlineBackup": _INTERNET_ADDON,
    "DeviceProtection": _INTERNET_ADDON,
    "TechSupport": _INTERNET_ADDON,
    "StreamingTV": _INTERNET_ADDON,
    "StreamingMovies": _INTERNET_ADDON,
    "Contract": ["Month-to-month", "One year", "Two year"],
    "PaperlessBilling": _YES_NO,
    "PaymentMethod": [
        "Bank transfer (automatic)",
        "Credit card (automatic)",
        "Electronic check",
        "Mailed check",
    ],
}

INTERNET_ADDONS = [
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
]

FEATURE_COLUMNS: list[str] = (
    ["gender"]
    + BINARY_FEATURES
    + ["Partner", "Dependents", "tenure", "PhoneService", "MultipleLines", "InternetService"]
    + INTERNET_ADDONS
    + ["Contract", "PaperlessBilling", "PaymentMethod", "MonthlyCharges", "TotalCharges"]
)

RAW_COLUMNS: list[str] = [ID_COLUMN] + FEATURE_COLUMNS + [TARGET_COLUMN]

# Hard limits used by input validation. Values outside the range observed in
# the training data are allowed but produce a warning (see validation.py).
NUMERIC_LIMITS = {
    "tenure": (0, 1200),
    "MonthlyCharges": (0.0, 10_000.0),
    "TotalCharges": (0.0, 1_000_000.0),
}

FEATURE_DESCRIPTIONS = {
    "customerID": "Unique customer identifier (excluded from modelling).",
    "gender": "Customer gender (Female/Male).",
    "SeniorCitizen": "1 if the customer is 65 or older, otherwise 0.",
    "Partner": "Whether the customer has a partner.",
    "Dependents": "Whether the customer has dependents.",
    "tenure": "Number of months the customer has stayed with the company.",
    "PhoneService": "Whether the customer has phone service.",
    "MultipleLines": "Whether the customer has multiple phone lines.",
    "InternetService": "Internet service type (DSL, Fiber optic, or none).",
    "OnlineSecurity": "Whether the customer has the online security add-on.",
    "OnlineBackup": "Whether the customer has the online backup add-on.",
    "DeviceProtection": "Whether the customer has the device protection add-on.",
    "TechSupport": "Whether the customer has the technical support add-on.",
    "StreamingTV": "Whether the customer streams TV.",
    "StreamingMovies": "Whether the customer streams movies.",
    "Contract": "Contract term (Month-to-month, One year, Two year).",
    "PaperlessBilling": "Whether the customer uses paperless billing.",
    "PaymentMethod": "Payment method.",
    "MonthlyCharges": "Amount charged to the customer monthly.",
    "TotalCharges": "Total amount charged to the customer to date.",
    "Churn": "Target: whether the customer left within the last month.",
}
