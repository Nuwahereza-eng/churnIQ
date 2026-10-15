import streamlit as st

from src.eda import highest_churn_groups
from ui import charts
from ui.common import pct, require_dataset, require_results, setup_page

setup_page("Insights", "💡")
df = require_dataset()
results = require_results()
meta = results["metadata"]
overall = (df["Churn"] == "Yes").mean()

st.warning(
    "**Association is not causation.** The patterns below describe which customers churned in this "
    "historical, fictional dataset and what the model relies on to predict churn. They do not show "
    "that changing a characteristic (for example moving a customer to a longer contract) would cause "
    "them to stay. Establishing that requires controlled experiments.",
    icon="⚠️",
)

st.subheader("1. Groups with the highest churn rates")
top = highest_churn_groups(df, min_customers=200, top=8)
top["label"] = top["feature"] + " = " + top["group"].astype(str)
st.altair_chart(
    charts.churn_rate_bars(top.assign(group=top["label"]), overall),
    width="stretch", theme=None,
)
st.caption(f"Single characteristics shared by at least 200 customers. Dashed line: overall churn rate "
           f"({pct(overall)}). Many of these groups overlap (e.g. new customers are mostly on "
           "month-to-month contracts).")

st.markdown(
    "- **Contract length** shows the largest differences: month-to-month customers churn far more than "
    "those on one- or two-year contracts.\n"
    "- **Early tenure**: customers in their first months churn most; churn falls steadily with tenure.\n"
    "- **Fibre-optic internet** customers churn more than DSL customers; they also pay higher monthly "
    "charges, so the two effects cannot be separated from this data alone.\n"
    "- **Electronic check** payers churn more than customers on automatic payment methods.\n"
    "- Customers **without online security or technical support** add-ons churn more."
)
st.caption("These statements summarise the charts on the Data Exploration page; check the exact figures there.")

st.subheader("2. What the model relies on")
st.markdown(
    f"**Permutation importance** of the deployed {meta['selected_model']} on the test set: how much "
    "ROC-AUC drops when one column's values are randomly shuffled. Larger drops mean the model relies "
    "more on that column."
)
perm = results["permutation_importance"]
st.altair_chart(
    charts.importance_bars(perm, "mean", "Drop in ROC-AUC when shuffled", error="std"),
    width="stretch", theme=None,
)
st.caption(
    "When columns carry overlapping information (tenure, TotalCharges and Contract are related), shuffling "
    "one leaves the others available, so the importance of correlated features can be understated. "
    "Values near zero mean the model can do as well without that column, not that it is unrelated to churn."
)

st.subheader("3. Model-specific views")
imps = results["model_importances"]
tab_lr, tab_rf, tab_dt = st.tabs(["Logistic Regression coefficients", "Random Forest", "Decision Tree"])
with tab_lr:
    if imps.get("Logistic Regression"):
        st.altair_chart(
            charts.importance_bars(imps["Logistic Regression"][:15], "value",
                                   "Coefficient (change in log-odds of churn)", signed=True),
            width="stretch", theme=None,
        )
        st.caption(
            "Numeric features are standardised, so their coefficients are per standard deviation. Category "
            "coefficients are relative to the other categories of the same feature. Correlated features "
            "(tenure, TotalCharges, MonthlyCharges) can take offsetting signs, so read them together."
        )
with tab_rf:
    if imps.get("Random Forest"):
        st.altair_chart(
            charts.importance_bars(imps["Random Forest"][:15], "value", "Impurity-based importance"),
            width="stretch", theme=None,
        )
        st.caption("Impurity-based importance favours numeric and high-cardinality features; prefer the "
                   "permutation importance above for interpretation.")
with tab_dt:
    if imps.get("Decision Tree"):
        st.altair_chart(
            charts.importance_bars(imps["Decision Tree"][:15], "value", "Impurity-based importance"),
            width="stretch", theme=None,
        )

st.subheader("4. Using these insights responsibly")
st.markdown(
    "- Treat churn scores as **decision support** for prioritising outreach, not as verdicts about individuals.\n"
    "- Never use a high churn score to penalise a customer (e.g. withdrawing service or raising prices).\n"
    "- Check flagged customers with human judgement and other information before acting.\n"
    "- Monitor results: if retention offers are targeted using the model, the data used to retrain it will "
    "change, and its performance should be re-evaluated.\n"
    "- The data is fictional and US-styled; patterns may not transfer to other markets (for example Uganda) "
    "without retraining and re-validating on local data."
)
