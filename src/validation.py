"""Validate customer records submitted for prediction (form or CSV upload).

Errors make a record unusable and block prediction. Warnings flag values that
are technically valid but unusual (for example outside the range seen during
training), so the user can judge how much to trust the estimate.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from src.data_loader import fill_total_charges
from src.schema import (
    BINARY_FEATURES,
    CATEGORICAL_FEATURES,
    FEATURE_COLUMNS,
    INTERNET_ADDONS,
    NUMERIC_FEATURES,
    NUMERIC_LIMITS,
)

MAX_BATCH_ROWS = 50_000
MAX_REPORTED_ISSUES = 50


class InputValidationError(ValueError):
    """Raised when records cannot be used for prediction."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors[:5]) + (" ..." if len(errors) > 5 else ""))


@dataclass
class ValidationResult:
    data: pd.DataFrame | None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _row_label(idx: int) -> str:
    # Row numbers as a user sees them in a spreadsheet: header is line 1.
    return f"row {idx + 2}"


def _cap(messages: list[str]) -> list[str]:
    if len(messages) > MAX_REPORTED_ISSUES:
        extra = len(messages) - MAX_REPORTED_ISSUES
        return messages[:MAX_REPORTED_ISSUES] + [f"... and {extra} more issue(s)."]
    return messages


def validate_records(
    df: pd.DataFrame, training_ranges: dict[str, tuple[float, float]] | None = None
) -> ValidationResult:
    """Check and type-convert records for prediction.

    Returns a ValidationResult whose ``data`` holds only the model feature
    columns, correctly typed, in the order the pipeline expects. Extra columns
    in ``df`` are ignored here (batch prediction keeps them in the output).
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(df, pd.DataFrame):
        return ValidationResult(None, ["Input must be a table of customer records."])
    if df.empty:
        return ValidationResult(None, ["The file contains no customer records."])
    if len(df) > MAX_BATCH_ROWS:
        return ValidationResult(
            None, [f"Too many rows ({len(df):,}). The maximum is {MAX_BATCH_ROWS:,}."]
        )

    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    dupe_cols = sorted({c for c in df.columns if list(df.columns).count(c) > 1})
    if dupe_cols:
        return ValidationResult(None, [f"Duplicate column names: {', '.join(dupe_cols)}."])

    missing = [c for c in FEATURE_COLUMNS if c not in df.columns]
    if missing:
        return ValidationResult(
            None,
            [
                "Missing required column(s): " + ", ".join(missing) + ". "
                "Download the template CSV to see the expected format."
            ],
        )

    df = df.reset_index(drop=True)
    out = pd.DataFrame(index=df.index)

    # Categorical columns: strip whitespace, require a known category.
    for col, allowed in CATEGORICAL_FEATURES.items():
        values = df[col].astype(object).where(df[col].notna(), None)
        values = values.map(lambda v: v.strip() if isinstance(v, str) else v)
        blank = values.isna() | values.eq("")
        for i in values.index[blank]:
            errors.append(f"{_row_label(i)}: '{col}' is empty.")
        bad = ~blank & ~values.isin(allowed)
        for i in values.index[bad]:
            errors.append(
                f"{_row_label(i)}: '{col}' has invalid value '{values[i]}'. "
                f"Allowed: {', '.join(allowed)}."
            )
        out[col] = values.astype(object)

    # SeniorCitizen: must be 0 or 1.
    for col in BINARY_FEATURES:
        num = pd.to_numeric(df[col], errors="coerce")
        bad = num.isna() | ~num.isin([0, 1])
        for i in num.index[bad]:
            errors.append(f"{_row_label(i)}: '{col}' must be 0 or 1 (got '{df[col][i]}').")
        out[col] = num.fillna(0).astype(int)

    # Numeric columns. TotalCharges blank + tenure 0 is valid (not yet billed).
    numeric = df[NUMERIC_FEATURES].copy()
    numeric["TotalCharges"] = numeric["TotalCharges"].astype(object)
    numeric = fill_total_charges(numeric)
    for col in NUMERIC_FEATURES:
        num = pd.to_numeric(numeric[col], errors="coerce").astype(float)
        lo, hi = NUMERIC_LIMITS[col]
        for i in num.index[num.isna()]:
            errors.append(f"{_row_label(i)}: '{col}' must be a number (got '{df[col][i]}').")
        for i in num.index[num.notna() & ~np.isfinite(num)]:
            errors.append(f"{_row_label(i)}: '{col}' must be a finite number.")
        out_of_bounds = num.notna() & np.isfinite(num) & ((num < lo) | (num > hi))
        for i in num.index[out_of_bounds]:
            errors.append(f"{_row_label(i)}: '{col}' must be between {lo:g} and {hi:g} (got {num[i]:g}).")
        out[col] = num

    tenure = out["tenure"]
    non_int = tenure.notna() & np.isfinite(tenure) & (tenure % 1 != 0)
    for i in tenure.index[non_int]:
        errors.append(f"{_row_label(i)}: 'tenure' must be a whole number of months.")

    if errors:
        return ValidationResult(None, _cap(errors), [])

    out["tenure"] = out["tenure"].astype(int)

    # ---- Consistency and range warnings (do not block prediction) ----
    no_internet = out["InternetService"].eq("No")
    for col in INTERNET_ADDONS:
        inconsistent = (no_internet & out[col].ne("No internet service")) | (
            ~no_internet & out[col].eq("No internet service")
        )
        for i in out.index[inconsistent]:
            warnings.append(
                f"{_row_label(i)}: '{col}'='{out[col][i]}' is inconsistent with "
                f"InternetService='{out['InternetService'][i]}'."
            )
    no_phone = out["PhoneService"].eq("No")
    inconsistent = (no_phone & out["MultipleLines"].ne("No phone service")) | (
        ~no_phone & out["MultipleLines"].eq("No phone service")
    )
    for i in out.index[inconsistent]:
        warnings.append(
            f"{_row_label(i)}: 'MultipleLines'='{out['MultipleLines'][i]}' is inconsistent "
            f"with PhoneService='{out['PhoneService'][i]}'."
        )

    if training_ranges:
        for col, (lo, hi) in training_ranges.items():
            if col not in out:
                continue
            outside = (out[col] < lo) | (out[col] > hi)
            for i in out.index[outside]:
                warnings.append(
                    f"{_row_label(i)}: '{col}'={out[col][i]:g} is outside the training range "
                    f"[{lo:g}, {hi:g}]; the estimate is less reliable."
                )

    return ValidationResult(out[FEATURE_COLUMNS], [], _cap(warnings))


def validate_or_raise(df: pd.DataFrame, training_ranges=None) -> pd.DataFrame:
    result = validate_records(df, training_ranges)
    if not result.ok:
        raise InputValidationError(result.errors)
    return result.data
