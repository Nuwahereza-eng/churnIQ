"""Load and clean the raw churn dataset.

Data acquisition (scripts/download_data.py) is deliberately separate from this
module: anything here works on a local CSV, so a different but schema-compatible
dataset can be dropped in without touching the training code.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import RAW_DATA_PATH
from src.schema import (
    BINARY_FEATURES,
    CATEGORICAL_FEATURES,
    FEATURE_COLUMNS,
    ID_COLUMN,
    NUMERIC_FEATURES,
    POSITIVE_LABEL,
    RAW_COLUMNS,
    TARGET_COLUMN,
    TARGET_VALUES,
)


class DatasetError(ValueError):
    """Raised when the dataset is missing or does not match the expected schema."""


@dataclass
class DataQualityReport:
    n_rows: int
    n_columns: int
    missing_columns: list[str]
    unexpected_columns: list[str]
    missing_values: dict[str, int]
    blank_total_charges: int
    blank_total_charges_with_zero_tenure: int
    duplicate_rows: int
    duplicate_ids: int
    duplicate_feature_rows: int
    unexpected_target_values: list[str]
    unexpected_categories: dict[str, list[str]] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        return not (
            self.missing_columns
            or self.unexpected_target_values
            or self.unexpected_categories
            or self.duplicate_ids
        )

    def to_dict(self) -> dict:
        d = self.__dict__.copy()
        d["is_valid"] = self.is_valid
        return d


def read_raw_csv(path: str | Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Read the CSV exactly as stored (all values as strings except where unambiguous)."""
    path = Path(path)
    if not path.exists():
        raise DatasetError(
            f"Dataset not found at '{path}'. Run `python scripts/download_data.py` "
            "or follow the manual download instructions in data/README.md."
        )
    # keep_default_na=False so blank TotalCharges stay visible as "" / " " for checks
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def _is_blank(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().eq("")


def check_quality(raw: pd.DataFrame) -> DataQualityReport:
    """Inspect a raw (string-typed) dataframe without modifying it."""
    missing_cols = [c for c in RAW_COLUMNS if c not in raw.columns]
    unexpected_cols = [c for c in raw.columns if c not in RAW_COLUMNS]

    missing_values = {
        c: int(_is_blank(raw[c]).sum()) for c in raw.columns if _is_blank(raw[c]).any()
    }

    blank_tc = zero_tenure_blank_tc = 0
    if "TotalCharges" in raw.columns:
        blank_mask = _is_blank(raw["TotalCharges"])
        blank_tc = int(blank_mask.sum())
        if "tenure" in raw.columns:
            tenure = pd.to_numeric(raw["tenure"], errors="coerce")
            zero_tenure_blank_tc = int((blank_mask & tenure.eq(0)).sum())

    unexpected_target: list[str] = []
    if TARGET_COLUMN in raw.columns:
        unexpected_target = sorted(set(raw[TARGET_COLUMN].unique()) - set(TARGET_VALUES))

    unexpected_cats: dict[str, list[str]] = {}
    for col, allowed in CATEGORICAL_FEATURES.items():
        if col in raw.columns:
            bad = sorted(set(raw[col].unique()) - set(allowed))
            if bad:
                unexpected_cats[col] = bad

    feature_cols = [c for c in FEATURE_COLUMNS if c in raw.columns]
    return DataQualityReport(
        n_rows=len(raw),
        n_columns=raw.shape[1],
        missing_columns=missing_cols,
        unexpected_columns=unexpected_cols,
        missing_values=missing_values,
        blank_total_charges=blank_tc,
        blank_total_charges_with_zero_tenure=zero_tenure_blank_tc,
        duplicate_rows=int(raw.duplicated().sum()),
        duplicate_ids=int(raw[ID_COLUMN].duplicated().sum()) if ID_COLUMN in raw.columns else 0,
        duplicate_feature_rows=int(raw[feature_cols + [TARGET_COLUMN]].duplicated().sum())
        if TARGET_COLUMN in raw.columns
        else 0,
        unexpected_target_values=unexpected_target,
        unexpected_categories=unexpected_cats,
    )


def fill_total_charges(df: pd.DataFrame) -> pd.DataFrame:
    """Convert TotalCharges to numeric.

    Blank TotalCharges occur only for customers with tenure 0 who have not yet
    been billed, so the correct value is 0. Any other non-numeric value is left
    as NaN and handled by the pipeline's imputer (fitted on training data only).
    """
    df = df.copy()
    tc = pd.to_numeric(df["TotalCharges"].astype(str).str.strip().replace("", np.nan), errors="coerce")
    if "tenure" in df.columns:
        tenure = pd.to_numeric(df["tenure"], errors="coerce")
        tc = tc.mask(tc.isna() & tenure.eq(0), 0.0)
    df["TotalCharges"] = tc.astype(float)
    return df


def clean_dataset(raw: pd.DataFrame) -> pd.DataFrame:
    """Return a typed copy of the raw data ready for modelling.

    Does not drop rows: duplicate feature rows belong to different customer IDs
    and are genuine observations.
    """
    report = check_quality(raw)
    if report.missing_columns:
        raise DatasetError(f"Dataset is missing required columns: {report.missing_columns}")
    if report.unexpected_target_values:
        raise DatasetError(
            f"Unexpected values in '{TARGET_COLUMN}': {report.unexpected_target_values}"
        )
    if report.unexpected_categories:
        raise DatasetError(f"Unexpected category values: {report.unexpected_categories}")

    df = raw[RAW_COLUMNS].copy()
    df = fill_total_charges(df)
    for col in ["tenure", "MonthlyCharges"]:
        df[col] = pd.to_numeric(df[col], errors="raise").astype(float if col == "MonthlyCharges" else int)
    for col in BINARY_FEATURES:
        df[col] = pd.to_numeric(df[col], errors="raise").astype(int)
    for col in CATEGORICAL_FEATURES:
        df[col] = df[col].astype(object)
    df[ID_COLUMN] = df[ID_COLUMN].astype(object)
    df[TARGET_COLUMN] = df[TARGET_COLUMN].astype(object)
    return df


def load_dataset(path: str | Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Read, validate and clean the dataset in one call."""
    return clean_dataset(read_raw_csv(path))


def split_features_target(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Separate model features (identifier excluded) and a 0/1 target."""
    X = df[FEATURE_COLUMNS].copy()
    y = (df[TARGET_COLUMN] == POSITIVE_LABEL).astype(int).rename(TARGET_COLUMN)
    return X, y


def file_sha256(path: str | Path = RAW_DATA_PATH) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


__all__ = [
    "DatasetError",
    "DataQualityReport",
    "read_raw_csv",
    "check_quality",
    "fill_total_charges",
    "clean_dataset",
    "load_dataset",
    "split_features_target",
    "file_sha256",
    "NUMERIC_FEATURES",
]
