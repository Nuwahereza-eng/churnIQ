import pandas as pd
import pytest

from src.config import RAW_DATA_PATH
from src.data_loader import (
    DatasetError,
    check_quality,
    clean_dataset,
    load_dataset,
    read_raw_csv,
    split_features_target,
)
from src.schema import FEATURE_COLUMNS, ID_COLUMN, RAW_COLUMNS, TARGET_COLUMN


def test_missing_file_gives_helpful_error(tmp_path):
    with pytest.raises(DatasetError, match="download_data.py"):
        read_raw_csv(tmp_path / "nope.csv")


def test_load_synthetic_csv(synthetic_csv):
    df = load_dataset(synthetic_csv)
    assert list(df.columns) == RAW_COLUMNS
    assert df["TotalCharges"].dtype == float
    assert df["tenure"].dtype.kind == "i"
    assert df["SeniorCitizen"].isin([0, 1]).all()


def test_blank_total_charges_become_zero_for_new_customers(synthetic_raw):
    report = check_quality(synthetic_raw)
    assert report.blank_total_charges > 0
    assert report.blank_total_charges == report.blank_total_charges_with_zero_tenure
    df = clean_dataset(synthetic_raw)
    assert df["TotalCharges"].isna().sum() == 0
    assert (df.loc[df["tenure"] == 0, "TotalCharges"] == 0).all()


def test_blank_total_charges_with_positive_tenure_left_missing(synthetic_raw):
    raw = synthetic_raw.copy()
    idx = raw.index[raw["tenure"] != "0"][0]
    raw.loc[idx, "TotalCharges"] = ""
    df = clean_dataset(raw)
    assert pd.isna(df.loc[idx, "TotalCharges"])  # imputed later inside the pipeline


def test_missing_column_rejected(synthetic_raw):
    with pytest.raises(DatasetError, match="missing required columns"):
        clean_dataset(synthetic_raw.drop(columns=["Contract"]))


def test_unexpected_target_rejected(synthetic_raw):
    raw = synthetic_raw.copy()
    raw.loc[0, TARGET_COLUMN] = "Maybe"
    report = check_quality(raw)
    assert report.unexpected_target_values == ["Maybe"]
    assert not report.is_valid
    with pytest.raises(DatasetError, match="Unexpected values"):
        clean_dataset(raw)


def test_unexpected_category_rejected(synthetic_raw):
    raw = synthetic_raw.copy()
    raw.loc[0, "Contract"] = "Ten year"
    with pytest.raises(DatasetError, match="Unexpected category"):
        clean_dataset(raw)


def test_duplicates_detected(synthetic_raw):
    raw = pd.concat([synthetic_raw, synthetic_raw.iloc[[0]]], ignore_index=True)
    report = check_quality(raw)
    assert report.duplicate_rows == 1
    assert report.duplicate_ids == 1


def test_identifier_excluded_from_features(synthetic_csv):
    X, y = split_features_target(load_dataset(synthetic_csv))
    assert ID_COLUMN not in X.columns
    assert TARGET_COLUMN not in X.columns
    assert list(X.columns) == FEATURE_COLUMNS
    assert set(y.unique()) <= {0, 1}


@pytest.mark.skipif(not RAW_DATA_PATH.exists(), reason="real dataset not downloaded")
def test_real_dataset_matches_documented_properties():
    raw = read_raw_csv()
    report = check_quality(raw)
    assert report.is_valid
    assert report.n_rows == 7043
    assert report.blank_total_charges == 11
    assert report.blank_total_charges_with_zero_tenure == 11
    df = load_dataset()
    assert df["TotalCharges"].isna().sum() == 0
    assert set(df[TARGET_COLUMN]) == {"Yes", "No"}
