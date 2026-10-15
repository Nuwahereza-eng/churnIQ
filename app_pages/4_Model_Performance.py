import pandas as pd
import streamlit as st

from ui import charts
from ui.common import pct, require_results, setup_page

setup_page("Model Performance", "📊")
results = require_results()
meta = results["metadata"]
models = results["models"]
deployed = results["deployed_model"]
base_rate = deployed["observed_churn_rate_test"]

st.markdown(
    f"Three algorithms were tuned with {meta['cv_folds']}-fold stratified cross-validation on the "
    f"training set ({meta['n_train']:,} customers) and evaluated once on the same held-out test set "
    f"({meta['n_test']:,} customers, {pct(base_rate)} churners). The test set played no part in tuning "
    f"or selection. **Selected: {meta['selected_model']}** ({meta['selection_metric']})."
)

# ---------------- Comparison table ----------------
st.subheader("Comparison of algorithms")
rows = []
for name, r in models.items():
    m = r["test"]["metrics"]
    rows.append({
        "Model": name,
        "CV ROC-AUC (mean ± sd)": f"{r['cv']['roc_auc']['mean']:.3f} ± {r['cv']['roc_auc']['std']:.3f}",
        "Accuracy": m["accuracy"], "Precision": m["precision"], "Recall": m["recall"],
        "F1": m["f1"], "ROC-AUC": m["roc_auc"], "Avg. precision": m["average_precision"],
        "Brier": m["brier_score"],
    })
b = results["baseline_majority_class"]
rows.append({"Model": "Majority-class baseline", "CV ROC-AUC (mean ± sd)": "–",
             "Accuracy": b["accuracy"], "Precision": b["precision"], "Recall": b["recall"], "F1": b["f1"],
             "ROC-AUC": b["roc_auc"], "Avg. precision": b["average_precision"], "Brier": b["brier_score"]})
table = pd.DataFrame(rows)
num_cols = ["Accuracy", "Precision", "Recall", "F1", "ROC-AUC", "Avg. precision", "Brier"]
st.dataframe(table.style.format({c: "{:.3f}" for c in num_cols}), hide_index=True, width="stretch")
st.caption(
    "Test-set metrics at a threshold of 0.5 for the uncalibrated, class-weighted models. "
    "Brier score: mean squared error of the probabilities (lower is better). The baseline always "
    "predicts 'no churn': its 73% accuracy shows why accuracy alone is a poor guide here."
)

long = pd.DataFrame([
    {"model": name, "metric": label, "value": r["test"]["metrics"][key]}
    for name, r in models.items()
    for key, label in [("accuracy", "Accuracy"), ("precision", "Precision"), ("recall", "Recall"),
                       ("f1", "F1"), ("roc_auc", "ROC-AUC")]
])
st.altair_chart(charts.metric_comparison(long), width="stretch", theme=None)

aucs = sorted(((r["cv"]["roc_auc"]["mean"], r["cv"]["roc_auc"]["std"], n) for n, r in models.items()), reverse=True)
gap = aucs[0][0] - aucs[1][0]
if gap < aucs[0][1]:
    st.info(
        f"The difference in cross-validated ROC-AUC between {aucs[0][2]} and {aucs[1][2]} "
        f"({gap:.3f}) is smaller than one standard deviation across folds ({aucs[0][1]:.3f}), "
        "so their ranking may not be stable. They should be regarded as performing similarly."
    )

# ---------------- Curves ----------------
st.subheader("ROC and precision–recall curves")
c1, c2 = st.columns(2)
with c1:
    st.markdown("**ROC curve**")
    st.altair_chart(charts.roc_curves(results), width="stretch", theme=None)
    st.caption("Dashed diagonal: random guessing. Higher and further left is better.")
with c2:
    st.markdown("**Precision–recall curve**")
    st.altair_chart(charts.pr_curves(results, base_rate), width="stretch", theme=None)
    st.caption("Dashed line: churn rate, the precision of random guessing. More informative than ROC "
               "when the positive class is the minority.")

# ---------------- Confusion matrices ----------------
st.subheader("Confusion matrix")
choice = st.radio("Model", list(models) + [f"Deployed: calibrated {meta['selected_model']}"], horizontal=True)
if choice.startswith("Deployed"):
    ev, thr = deployed["test"], deployed["decision_threshold"]
else:
    ev, thr = models[choice]["test"], 0.5
c1, c2 = st.columns([1, 1])
with c1:
    st.altair_chart(charts.confusion_matrix_chart(ev["confusion_matrix"]), width="stretch", theme=None)
    st.caption(f"Threshold {thr:.2f}. Percentages are shares of all test customers.")
