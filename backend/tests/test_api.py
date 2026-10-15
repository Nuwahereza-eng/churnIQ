"""API tests for the ChurnIQ FastAPI backend."""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from backend.app.core.config import Settings  # noqa: E402
from backend.app.main import create_app  # noqa: E402
from src.config import METADATA_PATH, MODEL_PATH, RAW_DATA_PATH, RESULTS_PATH  # noqa: E402
from src.schema import FEATURE_COLUMNS  # noqa: E402
from synthetic import make_feature_records  # noqa: E402  (SYNTHETIC test data)

REAL_FILES = all(p.exists() for p in [RAW_DATA_PATH, MODEL_PATH, METADATA_PATH, RESULTS_PATH])
needs_real = pytest.mark.skipif(not REAL_FILES, reason="real dataset/model/results not available")

CUSTOMER = {
    "gender": "Female", "SeniorCitizen": 0, "Partner": "No", "Dependents": "No", "tenure": 2,
    "PhoneService": "Yes", "MultipleLines": "No", "InternetService": "Fiber optic",
    "OnlineSecurity": "No", "OnlineBackup": "No", "DeviceProtection": "No", "TechSupport": "No",
    "StreamingTV": "No", "StreamingMovies": "No", "Contract": "Month-to-month",
    "PaperlessBilling": "Yes", "PaymentMethod": "Electronic check",
    "MonthlyCharges": 80.0, "TotalCharges": 160.0,
}


@pytest.fixture(scope="module")
def client():
    return TestClient(create_app(Settings(cors_origins=["http://localhost:5173"])))


@pytest.fixture
def empty_client(tmp_path):
    """App whose dataset, model and results files do not exist."""
    s = Settings(data_path=tmp_path / "missing.csv", model_path=tmp_path / "m.joblib",
                 metadata_path=tmp_path / "m.json", results_path=tmp_path / "r.json")
    return TestClient(create_app(s))


def _csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode()


def _upload(client, path, content: bytes, name="customers.csv", **params):
    return client.post(path, files={"file": (name, content, "text/csv")}, params=params)


def _assert_error(resp, status, code=None):
    assert resp.status_code == status, resp.text
    body = resp.json()
    assert set(body) == {"error"} and {"code", "message", "details"} <= set(body["error"])
    if code:
        assert body["error"]["code"] == code
    text = resp.text.lower()
    for leak in ("traceback", "/home/", "site-packages", 'file "', str(ROOT).lower()):
        assert leak not in text, f"error response leaks internal detail: {leak}"
    return body["error"]


# ---------------- health / missing resources ----------------

