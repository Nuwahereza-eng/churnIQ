"""scikit-learn preprocessing for the churn model.

All learned steps (imputation statistics, scaling parameters, one-hot
categories) are fitted inside the Pipeline, so cross-validation and the final
fit only ever learn from training folds and leakage is avoided.
"""

from __future__ import annotations

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

from src.schema import BINARY_FEATURES, CATEGORICAL_FEATURES, FEATURE_COLUMNS, NUMERIC_FEATURES

CATEGORICAL_COLUMNS = list(CATEGORICAL_FEATURES)


def coerce_feature_types(X: pd.DataFrame) -> pd.DataFrame:
    """Select the model columns in a fixed order and enforce dtypes.

    This runs as the first pipeline step, so the saved pipeline applies the
    same column selection at training and prediction time.
    """
    missing = [c for c in FEATURE_COLUMNS if c not in X.columns]
    if missing:
        raise ValueError(f"Missing feature columns: {missing}")
    X = X[FEATURE_COLUMNS].copy()
    for col in NUMERIC_FEATURES + BINARY_FEATURES:
        X[col] = pd.to_numeric(X[col], errors="coerce").astype(float)
    for col in CATEGORICAL_COLUMNS:
        X[col] = X[col].astype(object).where(X[col].notna(), None)
    return X


def build_preprocessor() -> ColumnTransformer:
    """Imputation + scaling for numeric columns, imputation + one-hot for categoricals.

    - Numeric: median imputation (robust to the skewed TotalCharges
      distribution), then standardisation, which Logistic Regression needs and
      tree models are unaffected by.
    - SeniorCitizen: already 0/1, so only imputed (most frequent).
    - Categorical: most-frequent imputation and one-hot encoding.
      ``handle_unknown="ignore"`` encodes an unseen category as all zeros
      instead of failing.
    """
    numeric = Pipeline(
        [("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]
    )
    binary = SimpleImputer(strategy="most_frequent")
    categorical = Pipeline(
        [
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        [
            ("num", numeric, NUMERIC_FEATURES),
            ("bin", binary, BINARY_FEATURES),
            ("cat", categorical, CATEGORICAL_COLUMNS),
        ],
        verbose_feature_names_out=True,
    )


def build_pipeline(classifier) -> Pipeline:
    return Pipeline(
        [
            ("coerce", FunctionTransformer(coerce_feature_types)),
            ("preprocess", build_preprocessor()),
            ("model", classifier),
        ]
    )


def transformed_feature_names(pipeline: Pipeline) -> list[str]:
    return list(pipeline.named_steps["preprocess"].get_feature_names_out())
