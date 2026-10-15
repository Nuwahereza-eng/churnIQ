"""Generate notebooks/exploratory_analysis.ipynb.

The notebook is generated from this script so its structure is version
controlled in readable form. Execute it with:
    jupyter nbconvert --to notebook --execute --inplace notebooks/exploratory_analysis.ipynb
"""

from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell

cells = [
    md("""# Exploratory Data Analysis: IBM Telco Customer Churn

**Project:** Development and Evaluation of a Machine Learning Model for Predicting Customer Churn in the Telecommunications Industry.

This notebook is reproducible: it reads the local CSV (`data/raw/Telco-Customer-Churn.csv`, obtained with
`python scripts/download_data.py`) through the same loading and cleaning code used for model training
(`src/data_loader.py`). Figures are saved to `reports/figures/`.

**Dataset provenance.** The IBM Telco Customer Churn sample describes a *fictional* telecommunications company
providing phone and internet services to 7,043 customers. It is not data from any real company or from the
Ugandan market. All findings below are associations within this sample, not causal effects."""),
    code("""import sys
from pathlib import Path

ROOT = Path.cwd().resolve().parent if Path.cwd().name == "notebooks" else Path.cwd().resolve()
sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.config import FIGURES_DIR, RAW_DATA_PATH
from src.data_loader import check_quality, load_dataset, read_raw_csv
from src.eda import (add_tenure_band, association_with_churn, churn_rate_by,
                     column_summary, highest_churn_groups)
from src.schema import CATEGORICAL_FEATURES, FEATURE_DESCRIPTIONS, NUMERIC_FEATURES

FIGURES_DIR.mkdir(parents=True, exist_ok=True)
BLUE, ORANGE, INK2, GRID = "#2a78d6", "#eb6834", "#52514e", "#e1e0d9"
CHURN_COLORS = {"No": BLUE, "Yes": ORANGE}
plt.rcParams.update({
    "figure.dpi": 110, "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "axes.titlesize": 12, "axes.titleweight": "normal",
})
pd.set_option("display.width", 140)

def save(fig, name):
    fig.savefig(FIGURES_DIR / name, bbox_inches="tight", dpi=150)"""),
    md("## 1. Raw data: dimensions, types and quality checks"),
    code("""raw = read_raw_csv(RAW_DATA_PATH)
print("Shape:", raw.shape)
raw.head()"""),
    code("""quality = check_quality(raw)
pd.Series(quality.to_dict(), name="value").to_frame()"""),
    md("""**Findings.**
- All 21 expected columns are present; no unexpected target or category values.
- `TotalCharges` is stored as text and contains 11 blank values. Every one of them belongs to a customer with
  `tenure = 0`, i.e. a new customer who has not yet been billed, so the blank is set to **0** (not imputed with a
  statistic). Any other missing value would be imputed by the model pipeline using training-data statistics only.
- There are no duplicate customer IDs. A small number of rows are identical apart from `customerID`; they belong to
  different customers with the same attributes and are kept."""),
    code("""raw.loc[raw["TotalCharges"].str.strip() == "", ["customerID", "tenure", "MonthlyCharges", "TotalCharges", "Churn"]]"""),
    code("""df = load_dataset(RAW_DATA_PATH)
column_summary(df, FEATURE_DESCRIPTIONS)"""),
    md("## 2. Target class distribution"),
    code("""counts = df["Churn"].value_counts()
print(counts, "\\n")
print((counts / len(df)).round(4))

fig, ax = plt.subplots(figsize=(6, 2.2))
ax.barh(counts.index, counts.values, color=[CHURN_COLORS[c] for c in counts.index], height=0.55)
for i, (label, v) in enumerate(counts.items()):
    ax.text(v + 60, i, f"{v:,} ({v / len(df):.1%})", va="center", color=INK2)
ax.set_xlabel("Customers"); ax.set_title("Churn vs non-churn customers"); ax.grid(axis="y", visible=False)
ax.set_xlim(0, counts.max() * 1.25)
save(fig, "01_class_distribution.png"); plt.show()"""),
    md("""About 26.5% of customers churned. The classes are **imbalanced**: a model that always predicts "No" would be
about 73% accurate while identifying no churners, so accuracy alone is not a suitable evaluation metric."""),
    md("## 3. Numerical features"),
    code("""df.groupby("Churn")[NUMERIC_FEATURES].describe().T.round(2)"""),
    code("""fig, axes = plt.subplots(1, 3, figsize=(14, 3.6))
for ax, col in zip(axes, NUMERIC_FEATURES):
    for label in ["No", "Yes"]:
        sns.histplot(df.loc[df["Churn"] == label, col], ax=ax, stat="percent", bins=30, element="step",
                     fill=False, color=CHURN_COLORS[label], label=f"Churn = {label}", linewidth=1.8)
    ax.set_title(f"Distribution of {col} by churn"); ax.set_ylabel("% of customers in class")
axes[0].legend(frameon=False)
fig.tight_layout(); save(fig, "02_numeric_distributions.png"); plt.show()"""),
    md("""- **Tenure:** churners are concentrated in the first months; long-tenure customers rarely churn.
- **MonthlyCharges:** churners tend to pay more per month (median about 80 vs 64 for non-churners); very low
  charges (around 20, typically phone-only customers) are dominated by non-churners.
- **TotalCharges:** lower for churners, largely because they have shorter tenure (the two are strongly correlated)."""),
    code("""corr = df[NUMERIC_FEATURES].assign(Churn=(df["Churn"] == "Yes").astype(int)).corr()
fig, ax = plt.subplots(figsize=(5, 4))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1, ax=ax, cbar_kws={"shrink": 0.8})
ax.set_title("Correlation (numeric features and churn indicator)")
save(fig, "03_correlation.png"); plt.show()"""),
    md("""`TotalCharges` is strongly correlated with `tenure` (r ≈ 0.83). This collinearity matters when interpreting
model coefficients or importances: the information in one is largely available in the other."""),
    md("## 4. Categorical features and churn rates"),
    code("""data = add_tenure_band(df)
groups = ["Contract", "tenure_band", "InternetService", "PaymentMethod", "OnlineSecurity", "TechSupport",
          "PaperlessBilling", "SeniorCitizen", "Partner", "Dependents", "gender", "PhoneService"]
overall = (df["Churn"] == "Yes").mean()
fig, axes = plt.subplots(4, 3, figsize=(15, 13))
for ax, col in zip(axes.ravel(), groups):
    t = churn_rate_by(data, col)
    ax.barh(t["group"].astype(str), t["churn_rate"], color=BLUE, height=0.6)
    ax.axvline(overall, color="#898781", linestyle="--", linewidth=1)
    for y, (r, n) in enumerate(zip(t["churn_rate"], t["customers"])):
        ax.text(r + 0.01, y, f"{r:.0%} (n={n:,})", va="center", fontsize=8, color=INK2)
    ax.set_xlim(0, 0.8); ax.set_title(col); ax.grid(axis="y", visible=False)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
fig.suptitle("Churn rate by customer group (dashed line = overall churn rate)", y=1.0)
fig.tight_layout(); save(fig, "04_churn_rate_by_group.png"); plt.show()"""),
    code("""highest_churn_groups(df, min_customers=200, top=10)"""),
    md("""**Observed patterns (associations, not causes):**
- Month-to-month contracts have much higher churn (~43%) than one-year (~11%) and two-year (~3%) contracts.
- Customers in their first six months churn at over 50%.
- Fibre-optic internet customers churn more (~42%) than DSL customers (~19%); fibre customers also pay higher
  monthly charges, so the two cannot be separated here.
- Electronic-check payers churn at ~45%, far above automatic payment methods (~15–17%).
- Customers without online security or technical support churn at ~42%.
- Gender and phone service show essentially no difference in churn rate."""),
    md("## 5. Strength of association with churn"),
    code("""assoc = association_with_churn(df)
assoc.style.format({"strength": "{:.3f}", "p_value": "{:.2e}"})"""),
    code("""fig, ax = plt.subplots(figsize=(7, 6))
a = assoc.assign(abs_strength=assoc["strength"].abs()).sort_values("abs_strength")
ax.barh(a["feature"], a["abs_strength"], color=BLUE, height=0.6)
ax.set_xlabel("|Cramér's V| (categorical) or |point-biserial r| (numeric)")
ax.set_title("Bivariate association with churn"); ax.grid(axis="y", visible=False)
save(fig, "05_association.png"); plt.show()"""),
    md("""Contract type, tenure, online security, technical support, internet service and payment method show the
strongest bivariate associations with churn; gender and phone service show none. Note that p-values are tiny for
most features because the sample is large; effect size (the strength measure) is more informative than
significance here. Bivariate measures do not account for overlaps between features (for example, month-to-month
customers also tend to have short tenure).

## 6. Implications for modelling

1. `customerID` is an identifier with no predictive meaning and is excluded.
2. Blank `TotalCharges` → 0 for tenure-0 customers; median imputation inside the pipeline as a safeguard.
3. Numeric features are standardised (needed for Logistic Regression), categoricals one-hot encoded.
4. Class imbalance (26.5% churn) is handled with class weighting and evaluated with recall, precision, F1,
   ROC-AUC and precision–recall curves rather than accuracy alone.
5. Correlated features (tenure / TotalCharges) call for care when interpreting importances."""),
]

nb = nbf.v4.new_notebook()
nb["cells"] = cells
nb["metadata"]["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
out = ROOT / "notebooks" / "exploratory_analysis.ipynb"
out.parent.mkdir(exist_ok=True)
nbf.write(nb, out)
print(f"Wrote {out.relative_to(ROOT)}")
