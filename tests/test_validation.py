import pandas as pd
import pytest

from src.schema import FEATURE_COLUMNS
from src.validation import InputValidationError, validate_or_raise, validate_records
from synthetic import make_feature_records


@pytest.fixture
def records():
    return make_feature_records(5)


def test_valid_records_pass(records):
    result = validate_records(records)
    assert result.ok, result.errors
    assert list(result.data.columns) == FEATURE_COLUMNS
    assert result.data["tenure"].dtype.kind == "i"
    assert result.data["MonthlyCharges"].dtype == float


def test_extra_columns_ignored_and_order_irrelevant(records):
    shuffled = records[list(reversed(records.columns))].copy()
    shuffled["notes"] = "x"
    result = validate_records(shuffled)
    assert result.ok
    assert list(result.data.columns) == FEATURE_COLUMNS


def test_missing_column(records):
    result = validate_records(records.drop(columns=["tenure", "Contract"]))
    assert not result.ok
    assert "tenure" in result.errors[0] and "Contract" in result.errors[0]


def test_empty_dataframe():
    result = validate_records(pd.DataFrame(columns=FEATURE_COLUMNS))
    assert not result.ok
    assert "no customer records" in result.errors[0]


def test_invalid_category(records):
    records.loc[1, "Contract"] = "Weekly"
    result = validate_records(records)
    assert not result.ok
    assert "row 3" in result.errors[0] and "Weekly" in result.errors[0]


def test_category_whitespace_is_stripped(records):
    records.loc[0, "Contract"] = "  Two year "
    result = validate_records(records)
    assert result.ok
    assert result.data.loc[0, "Contract"] == "Two year"


@pytest.mark.parametrize(
    "col,value,msg",
    [
        ("tenure", "abc", "must be a number"),
        ("tenure", -1, "between"),
        ("tenure", 3.5, "whole number"),
        ("MonthlyCharges", "", "must be a number"),
        ("MonthlyCharges", float("inf"), "finite"),
        ("TotalCharges", -5, "between"),
        ("SeniorCitizen", 2, "0 or 1"),
        ("gender", None, "empty"),
    ],
)
def test_invalid_values_rejected(records, col, value, msg):
    records[col] = records[col].astype(object)
    records.loc[0, col] = value
    result = validate_records(records)
    assert not result.ok
    assert any(msg in e for e in result.errors), result.errors


def test_blank_total_charges_allowed_for_zero_tenure(records):
    records["tenure"] = records["tenure"].astype(object)
    records["TotalCharges"] = records["TotalCharges"].astype(object)
    records.loc[0, ["tenure", "TotalCharges"]] = [0, " "]
    result = validate_records(records)
    assert result.ok, result.errors
    assert result.data.loc[0, "TotalCharges"] == 0.0


def test_blank_total_charges_rejected_for_existing_customer(records):
    records["tenure"] = records["tenure"].astype(object)
    records["TotalCharges"] = records["TotalCharges"].astype(object)
    records.loc[0, ["tenure", "TotalCharges"]] = [12, ""]
    result = validate_records(records)
    assert not result.ok


def test_inconsistent_services_warn_but_pass(records):
    records.loc[0, "InternetService"] = "No"
    records.loc[0, "TechSupport"] = "Yes"
    result = validate_records(records)
    assert result.ok
    assert any("TechSupport" in w for w in result.warnings)


def test_out_of_training_range_warns(records):
    records["tenure"] = records["tenure"].astype(object)
    records.loc[0, "tenure"] = 200
    result = validate_records(records, training_ranges={"tenure": (0, 72)})
    assert result.ok
    assert any("outside the training range" in w for w in result.warnings)


def test_validate_or_raise(records):
    records.loc[0, "PaymentMethod"] = "Bitcoin"
    with pytest.raises(InputValidationError) as exc:
        validate_or_raise(records)
    assert exc.value.errors