@needs_real
def test_health_ok(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok" and body["model_available"] and body["dataset_available"]
    assert body["model_name"].startswith("Calibrated")


def test_health_degraded_when_files_missing(empty_client):
    body = empty_client.get("/api/health").json()
    assert body["status"] == "degraded"
    assert not (body["model_available"] or body["dataset_available"] or body["results_available"])


@pytest.mark.parametrize("method,path", [
    ("get", "/api/overview"), ("get", "/api/customers"), ("get", "/api/insights"),
    ("get", "/api/model/metrics"), ("get", "/api/schema"),
])
def test_missing_resources_return_503(empty_client, method, path):
    _assert_error(getattr(empty_client, method)(path), 503, "service_unavailable")


def test_predict_without_model_returns_503(empty_client):
    _assert_error(empty_client.post("/api/predict", json={"customer": CUSTOMER}), 503, "service_unavailable")


# ---------------- overview / customers / insights / metrics ----------------

@needs_real
def test_overview_matches_dataset(client):
    body = client.get("/api/overview").json()
    df = pd.read_csv(RAW_DATA_PATH)
    assert body["total_customers"] == len(df)
    assert body["churned"] == int((df["Churn"] == "Yes").sum())
    assert body["churned"] + body["stayed"] == body["total_customers"]
    assert body["churn_rate"] == pytest.approx(body["churned"] / body["total_customers"], abs=1e-4)
    contracts = {g["group"]: g for g in body["churn_by_contract"]}
    mtm = df[df["Contract"] == "Month-to-month"]
    assert contracts["Month-to-month"]["customers"] == len(mtm)
    assert [g["group"] for g in body["churn_by_tenure"]] == ["0-6", "7-12", "13-24", "25-48", "49-72"]
    assert sum(b["stayed"] + b["churned"] for b in body["monthly_charges_histogram"]) == len(df)


@needs_real
def test_customers_pagination_filters_and_sort(client):
    r = client.get("/api/customers", params={"page": 1, "page_size": 10, "contract": ["Two year"],
                                             "churn": "Yes", "sort_by": "MonthlyCharges", "sort_dir": "desc"})
    body = r.json()
    assert r.status_code == 200
    assert body["page_size"] == 10 and len(body["items"]) <= 10
    assert all(i["Contract"] == "Two year" and i["Churn"] == "Yes" for i in body["items"])
    charges = [i["MonthlyCharges"] for i in body["items"]]
    assert charges == sorted(charges, reverse=True)
    df = pd.read_csv(RAW_DATA_PATH)
    assert body["total"] == int(((df["Contract"] == "Two year") & (df["Churn"] == "Yes")).sum())
    assert set(body["items"][0]) == {"customerID", "tenure", "Contract", "InternetService", "PaymentMethod",
                                     "TechSupport", "MonthlyCharges", "TotalCharges", "Churn"}


@needs_real
def test_customers_search_and_tenure_range(client):
    first = client.get("/api/customers", params={"page_size": 1}).json()["items"][0]["customerID"]
    body = client.get("/api/customers", params={"search": first[:6].lower()}).json()
    assert any(i["customerID"] == first for i in body["items"])
    body = client.get("/api/customers", params={"tenure_min": 10, "tenure_max": 12, "page_size": 100}).json()
    assert all(10 <= i["tenure"] <= 12 for i in body["items"])


@needs_real
def test_customers_page_size_is_capped_and_bad_params_rejected(client):
    assert client.get("/api/customers", params={"page_size": 5000}).json()["page_size"] == 100
    _assert_error(client.get("/api/customers", params={"sort_by": "secret"}), 422)
    _assert_error(client.get("/api/customers", params={"contract": "Weekly"}), 422, "invalid_request")
    _assert_error(client.get("/api/customers", params={"page": 0}), 422)


@needs_real
def test_insights(client):
    body = client.get("/api/insights").json()
    for key in ["churn_by_contract", "churn_by_tenure", "churn_by_internet_service",
                "churn_by_payment_method", "churn_by_monthly_charge_band"]:
        assert body[key] and all(0 <= g["churn_rate"] <= 1 for g in body[key])
    assert body["permutation_importance"][0]["feature"] in FEATURE_COLUMNS
    assert body["associations"]


@needs_real
def test_model_metrics_match_saved_results(client):
    import json
    saved = json.loads(RESULTS_PATH.read_text())
    body = client.get("/api/model/metrics").json()
    assert body["selected_model"] == saved["metadata"]["selected_model"]
    names = [m["name"] for m in body["models"]]
    assert names == list(saved["models"])
    for m in body["models"]:
        assert m["test"]["metrics"] == pytest.approx(saved["models"][m["name"]]["test"]["metrics"])
        assert m["test"]["roc_curve"] and m["test"]["pr_curve"]
    assert body["deployed"]["decision_threshold"] == saved["deployed_model"]["decision_threshold"]
    assert body["methodology"]["n_test"] == saved["metadata"]["n_test"]


# ---------------- schema ----------------

@needs_real
def test_schema_and_template(client):
    body = client.get("/api/schema").json()
    assert [f["name"] for f in body["features"]] == FEATURE_COLUMNS
    contract = next(f for f in body["features"] if f["name"] == "Contract")
    assert contract["allowed_values"] == ["Month-to-month", "One year", "Two year"]
    r = client.get("/api/schema/template.csv")
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/csv")
    assert r.text.strip().split(",") == ["customerID"] + FEATURE_COLUMNS


# ---------------- single prediction ----------------

@needs_real
def test_predict_valid(client):
    r = client.post("/api/predict", json={"customer": CUSTOMER})
    assert r.status_code == 200, r.text
    body = r.json()
    assert 0 <= body["churn_probability"] <= 1
    assert body["predicted_label"] in {"Yes", "No"}
    assert body["predicted_churn"] == (body["churn_probability"] >= body["threshold"])
    assert body["risk_band"] in {"Low", "Medium", "High"}


@needs_real
def test_predict_matches_existing_pipeline(client):
    from src.predict import load_model, predict_one
    expected = predict_one(load_model(), dict(CUSTOMER))["probability"]
    assert client.post("/api/predict", json={"customer": CUSTOMER}).json()["churn_probability"] == expected


@needs_real
def test_predict_threshold_override(client):
    low = client.post("/api/predict", json={"customer": CUSTOMER, "threshold": 0.01}).json()
    high = client.post("/api/predict", json={"customer": CUSTOMER, "threshold": 0.99}).json()
    assert low["predicted_label"] == "Yes" and high["predicted_label"] == "No"
    _assert_error(client.post("/api/predict", json={"customer": CUSTOMER, "threshold": 1.5}), 422)


@needs_real
def test_predict_new_customer_without_total_charges(client):
    r = client.post("/api/predict", json={"customer": {**CUSTOMER, "tenure": 0, "TotalCharges": None}})
    assert r.status_code == 200


@pytest.mark.parametrize("change,fragment", [
    ({"Contract": "Weekly"}, "customer.Contract"),
    ({"tenure": -3}, "customer.tenure"),
    ({"MonthlyCharges": "abc"}, "customer.MonthlyCharges"),
    ({"SeniorCitizen": 2}, "customer.SeniorCitizen"),
    ({"TotalCharges": None}, "TotalCharges is required"),
    ({"unexpected_field": 1}, "unexpected_field"),
])
def test_predict_invalid_inputs(client, change, fragment):
    err = _assert_error(client.post("/api/predict", json={"customer": {**CUSTOMER, **change}}), 422, "invalid_request")
    assert any(fragment in d for d in err["details"]), err["details"]


def test_predict_missing_field(client):
    body = {k: v for k, v in CUSTOMER.items() if k != "Contract"}
    err = _assert_error(client.post("/api/predict", json={"customer": body}), 422)
    assert any("Contract" in d for d in err["details"])


@needs_real
def test_predict_inconsistent_services_warns(client):
    r = client.post("/api/predict", json={"customer": {**CUSTOMER, "InternetService": "No"}})
    assert r.status_code == 200
    assert any("inconsistent" in w for w in r.json()["warnings"])


# ---------------- batch ----------------

@needs_real
def test_batch_validate_and_predict(client):
    records = make_feature_records(25, seed=3)
    v = _upload(client, "/api/predict/batch/validate", _csv(records)).json()
    assert v["valid"] and v["n_rows"] == 25 and len(v["preview"]) == 10
    assert v["extra_columns"] == ["customerID"]

    r = _upload(client, "/api/predict/batch", _csv(records))
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["n_records"] == 25 and len(body["rows"]) == 25
    assert body["columns"][: len(records.columns)] == list(records.columns)
    assert body["columns"][-3:] == ["churn_probability", "predicted_churn", "risk_band"]
    for row, original in zip(body["rows"], records.to_dict(orient="records")):
        assert row["customerID"] == original["customerID"]
        assert 0 <= row["churn_probability"] <= 1
        assert row["predicted_churn"] in {"Yes", "No"}
    assert body["n_predicted_churn"] == sum(r["predicted_churn"] == "Yes" for r in body["rows"])


@needs_real
def test_batch_invalid_values_rejected(client):
    records = make_feature_records(5, seed=4)
    records.loc[2, "Contract"] = "Lifetime"
    v = _upload(client, "/api/predict/batch/validate", _csv(records)).json()
    assert not v["valid"] and any("row 4" in e for e in v["errors"])
    err = _assert_error(_upload(client, "/api/predict/batch", _csv(records)), 422, "invalid_records")
    assert any("Lifetime" in d for d in err["details"])


@needs_real
@pytest.mark.parametrize("name,content,status,code", [
    ("customers.txt", b"a,b\n1,2\n", 415, "unsupported_file"),
    ("customers.csv", b"", 422, "empty_file"),
    ("customers.csv", b"   \n", 422, "empty_file"),
    ("customers.csv", ",".join(FEATURE_COLUMNS).encode() + b"\n", 422, "empty_file"),
    ("customers.csv", b"\xff\xfe\x00bad", 422, "malformed_file"),
    ("customers.csv", b'a,b\n"unterminated,2\n', 422, None),
])
def test_batch_bad_files(client, name, content, status, code):
    _assert_error(_upload(client, "/api/predict/batch", content, name=name), status, code)


@needs_real
def test_batch_incompatible_columns(client):
    err = _assert_error(_upload(client, "/api/predict/batch", b"foo,bar\n1,2\n"), 422, "invalid_records")
    assert "Missing required column" in err["details"][0]


def test_batch_oversized_upload(tmp_path):
    s = Settings(max_upload_bytes=1000)
    c = TestClient(create_app(s))
    if not s.model_path.exists():
        pytest.skip("model not available")
    big = _csv(make_feature_records(50, seed=5))
    _assert_error(_upload(c, "/api/predict/batch", big), 413, "file_too_large")


def test_batch_too_many_rows():
    s = Settings(max_batch_rows=10)
    if not s.model_path.exists():
        pytest.skip("model not available")
    c = TestClient(create_app(s))
    _assert_error(_upload(c, "/api/predict/batch", _csv(make_feature_records(11, seed=6))), 413, "too_many_rows")


def test_batch_missing_file(client):
    _assert_error(client.post("/api/predict/batch"), 422)


# ---------------- CORS ----------------

def test_cors_allows_only_configured_origin(client):
    ok = client.options("/api/health", headers={"Origin": "http://localhost:5173",
                                                 "Access-Control-Request-Method": "GET"})
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:5173"
    bad = client.options("/api/health", headers={"Origin": "http://evil.example",
                                                  "Access-Control-Request-Method": "GET"})
    assert "access-control-allow-origin" not in bad.headers


# ---------------- production: serving the built frontend ----------------

def test_serves_frontend_when_static_dir_set(tmp_path):
    (tmp_path / "assets").mkdir()
    (tmp_path / "index.html").write_text("<!doctype html><div id=root></div>")
    (tmp_path / "assets" / "app.js").write_text("console.log(1)")
    (tmp_path / "favicon.svg").write_text("<svg/>")
    (tmp_path.parent / "secret.txt").write_text("do not serve")
    c = TestClient(create_app(Settings(static_dir=tmp_path)))

    assert c.get("/").text.startswith("<!doctype html>")
    assert c.get("/predict").text.startswith("<!doctype html>")  # client-side route
    assert c.get("/assets/app.js").text == "console.log(1)"
    assert c.get("/favicon.svg").text == "<svg/>"
    assert "do not serve" not in c.get("/../secret.txt").text
    _assert_error(c.get("/api/does-not-exist"), 404)
    assert c.get("/api/health").status_code == 200


def test_frontend_not_served_by_default(client):
    assert client.get("/").status_code == 404

