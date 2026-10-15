"""Reusable exploratory-analysis helpers (used by the notebook and the app)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, mannwhitneyu

from src.schema import CATEGORICAL_FEATURES, NUMERIC_FEATURES, POSITIVE_LABEL, TARGET_COLUMN

TENURE_BINS = [-1, 6, 12, 24, 48, 72]
TENURE_LABELS = ["0-6", "7-12", "13-24", "25-48", "49-72"]


def churn_flag(df: pd.DataFrame) -> pd.Series:
    return (df[TARGET_COLUMN] == POSITIVE_LABEL).astype(int)


def column_summary(df: pd.DataFrame, descriptions: dict | None = None) -> pd.DataFrame:
    rows = []
    for col in df.columns:
        s = df[col]
        rows.append(
            {
                "column": col,
                "type": "numeric" if pd.api.types.is_numeric_dtype(s) else "categorical",
                "missing": int(s.isna().sum()),
                "unique": int(s.nunique()),
                "example values": ", ".join(map(str, s.dropna().unique()[:3])),
                "description": (descriptions or {}).get(col, ""),
            }
        )
    return pd.DataFrame(rows)


def churn_rate_by(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Customers and churn rate for each value of ``col``."""
    g = df.assign(_churn=churn_flag(df)).groupby(col, observed=True)["_churn"]
    out = pd.DataFrame({"customers": g.size(), "churned": g.sum(), "churn_rate": g.mean()})
    out = out.reset_index().rename(columns={col: "group"})
    out.insert(0, "feature", col)
    return out


def add_tenure_band(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # ordered categorical so groups sort by tenure, not alphabetically
    df["tenure_band"] = pd.cut(df["tenure"], TENURE_BINS, labels=TENURE_LABELS)
    return df


def cramers_v(x: pd.Series, y: pd.Series) -> float:
    """Bias-corrected Cramér's V: strength of association between two categoricals (0-1)."""
    table = pd.crosstab(x, y)
    if table.shape[0] < 2 or table.shape[1] < 2:
        return 0.0
    chi2 = chi2_contingency(table, correction=False)[0]
    n = table.to_numpy().sum()
    phi2 = chi2 / n
    r, k = table.shape
    phi2corr = max(0.0, phi2 - (k - 1) * (r - 1) / (n - 1))
    rcorr = r - (r - 1) ** 2 / (n - 1)
    kcorr = k - (k - 1) ** 2 / (n - 1)
    denom = min(kcorr - 1, rcorr - 1)
    return float(np.sqrt(phi2corr / denom)) if denom > 0 else 0.0


def association_with_churn(df: pd.DataFrame) -> pd.DataFrame:
    """Association of every feature with churn.

    Categorical features: Cramér's V and chi-square p-value.
    Numeric features: point-biserial correlation and Mann-Whitney U p-value.
    These are bivariate associations only; they do not control for other
    variables and do not imply causation.
    """
    y = churn_flag(df)
    rows = []
    for col in list(CATEGORICAL_FEATURES) + ["SeniorCitizen"]:
        table = pd.crosstab(df[col], y)
        p = chi2_contingency(table)[1]
        rows.append({"feature": col, "type": "categorical", "measure": "Cramér's V",
                     "strength": cramers_v(df[col], y), "p_value": p})
    for col in NUMERIC_FEATURES:
        x = df[col].astype(float)
        mask = x.notna()
        r = float(np.corrcoef(x[mask], y[mask])[0, 1])
        p = mannwhitneyu(x[mask & (y == 1)], x[mask & (y == 0)]).pvalue
        rows.append({"feature": col, "type": "numeric", "measure": "point-biserial r",
                     "strength": r, "p_value": float(p)})
    out = pd.DataFrame(rows)
    out["abs_strength"] = out["strength"].abs()
    return out.sort_values("abs_strength", ascending=False).drop(columns="abs_strength").reset_index(drop=True)


def numeric_summary_by_churn(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(TARGET_COLUMN)[NUMERIC_FEATURES].describe().T.round(2)


def highest_churn_groups(df: pd.DataFrame, min_customers: int = 200, top: int = 8) -> pd.DataFrame:
    """Groups (single feature values) with the highest churn rates."""
    df = add_tenure_band(df)
    cols = list(CATEGORICAL_FEATURES) + ["SeniorCitizen", "tenure_band"]
    table = pd.concat([churn_rate_by(df, c) for c in cols], ignore_index=True)
    table = table[table["customers"] >= min_customers]
    return table.sort_values("churn_rate", ascending=False).head(top).reset_index(drop=True)