with c2:
    report = pd.DataFrame(ev["classification_report"]).T
    report = report.loc[["No churn", "Churn", "macro avg", "weighted avg"]]
    st.dataframe(report.style.format({"precision": "{:.3f}", "recall": "{:.3f}", "f1-score": "{:.3f}",
                                      "support": "{:,.0f}"}), width="stretch")
    m = ev["metrics"]
    st.markdown(
        f"- **False positives ({m['fp']:,})**: customers flagged as likely to churn who stayed. Cost: "
        "retention offers or contact spent on customers who did not need them.\n"
        f"- **False negatives ({m['fn']:,})**: churners the model missed. Cost: lost revenue from "
        "customers who could have been approached.\n\n"
        "Because missing a churner usually costs more than an unnecessary offer, recall is "
        "prioritised over precision, but the right balance depends on the cost of the retention action."
    )

# ---------------- Threshold & calibration ----------------
st.subheader("Deployed model: threshold and calibration")
st.markdown(
    f"Class weighting makes the models over-estimate churn probabilities (for the selected model, mean "
    f"predicted probability {pct(deployed['mean_predicted_uncalibrated'])} vs an observed churn rate of "
    f"{pct(base_rate)}). The deployed model therefore applies {deployed['calibration']}. "
    f"Brier score: **{deployed['brier_uncalibrated']:.3f} → {deployed['brier_calibrated']:.3f}** after "
    f"calibration. The decision threshold **{deployed['decision_threshold']:.2f}** "
    f"{deployed['threshold_rule']}."
)
dm = deployed["test"]["metrics"]
cols = st.columns(5)
cols[0].metric("ROC-AUC", f"{dm['roc_auc']:.3f}")
cols[1].metric("Recall", pct(dm["recall"]))
cols[2].metric("Precision", pct(dm["precision"]))
cols[3].metric("F1", f"{dm['f1']:.3f}")
cols[4].metric("Accuracy", pct(dm["accuracy"]))

c1, c2 = st.columns(2)
with c1:
    st.markdown("**Effect of the decision threshold (test set)**")
    st.altair_chart(charts.threshold_chart(deployed["test"]["threshold_table"], deployed["decision_threshold"]),
                    width="stretch", theme=None)
    st.caption("Lowering the threshold catches more churners (recall rises) but more of the flagged "
               "customers would have stayed (precision falls). Dashed line: deployed threshold.")
with c2:
    st.markdown("**Calibration (reliability diagram, test set)**")
    points = {
        f"{meta['selected_model']} (uncalibrated)": models[meta["selected_model"]]["test"]["calibration_curve"],
        "Deployed (calibrated)": deployed["test"]["calibration_curve"],
    }
    st.altair_chart(charts.calibration_chart(points), width="stretch", theme=None)
    st.caption("Points on the dashed diagonal mean that a predicted probability of, say, 40% corresponds "
               "to about 40% of such customers actually churning.")

with st.expander("Threshold table (deployed model, test set)"):
    tt = pd.DataFrame(deployed["test"]["threshold_table"])
    st.dataframe(tt.style.format({c: "{:.3f}" for c in ["accuracy", "precision", "recall", "f1",
                                                          "predicted_positive_rate"]}),
                 hide_index=True, width="stretch")

# ---------------- Strengths & limitations ----------------
st.subheader("Strengths and limitations of each algorithm")
notes = {
    "Logistic Regression": (
        "Transparent: each coefficient shows how a feature shifts the log-odds of churn. Fast, stable, "
        "and produces reasonably ranked probabilities.",
        "Assumes effects are additive and linear in the log-odds; interactions (e.g. fibre internet × "
        "month-to-month contract) must be added by hand.",
    ),
    "Decision Tree": (
        "Produces human-readable if/then rules and captures interactions automatically.",
        "High variance: small changes in data can change the tree. Probabilities are coarse (one value "
        "per leaf). Usually the weakest of the three on ranking metrics.",
    ),
    "Random Forest": (
        "Averages many trees, reducing variance and capturing non-linear effects and interactions.",
        "Less interpretable (needs permutation importance or similar to explain), larger model file, "
        "slower to train. Gains over Logistic Regression are small on this dataset.",
    ),
}
for name, r in models.items():
    s, l = notes.get(name, ("", ""))
    with st.expander(f"{name}: best hyperparameters {r['best_params']}"):
        st.markdown(f"**Strengths.** {s}\n\n**Limitations.** {l}")
        st.caption(f"{r['n_candidates']} hyperparameter combinations evaluated; tuning took {r['fit_seconds']} s.")
