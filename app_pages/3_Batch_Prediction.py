import io

import pandas as pd
import streamlit as st

from src.predict import PREDICTION_COLUMN, PROBABILITY_COLUMN, RISK_BAND_COLUMN, predict_records
from src.schema import FEATURE_COLUMNS, ID_COLUMN
from src.validation import InputValidationError
from ui import charts
from ui.common import disclaimer, get_dataset, pct, require_model, setup_page

MAX_UPLOAD_MB = 10

setup_page("Batch Prediction", "📄")
model = require_model()

st.markdown(
    "Upload a CSV file of customers to score them all at once. The file must contain these "
    f"{len(FEATURE_COLUMNS)} columns with the same names and value formats as the IBM dataset. "
    "Other columns (for example `customerID`) are kept in the output but are not used by the model."
)
with st.expander("Required columns and allowed values"):
    from src.schema import CATEGORICAL_FEATURES

    rows = [(c, ", ".join(v)) for c, v in CATEGORICAL_FEATURES.items()]
    rows += [("SeniorCitizen", "0 or 1"), ("tenure", "whole number of months ≥ 0"),
             ("MonthlyCharges", "number ≥ 0"),
             ("TotalCharges", "number ≥ 0 (may be blank only when tenure is 0)")]
    st.dataframe(pd.DataFrame(rows, columns=["Column", "Allowed values"]), hide_index=True,
                 width="stretch")

try:
    sample = get_dataset().drop(columns=["Churn"]).head(5)
    st.download_button(
        "Download template CSV (5 real rows from the dataset, Churn column removed)",
        sample.to_csv(index=False).encode(), "churn_template.csv", "text/csv",
    )
except Exception:  # noqa: BLE001 - template is optional
    st.download_button("Download empty template CSV", (",".join([ID_COLUMN] + FEATURE_COLUMNS) + "\n").encode(),
                       "churn_template.csv", "text/csv")

with st.sidebar:
    st.markdown("### Decision threshold")
    threshold = st.slider("Predict churn when probability ≥", 0.05, 0.95, float(model.threshold), 0.01)
    st.caption(f"Model default: {model.threshold:.2f}")

upload = st.file_uploader("Customer CSV", type=["csv"])
if upload is None:
    st.info("Upload a CSV file to begin.")
    st.stop()

if upload.size > MAX_UPLOAD_MB * 1024 * 1024:
    st.error(f"The file is larger than {MAX_UPLOAD_MB} MB. Split it into smaller files.")
    st.stop()

try:
    raw = pd.read_csv(io.BytesIO(upload.getvalue()), dtype=str, keep_default_na=False)
except UnicodeDecodeError:
    st.error("The file could not be read as text. Save it as a UTF-8 encoded CSV and try again.")
    st.stop()
except Exception:  # noqa: BLE001
    st.error("The file could not be read as a CSV. Check that it is comma-separated with a header row.")
    st.stop()

if "Churn" in raw.columns:
    st.info("The file contains a `Churn` column. It is kept in the output for reference but not used "
            "for prediction.")

try:
    with st.spinner(f"Validating and scoring {len(raw):,} customers ..."):
        out, warnings = predict_records(model, raw, threshold)
except InputValidationError as exc:
    st.error("The file was rejected. No predictions were made. Fix these problems and upload it again:")
    for e in exc.errors:
        st.markdown(f"- {e}")
    st.stop()
except Exception:  # noqa: BLE001
    st.error("Predictions could not be generated for this file.")
    st.stop()

st.success(f"Scored {len(out):,} customers.")
if warnings:
    with st.expander(f"{len(warnings)} warning(s): predictions were made but check these records"):
        for w in warnings:
            st.markdown(f"- {w}")

n_churn = int((out[PREDICTION_COLUMN] == "Yes").sum())
c1, c2, c3, c4 = st.columns(4)
c1.metric("Customers", f"{len(out):,}")
c2.metric("Predicted to churn", f"{n_churn:,}", help=f"Probability ≥ {threshold:.2f}")
c3.metric("Share flagged", pct(n_churn / len(out)))
c4.metric("Mean churn probability", pct(out[PROBABILITY_COLUMN].mean()))

st.altair_chart(charts.probability_histogram(out[PROBABILITY_COLUMN], threshold),
                width="stretch", theme=None)
st.caption("Dashed line: decision threshold.")

st.markdown("##### Results")
show_only = st.checkbox("Show only customers predicted to churn")
view = out[out[PREDICTION_COLUMN] == "Yes"] if show_only else out
front = [c for c in [ID_COLUMN, PROBABILITY_COLUMN, PREDICTION_COLUMN, RISK_BAND_COLUMN] if c in view.columns]
view = view[front + [c for c in view.columns if c not in front]].sort_values(PROBABILITY_COLUMN, ascending=False)
st.dataframe(
    view, hide_index=True, width="stretch", height=420,
    column_config={PROBABILITY_COLUMN: st.column_config.ProgressColumn(
        "churn_probability", min_value=0.0, max_value=1.0, format="percent")},
)

st.download_button(
    "Download predictions (CSV)",
    out.to_csv(index=False).encode(),
    file_name=f"churn_predictions_{upload.name.rsplit('.', 1)[0]}.csv",
    mime="text/csv",
    type="primary",
)
st.caption("The download contains every original column unchanged, plus `churn_probability`, "
           "`predicted_churn` and `risk_band`.")
disclaimer()
