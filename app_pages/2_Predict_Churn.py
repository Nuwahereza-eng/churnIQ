import pandas as pd
import streamlit as st

from src.predict import predict_one, predict_records
from src.schema import CATEGORICAL_FEATURES, INTERNET_ADDONS
from src.validation import InputValidationError
from ui import charts
from ui.common import disclaimer, pct, require_model, setup_page

setup_page("Predict Churn", "🧮")
model = require_model()
meta = model.metadata

st.markdown(
    "Enter a customer's details to estimate their probability of churning. The estimate comes "
    f"from the trained **{meta['selected_model']}** pipeline (calibrated)."
)

with st.sidebar:
    st.markdown("### Decision threshold")
    threshold = st.slider(
        "Predict churn when probability ≥", 0.05, 0.95, float(model.threshold), 0.01,
        help="Lower values flag more customers (higher recall, more false alarms). "
             "Higher values flag fewer customers (higher precision, more missed churners). "
             "The default was chosen on training data to maximise F1.",
    )
    st.caption(f"Model default: {model.threshold:.2f}")

YES_NO = CATEGORICAL_FEATURES["Partner"]
ADDON_LABELS = {
    "OnlineSecurity": "Online security", "OnlineBackup": "Online backup",
    "DeviceProtection": "Device protection", "TechSupport": "Technical support",
    "StreamingTV": "Streaming TV", "StreamingMovies": "Streaming movies",
}

st.markdown("#### Account")
a1, a2, a3 = st.columns(3)
tenure = a1.number_input("Tenure (months with the company)", min_value=0, max_value=120, value=12, step=1)
contract = a2.selectbox("Contract", CATEGORICAL_FEATURES["Contract"])
payment = a3.selectbox("Payment method", CATEGORICAL_FEATURES["PaymentMethod"])
b1, b2, b3 = st.columns(3)
monthly = b1.number_input("Monthly charges", min_value=0.0, max_value=1000.0, value=70.0, step=0.5, format="%.2f")
auto_total = b2.checkbox("Estimate total charges as tenure × monthly charges", value=True)
total = b2.number_input(
    "Total charges", min_value=0.0, max_value=100_000.0,
    value=float(round(tenure * monthly, 2)), step=10.0, format="%.2f", disabled=auto_total,
)
if auto_total:
    total = round(tenure * monthly, 2)
paperless = b3.radio("Paperless billing", YES_NO, index=1, horizontal=True)

st.markdown("#### Services")
s1, s2, s3 = st.columns(3)
phone = s1.radio("Phone service", YES_NO, index=1, horizontal=True)
if phone == "No":
    multiple = "No phone service"
    s1.caption("Multiple lines: not applicable (no phone service)")
else:
    multiple = s1.radio("Multiple lines", YES_NO, horizontal=True)
internet = s2.selectbox("Internet service", CATEGORICAL_FEATURES["InternetService"], index=1)
addons = {}
if internet == "No":
    for col in INTERNET_ADDONS:
        addons[col] = "No internet service"
    s3.caption("Internet add-ons are not applicable without internet service.")
else:
    with s3:
        for col in INTERNET_ADDONS:
            addons[col] = st.radio(ADDON_LABELS[col], YES_NO, horizontal=True, key=col)

st.markdown("#### Customer")
d1, d2, d3, d4 = st.columns(4)
gender = d1.radio("Gender", CATEGORICAL_FEATURES["gender"], horizontal=True)
senior = d2.radio("Senior citizen (65+)", YES_NO, horizontal=True)
partner = d3.radio("Partner", YES_NO, horizontal=True)
dependents = d4.radio("Dependents", YES_NO, horizontal=True)

record = {
    "gender": gender, "SeniorCitizen": 1 if senior == "Yes" else 0, "Partner": partner,
    "Dependents": dependents, "tenure": int(tenure), "PhoneService": phone,
    "MultipleLines": multiple, "InternetService": internet, **addons,
    "Contract": contract, "PaperlessBilling": paperless, "PaymentMethod": payment,
    "MonthlyCharges": float(monthly), "TotalCharges": float(total),
}

st.divider()
if st.button("Estimate churn probability", type="primary"):
    st.session_state["last_record"] = record

if "last_record" in st.session_state:
    if st.session_state["last_record"] != record:
        st.caption("The inputs have changed since the last estimate. Press the button to update it.")
    rec = st.session_state["last_record"]
    try:
        with st.spinner("Scoring ..."):
            result = predict_one(model, rec, threshold)
    except InputValidationError as exc:
        st.error("Some inputs are invalid:")
        for e in exc.errors:
            st.markdown(f"- {e.replace('row 2: ', '')}")
        st.stop()
    except Exception:  # noqa: BLE001
        st.error("The prediction could not be generated. Please check the inputs and try again.")
        st.stop()

    p = result["probability"]
    churn = result["prediction"] == "Yes"
    r1, r2, r3 = st.columns(3)
    r1.metric("Estimated churn probability", pct(p))
    r2.metric("Prediction", "Likely to churn" if churn else "Likely to stay")
    r3.metric("Risk band", result["risk_band"])
    st.markdown(
        f"The model estimates that customers with this profile churned about **{pct(p, 0)}** of the time. "
        f"Because this is {'at or above' if churn else 'below'} the decision threshold of "
        f"{threshold:.2f}, the customer is classified as **{'likely to churn' if churn else 'likely to stay'}**."
    )
    st.caption("Risk bands are display groupings of the probability: Low < 30%, Medium 30–60%, High ≥ 60%.")
    for w in result["warnings"]:
        st.warning(w.replace("row 2: ", ""))

    st.markdown("##### How would the estimate differ with another contract?")
    scenarios = pd.DataFrame([{**rec, "Contract": c} for c in CATEGORICAL_FEATURES["Contract"]])
    scored, _ = predict_records(model, scenarios, threshold)
    data = pd.DataFrame({
        "scenario": [f"{c}{' (current)' if c == rec['Contract'] else ''}" for c in scored["Contract"]],
        "probability": scored["churn_probability"],
        "current": scored["Contract"] == rec["Contract"],
    })
    st.altair_chart(charts.scenario_bars(data, threshold), width="stretch", theme=None)
    st.caption(
        "Same customer, only the contract type changed. This shows how the model's estimate depends on "
        "contract type. It is not evidence that changing a customer's contract would change their behaviour."
    )
    disclaimer()
else:
    st.info("Fill in the details above and press **Estimate churn probability**.")
