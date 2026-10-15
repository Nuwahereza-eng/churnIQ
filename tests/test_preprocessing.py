import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression

from src.data_loader import load_dataset, split_features_target
from src.preprocessing import build_pipeline, coerce_feature_types, transformed_feature_names
from src.schema import FEATURE_COLUMNS, ID_COLUMN


@pytest.fixture
def xy(synthetic_csv):
    return split_features_target(load_dataset(synthetic_csv))


def test_pipeline_fits_and_outputs_probabilities(xy):
    X, y = xy
    pipe = build_pipeline(LogisticRegression(max_iter=1000)).fit(X, y)
    proba = pipe.predict_proba(X)[:, 1]
    assert proba.shape == (len(X),)
    assert np.all((proba >= 0) & (proba <= 1))


def test_one_hot_columns_have_no_identifier(xy):
    X, y = xy
    pipe = build_pipeline(LogisticRegression(max_iter=1000)).fit(X, y)
    names = transformed_feature_names(pipe)
    assert not any(ID_COLUMN in n for n in names)
    assert any(n.startswith("cat__Contract_") for n in names)


def test_unseen_category_does_not_crash(xy):
    X, y = xy
    pipe = build_pipeline(LogisticRegression(max_iter=1000)).fit(X, y)
    row = X.iloc[[0]].copy()
    row["PaymentMethod"] = "Mobile money"  # never seen in training
    proba = pipe.predict_proba(row)[:, 1]
    assert 0 <= proba[0] <= 1


def test_missing_values_are_imputed(xy):
    X, y = xy
    pipe = build_pipeline(LogisticRegression(max_iter=1000)).fit(X, y)
    row = X.iloc[[0]].copy()
    row["TotalCharges"] = np.nan
    row["Contract"] = None
    assert np.isfinite(pipe.predict_proba(row)).all()


def test_imputer_learns_from_training_data_only(xy):
    X, y = xy
    train = X.iloc[:300]
    pipe = build_pipeline(LogisticRegression(max_iter=1000)).fit(train, y.iloc[:300])
    num = pipe.named_steps["preprocess"].named_transformers_["num"]
    cols = ["tenure", "MonthlyCharges", "TotalCharges"]
    assert np.allclose(num.named_steps["impute"].statistics_, train[cols].median())
    assert np.allclose(num.named_steps["scale"].mean_, train[cols].mean())


def test_column_order_and_extra_columns_do_not_change_predictions(xy):
    X, y = xy
    pipe = build_pipeline(LogisticRegression(max_iter=1000)).fit(X, y)
    shuffled = X[list(reversed(X.columns))].copy()
    shuffled["customerID"] = "ABC"
    assert np.allclose(pipe.predict_proba(X), pipe.predict_proba(shuffled))


def test_coerce_rejects_missing_columns(xy):
    X, _ = xy
    with pytest.raises(ValueError, match="Missing feature columns"):
        coerce_feature_types(X.drop(columns=["tenure"]))


def test_coerce_preserves_feature_order(xy):
    X, _ = xy
    assert list(coerce_feature_types(X).columns) == FEATURE_COLUMNS
