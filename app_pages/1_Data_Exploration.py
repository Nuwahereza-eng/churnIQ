import pandas as pd
import streamlit as st

from src.eda import add_tenure_band, association_with_churn, churn_rate_by, column_summary
from src.schema import CATEGORICAL_FEATURES, FEATURE_DESCRIPTIONS, NUMERIC_FEATURES
from ui import charts
from ui.common import get_quality_report, pct, require_dataset, setup_page

setup_page("Data Exploration", "🔎")
df = require_dataset()
overall = (df["Churn"] == "Yes").mean()

tab_overview, tab_groups, tab_numeric, tab_assoc, tab_data = st.tabs(
    ["Overview", "Customer groups", "Numeric features", "Associations", "Data table"]
)

with tab_overview:
    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", f"{df.shape[0]:,}")
    c2.metric("Columns", df.shape[1])
    c3.metric("Churn rate", pct(overall))

    st.markdown("##### Churn vs non-churn customers")
    st.altair_chart(charts.churn_distribution(df), width="stretch", theme=None)
    st.caption(
        "The classes are imbalanced: roughly one customer in four churned. Accuracy alone is "
        "therefore misleading (predicting 'No' for everyone is about 73% accurate), so the models "
        "are also judged on recall, precision, F1 and ROC-AUC."
    )

    st.markdown("##### Data quality checks")
    q = get_quality_report()
    checks = pd.DataFrame(
        [
            ("Required columns present", "Yes" if not q["missing_columns"] else ", ".join(q["missing_columns"])),
            ("Blank TotalCharges values", f"{q['blank_total_charges']} (all with tenure = 0: "
             f"{q['blank_total_charges_with_zero_tenure']})"),
            ("Other missing values", "None" if set(q["missing_values"]) <= {"TotalCharges"} else str(q["missing_values"])),
            ("Fully duplicated rows", q["duplicate_rows"]),
            ("Duplicate customer IDs", q["duplicate_ids"]),
            ("Rows identical apart from customer ID", q["duplicate_feature_rows"]),
            ("Unexpected target values", "None" if not q["unexpected_target_values"] else q["unexpected_target_values"]),
            ("Unexpected category values", "None" if not q["unexpected_categories"] else q["unexpected_categories"]),
        ],
        columns=["Check", "Result"],
    ).astype(str)
    st.dataframe(checks, hide_index=True, width="stretch")
    st.caption(
        "Blank TotalCharges occur only for customers in their first month (tenure 0) who have not "
        "yet been billed, so they are set to 0. Rows identical apart from the ID belong to different "
        "customers and are kept."
    )

    st.markdown("##### Column summary")
    st.dataframe(column_summary(df, FEATURE_DESCRIPTIONS), hide_index=True, width="stretch")

with tab_groups:
    options = ["Contract", "tenure_band", "InternetService", "PaymentMethod", "TechSupport",
               "OnlineSecurity", "PaperlessBilling", "SeniorCitizen", "Partner", "Dependents"]
    options += [c for c in CATEGORICAL_FEATURES if c not in options]
    labels = {"tenure_band": "Tenure band (months)", "SeniorCitizen": "SeniorCitizen (1 = 65+)"}
    feature = st.selectbox("Customer characteristic", options, format_func=lambda c: labels.get(c, c))
    data = add_tenure_band(df)
    table = churn_rate_by(data, feature)
    table["group"] = table["group"].astype(str)
    st.altair_chart(
        charts.churn_rate_bars(table, overall, f"Churn rate by {labels.get(feature, feature)}"),
        width="stretch", theme=None,
    )
    st.caption("Dashed line: overall churn rate. Hover over a bar for counts.")
    st.dataframe(
        table.drop(columns="feature").style.format({"churn_rate": "{:.1%}", "customers": "{:,}", "churned": "{:,}"}),
        hide_index=True, width="stretch",
    )

    st.markdown("##### Combine two characteristics")
    c1, c2 = st.columns(2)
    f1 = c1.selectbox("Rows", options, index=0, key="f1", format_func=lambda c: labels.get(c, c))
    f2 = c2.selectbox("Columns", options, index=2, key="f2", format_func=lambda c: labels.get(c, c))
    if f1 == f2:
        st.info("Choose two different characteristics.")
    else:
        pivot = data.assign(churn=(data["Churn"] == "Yes").astype(int)).pivot_table(
            index=f1, columns=f2, values="churn", aggfunc=["mean", "size"], observed=True
        )
        rates = pivot["mean"]
        sizes = pivot["size"]
        st.dataframe(
            rates.style.format("{:.1%}", na_rep="–").background_gradient(cmap="Blues", vmin=0, vmax=1),
            width="stretch",
        )
        st.caption(f"Churn rate per combination. Smallest cell: {int(sizes.min().min()):,} customers; "
                   "rates based on few customers are unreliable.")

with tab_numeric:
    col = st.selectbox("Numeric feature", NUMERIC_FEATURES)
    st.altair_chart(charts.numeric_distribution(df, col), width="stretch", theme=None)
    st.caption("Each panel shows the share of that class's customers in each range, so the shapes "
               "can be compared despite the class imbalance.")
    summary = df.groupby("Churn")[col].describe().round(2)
    st.dataframe(summary, width="stretch")
    if col == "tenure":
        st.markdown("Churners are concentrated among customers in their first months with the company.")

with tab_assoc:
    assoc = association_with_churn(df)
    st.altair_chart(charts.association_bars(assoc), width="stretch", theme=None)
    st.dataframe(
        assoc.style.format({"strength": "{:.3f}", "p_value": "{:.2e}"}),
        hide_index=True, width="stretch",
    )
    st.caption(
        "Categorical features: bias-corrected Cramér's V (0 = no association, 1 = perfect). "
        "Numeric features: point-biserial correlation with churn (sign shows direction). "
        "These are one-variable-at-a-time associations: they do not control for other variables "
        "(for example, tenure and TotalCharges are strongly related) and do not show causation."
    )
    corr = df[NUMERIC_FEATURES].corr().round(3)
    st.markdown("##### Correlation between numeric features")
    st.dataframe(corr.style.format("{:.3f}").background_gradient(cmap="Blues", vmin=-1, vmax=1),
                 width="stretch")

with tab_data:
    st.markdown("Filter the records (real rows from the IBM dataset).")
    c1, c2, c3 = st.columns(3)
    contract = c1.multiselect("Contract", CATEGORICAL_FEATURES["Contract"])
    internet = c2.multiselect("InternetService", CATEGORICAL_FEATURES["InternetService"])
    churn = c3.multiselect("Churn", ["No", "Yes"])
    view = df
    if contract:
        view = view[view["Contract"].isin(contract)]
    if internet:
        view = view[view["InternetService"].isin(internet)]
    if churn:
        view = view[view["Churn"].isin(churn)]
    if view.empty:
        st.info("No customers match these filters.")
    else:
        st.caption(f"{len(view):,} customers · churn rate {pct((view['Churn'] == 'Yes').mean())}")
        st.dataframe(view, hide_index=True, width="stretch", height=420)
