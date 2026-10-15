# Research Documentation

**Title:** Development and Evaluation of a Machine Learning Model for Predicting Customer Churn in the
Telecommunications Industry

**Type:** Undergraduate Software Engineering research project with a functional web application.

This document records what was actually implemented and measured. All numerical results are taken from
`reports/evaluation_results.json`, produced by `python -m src.train` on 2026-10-15 (Python 3.12.3,
scikit-learn 1.9.1, random seed 42). Items marked *future work* were **not** implemented.

---

## 1. Background and problem statement

Telecommunications subscribers can usually move to another provider with little cost, so operators lose revenue
when customers discontinue their services ("churn"). If customers likely to leave can be identified early, a
retention team can prioritise contact or offers. Historical customer records contain account, service and
demographic information that may be associated with churn.

**Problem.** Can machine-learning classifiers, trained on historical customer information, estimate which customers
are likely to churn well enough to support retention decisions, and which algorithm is most suitable?

## 2. Objectives and research questions

**General objective.** To develop and evaluate a machine-learning model for predicting customer churn in the
telecommunications industry.

| # | Specific objective | Where addressed |
|---|---|---|
| 1 | Analyse customer data to identify characteristics associated with churn | §6, notebook, Data Exploration page |
| 2 | Develop machine-learning models for predicting churn | §7, `src/train.py` |
| 3 | Compare selected algorithms using appropriate evaluation metrics | §8–9, Model Performance page |
| 4 | Develop a web application presenting predictions and churn patterns | §10, Streamlit app |

**Research questions.**

- RQ1. Which customer characteristics are most strongly associated with churn in the dataset?
- RQ2. How well do Logistic Regression, Decision Tree and Random Forest classifiers predict churn on unseen customers?
- RQ3. Which algorithm offers the best balance of predictive performance, reliability of probabilities and interpretability?
- RQ4. How does the choice of decision threshold affect the trade-off between finding churners and false alarms?

## 3. Dataset

**Source.** IBM Telco Customer Churn sample (`Telco-Customer-Churn.csv`), from the public GitHub repository
[IBM/telco-customer-churn-on-icp4d](https://github.com/IBM/telco-customer-churn-on-icp4d).
It describes a **fictional** telecom provider offering phone and internet services in a US-style market. It is not
data about Ugandan telecom customers or any real operator, which limits how far findings generalise (§12).

**Size and variables.** 7,043 customers, 21 columns: an identifier (`customerID`), 19 candidate features
(3 numeric: `tenure`, `MonthlyCharges`, `TotalCharges`; 1 binary: `SeniorCitizen`; 15 categorical service, account and
demographic fields) and the binary target `Churn` (left within the last month). Full variable list: `data/README.md`.

**Target distribution.** 1,869 churners (26.5%) and 5,174 non-churners (73.5%): moderately imbalanced.

**Quality findings.**

| Check | Finding | Decision |
|---|---|---|
| Missing values | 11 blank `TotalCharges` strings; no other missing values | All 11 have `tenure = 0` (not yet billed), so set to 0 |
| Data types | `TotalCharges` stored as text | Converted to numeric |
| Duplicate IDs / rows | None | – |
| Identical apart from ID | 22 rows | Kept: they are distinct customers |
| Unexpected categories / target values | None | Loader rejects such values if they appear |

## 4. Literature review planning

The literature review is to be written by the researcher. The plan below lists themes and starting references.
**Every reference must be checked against the original publication before it is cited**; the list was compiled
from general knowledge and has not been verified against library databases as part of this work, and no claim about
a research gap is made here.

**Themes and search strategy.**

1. Customer churn and retention economics in telecommunications.
2. Churn prediction with machine learning (logistic regression, decision trees, ensembles, boosting, neural networks).
3. Class imbalance in classification and appropriate metrics (precision–recall vs ROC).
4. Probability calibration and decision thresholds for cost-sensitive decisions.
5. Model interpretability (coefficients, permutation importance) and the limits of causal interpretation.
6. Ethics of predictive analytics on customer data; data-protection law (e.g. Uganda's Data Protection and Privacy
   Act, 2019) for any future use of local data.
7. Studies on churn in African / Ugandan mobile markets, to position the work and identify transferability issues.

Suggested sources: Google Scholar, IEEE Xplore, ScienceDirect, ACM Digital Library, SpringerLink; search terms such as
"telecom churn prediction", "customer churn machine learning", "imbalanced classification precision recall",
"probability calibration classifier", "churn prediction Africa mobile".

**Starting references (methods; verify before citing).**

- Breiman, L. (2001). Random forests. *Machine Learning*, 45(1), 5–32.
- Breiman, L., Friedman, J., Olshen, R., & Stone, C. (1984). *Classification and Regression Trees*. Wadsworth.
- Hosmer, D. W., Lemeshow, S., & Sturdivant, R. X. (2013). *Applied Logistic Regression* (3rd ed.). Wiley.
- Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830.
- Platt, J. (1999). Probabilistic outputs for support vector machines and comparisons to regularized likelihood
  methods. In *Advances in Large Margin Classifiers*. MIT Press.
- Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. *Proceedings of ICML 2005*.
- Saito, T., & Rehmsmeier, M. (2015). The precision-recall plot is more informative than the ROC plot when evaluating
  binary classifiers on imbalanced datasets. *PLoS ONE*, 10(3), e0118432.
- Brier, G. W. (1950). Verification of forecasts expressed in terms of probability. *Monthly Weather Review*, 78(1), 1–3.
- Strobl, C., Boulesteix, A.-L., Zeileis, A., & Hothorn, T. (2007). Bias in random forest variable importance
  measures. *BMC Bioinformatics*, 8, 25.
- Bergsma, W. (2013). A bias-correction for Cramér's V and Tschuprow's T. *Journal of the Korean Statistical Society*, 42(3), 323–328.
- Verbeke, W., Dejaeger, K., Martens, D., Hur, J., & Baesens, B. (2012). New insights into churn prediction in the
  telecommunication sector: A profit driven data mining approach. *European Journal of Operational Research*, 218(1), 211–229.

## 5. Research methodology

**Approach.** Quantitative, experimental. Supervised binary classification on a public secondary dataset, combined
with design-science style development of a software artefact (the web application) and its verification by
automated tests.

**Process.**

1. Data acquisition (`src/data_acquisition.py`), kept separate from training.
2. Data validation and cleaning (`src/data_loader.py`).
3. Exploratory data analysis (`notebooks/exploratory_analysis.ipynb`, `src/eda.py`).
4. Preprocessing pipeline and model development (`src/preprocessing.py`, `src/train.py`).
5. Evaluation on a held-out test set (`src/evaluate.py`).
6. Application development (Streamlit) and automated testing (pytest).

**Tools.** Python 3.12, pandas, NumPy, SciPy, scikit-learn, matplotlib/seaborn, Altair, Jupyter, Streamlit,
joblib, pytest, Git.

## 6. Exploratory analysis (RQ1)

Churn rates by group (all customers; overall 26.5%):

| Characteristic | Group | Customers | Churn rate |
|---|---|---|---|
| Contract | Month-to-month | 3,875 | 42.7% |
| | One year | 1,473 | 11.3% |
| | Two year | 1,695 | 2.8% |
| Tenure (months) | 0–6 | 1,481 | 52.9% |
| | 49–72 | 2,239 | 9.5% |
| Internet service | Fiber optic | 3,096 | 41.9% |
| | DSL | 2,421 | 19.0% |
| | None | 1,526 | 7.4% |
| Payment method | Electronic check | 2,365 | 45.3% |
| | Credit card (automatic) | 1,522 | 15.2% |
| Online security | No | 3,498 | 41.8% |
| Technical support | No | 3,473 | 41.6% |
| Senior citizen | Yes | 1,142 | 41.7% |

Strength of bivariate association with churn (bias-corrected Cramér's V for categorical features, point-biserial r for
numeric): Contract 0.410, tenure −0.352, OnlineSecurity 0.347, TechSupport 0.343, InternetService 0.322,
PaymentMethod 0.303; gender 0.000 and PhoneService 0.001 show no association.

`tenure` and `TotalCharges` are strongly correlated (r = 0.826), so their individual effects are hard to separate.

**Answer to RQ1.** Short tenure, month-to-month contracts, fibre-optic internet, electronic-check payment and the
absence of security/support add-ons are the characteristics most associated with churn in this dataset. These are
associations; the data cannot show that any of them causes churn, and several overlap (new customers are mostly on
month-to-month contracts).

## 7. Data preparation and experimental design

**Features.** The 19 candidate features; `customerID` excluded (an arbitrary identifier with no meaning beyond the
record, whose use would risk memorisation and privacy issues).

**Preprocessing (scikit-learn `Pipeline` + `ColumnTransformer`).**

| Feature group | Steps | Reason |
|---|---|---|
| Numeric (tenure, MonthlyCharges, TotalCharges) | Median imputation → standardisation | Median is robust to skew; scaling needed by Logistic Regression, harmless for trees |
| SeniorCitizen (0/1) | Most-frequent imputation | Already numeric binary |
| 15 categorical | Most-frequent imputation → one-hot encoding (`handle_unknown="ignore"`) | Nominal categories without order; unseen categories encode to all zeros instead of failing |

A first pipeline step enforces column selection, order and data types, so exactly the same transformation is applied
at training and prediction time. All learned statistics (medians, means/SDs, category lists) are fitted inside the
pipeline, so during cross-validation they are learned from training folds only: **no leakage** from validation or
test data. (Test `test_imputer_learns_from_training_data_only` checks this.)

**Split.** Stratified 80/20 train/test split (5,634 / 1,409 customers; churn rate 26.5% in both), seed 42.
The test set was used once, for final evaluation only.

**Class imbalance.** All three models use `class_weight="balanced"`, which weights errors on the minority class more
heavily during training. This was preferred to resampling (e.g. SMOTE) because it creates no synthetic customers and
integrates cleanly with cross-validation. Its side effect, inflated probabilities, is corrected by calibration (below).

**Hyperparameter tuning.** Grid search with stratified 5-fold cross-validation on the training set, scoring ROC-AUC
(threshold-independent ranking quality). Grids were widened after an initial run in which the best values lay on grid
edges; the final best values are interior.

| Model | Grid | Candidates | Best |
|---|---|---|---|
| Logistic Regression | C ∈ {0.001 … 100} (11 values) | 11 | C = 10 |
| Decision Tree | max_depth ∈ {3,4,5,6,8,10,None} × min_samples_leaf ∈ {1,10,25,50,100,150,250} | 49 | depth 8, min leaf 100 |
| Random Forest (300 trees) | max_depth ∈ {6,10,14,None} × min_samples_leaf ∈ {5,10,20,40,80} × max_features ∈ {sqrt, 0.5} | 40 | depth 10, min leaf 20, sqrt |

**Model selection.** The final algorithm is the one with the highest **mean cross-validated ROC-AUC on the training
set**. Selecting on the test set would bias the reported results.

**Calibration and threshold.** The selected pipeline is wrapped in sigmoid (Platt) calibration with 5-fold internal
cross-validation on the training set. The decision threshold is the value maximising F1 on out-of-fold calibrated
predictions for the training set. Neither step uses the test set.

## 8. Algorithms

- **Logistic Regression** models the log-odds of churn as a linear combination of features. Interpretable baseline;
  coefficients indicate direction and size of association, conditional on other features.
- **Decision Tree** recursively splits customers into groups using if/then rules (CART). Readable and captures
  interactions, but unstable (high variance).
- **Random Forest** averages many decorrelated trees trained on bootstrap samples with random feature subsets,
  reducing variance and capturing non-linear effects; less interpretable.

## 9. Evaluation metrics

| Metric | Meaning in churn terms |
|---|---|
| Accuracy | Share of all customers classified correctly; misleading under imbalance |
| Precision | Of customers flagged as churners, the share who did churn (cost of wasted retention effort) |
| Recall | Of actual churners, the share the model flagged (churners reached) |
| F1 | Harmonic mean of precision and recall |
| ROC-AUC | Probability that a random churner gets a higher score than a random non-churner; threshold-independent |
| Average precision (PR-AUC) | Summary of the precision–recall curve; informative for the minority class (baseline = churn rate 0.265) |
| Brier score | Mean squared error of probabilities; measures calibration and sharpness (lower is better) |
| Confusion matrix | Counts of true/false positives/negatives |

**False positives vs false negatives.** A *false positive* is a loyal customer flagged as a churn risk: the cost is an
unnecessary contact or discount. A *false negative* is a churner the model misses: the cost is the lost customer's
future revenue. Because a missed churner usually costs more than an unneeded offer, recall is prioritised, but the
right balance depends on the actual cost of the retention action, which this dataset does not provide.

## 10. Results (RQ2–RQ4)

### 10.1 Algorithm comparison (held-out test set, threshold 0.5)

| Model | CV ROC-AUC | CV F1 | Accuracy | Precision | Recall | F1 | ROC-AUC | Avg. precision | Brier | TP / FP / FN / TN |
|---|---|---|---|---|---|---|---|---|---|---|
| Logistic Regression | 0.846 ± 0.013 | 0.627 | 0.739 | 0.505 | 0.783 | 0.614 | 0.841 | 0.627 | 0.169 | 293 / 287 / 81 / 748 |
| Decision Tree | 0.833 ± 0.013 | 0.611 | 0.739 | 0.505 | 0.781 | 0.613 | 0.836 | 0.615 | 0.168 | 292 / 286 / 82 / 749 |
| Random Forest | 0.848 ± 0.009 | 0.631 | 0.752 | 0.521 | 0.789 | 0.628 | 0.844 | 0.651 | 0.163 | 295 / 271 / 79 / 764 |
| Majority-class baseline | – | – | 0.735 | 0.000 | 0.000 | 0.000 | 0.500 | 0.265 | 0.195 | 0 / 0 / 374 / 1,035 |

Figures: `reports/figures/06_roc_pr_curves.png`, `07_metric_comparison.png`, `08_confusion_matrices.png`.

### 10.2 Deployed model

Random Forest had the highest mean CV ROC-AUC and was selected. Class weighting made its probabilities too high: the
mean predicted probability on the test set was 41.3% against an observed churn rate of 26.5%. After sigmoid
calibration, the mean prediction was 26.7%, and the Brier score fell from **0.163 to 0.136**
(`09_threshold_calibration.png`). The F1-optimal threshold on out-of-fold training predictions was **0.36**.

| Deployed model (test set) | Accuracy | Precision | Recall | F1 | ROC-AUC | Avg. precision | Brier | TP / FP / FN / TN |
|---|---|---|---|---|---|---|---|---|
| Calibrated Random Forest, threshold 0.36 | 0.785 | 0.577 | 0.714 | 0.638 | 0.845 | 0.651 | 0.136 | 267 / 196 / 107 / 839 |

### 10.3 Effect of the threshold (deployed model, test set; RQ4)

| Threshold | Precision | Recall | F1 | Share of customers flagged |
|---|---|---|---|---|
| 0.20 | 0.488 | 0.842 | 0.618 | 45.9% |
| 0.30 | 0.541 | 0.770 | 0.636 | 37.8% |
| 0.36 (deployed) | 0.577 | 0.714 | 0.638 | 32.9% |
| 0.40 | 0.580 | 0.671 | 0.622 | 30.7% |
| 0.50 | 0.653 | 0.559 | 0.602 | 22.7% |
| 0.60 | 0.693 | 0.398 | 0.506 | 15.3% |

Lowering the threshold finds more churners at the cost of more false alarms. A retention team with a cheap action
(e.g. an email) can use a low threshold; an expensive action (e.g. a large discount) justifies a higher one.

### 10.4 Model interpretation

Permutation importance of the deployed model on the test set (mean drop in ROC-AUC when one column is shuffled):
Contract 0.064, tenure 0.023, InternetService 0.015, TotalCharges 0.013, OnlineSecurity 0.005, TechSupport 0.004;
all other features below 0.003 (`10_permutation_importance.png`). Logistic Regression's largest standardised
coefficients involve MonthlyCharges (−2.07), InternetService = Fiber optic (+1.37), tenure (−1.19) and contract type;
the negative MonthlyCharges coefficient alongside the positive fibre coefficient reflects collinearity between charges
and service type, and should not be read as "higher charges reduce churn".

## 11. Discussion

- **RQ2.** All three models clearly outperform the majority-class baseline (ROC-AUC 0.84 vs 0.50; recall ≈ 0.78 vs 0),
  ranking customers by churn risk reasonably well. Precision around 0.5–0.58 means roughly half of the flagged
  customers would not have churned, which is typical for this problem and acceptable only when the retention action is
  inexpensive.
- **RQ3.** Random Forest achieved the best scores on every test metric, but the margins over Logistic Regression are
  small (CV ROC-AUC 0.848 vs 0.846, a difference smaller than one fold standard deviation). The two should be regarded
  as performing similarly on this data. Logistic Regression is simpler and more transparent; Random Forest was retained
  because the pre-specified selection rule chose it and calibration made its probabilities reliable. The Decision Tree
  was slightly weaker and, as expected, less stable.
- **Calibration** was essential: with class weighting, uncalibrated scores overstated churn risk by about 15
  percentage points on average. Displaying such scores as "probabilities" would have misled users.
- **Consistency with the EDA.** The model relies most on contract type, tenure and internet service, the same
  characteristics that showed the strongest associations in §6.
- **Probability vs outcome.** A predicted probability of 0.6 means that, among customers like this one, about 60%
  churned in the historical data. It does not mean this specific customer will leave, and it does not account for
  factors absent from the data.

## 12. Limitations

- **Fictional, single-provider data.** Results do not describe real customers or the Ugandan market; local deployment
  would need local data, retraining and re-validation.
- **No time dimension.** One snapshot; the model cannot capture when customers churn or changes over time, and the
  held-out test is not a future time period.
- **Missing drivers.** Network quality, complaints, competitor offers and service interactions are absent.
- **Costs unknown.** The threshold was chosen by F1, not by actual retention costs and customer value.
- **Associations only.** Neither EDA nor importance measures establish causation.
- **Single split.** Test metrics come from one split of 1,409 customers; small differences between models are within
  sampling variability.
- **Limited model set.** Gradient boosting and other algorithms were not evaluated (future work).

## 13. Ethical considerations

- No personal data was collected; the dataset is public and fictional. The identifier is excluded from modelling.
- `gender` and `SeniorCitizen` are protected or sensitive attributes. They carry little weight in the deployed model
  (permutation importance < 0.003), but any real deployment should review whether they should be used at all and test
  for differences in error rates across groups.
- Predictions are decision support. The application states this on every prediction page and never recommends
  penalising customers predicted to churn (e.g. withholding service or raising prices).
- False positives and negatives have consequences for customers and the business (§9); human review is advised.
- Uploaded files are validated, processed in memory and not stored; error messages do not expose file paths or stack
  traces.
- Real-world use in Uganda would have to comply with the Data Protection and Privacy Act, 2019, including a lawful
  basis and transparency for profiling.

## 14. Implemented software

| Requirement | Implementation |
|---|---|
| Home / overview | `app_pages/0_Home.py`: purpose, dataset and model summary, verified test metrics, limitations |
| Data exploration | `app_pages/1_Data_Exploration.py`: quality checks, column summary, distributions, churn rates, associations, filterable data |
| Single prediction | `app_pages/2_Predict_Churn.py`: validated form, probability, class, risk band, adjustable threshold, contract scenario comparison |
| Batch prediction | `app_pages/3_Batch_Prediction.py`: CSV upload, schema and value validation with row-level errors, downloadable results preserving original columns |
| Model performance | `app_pages/4_Model_Performance.py`: comparison table, ROC/PR curves, confusion matrices, classification reports, threshold analysis, calibration |
| Insights | `app_pages/5_Insights.py`: highest-churn groups, permutation importance, coefficients, responsible-use guidance |
| Testing | 57 pytest tests (see README), all passing at the time of writing |

## 15. Conclusions and future work

A reproducible pipeline was built that trains, compares and calibrates three classifiers on the IBM Telco Customer
Churn data. On held-out customers, the deployed calibrated Random Forest reaches ROC-AUC 0.845 and identifies 71% of
churners at a threshold of 0.36, with about 58% of flagged customers being actual churners. Logistic Regression
performs almost as well and remains an attractive, transparent alternative. Contract type, tenure and internet service
are the dominant predictors. A Streamlit application makes the analysis, predictions and their limitations accessible
to non-technical users.

**Future work (not implemented):**

1. Evaluate gradient boosting (e.g. `HistGradientBoostingClassifier`) and compare with repeated cross-validation or
   statistical tests of model differences.
2. Cost-sensitive threshold selection using realistic retention costs and customer lifetime value.
3. Validation on real, time-stamped data from a Ugandan operator (with appropriate data-protection approval), with
   out-of-time testing.
4. Fairness analysis of error rates across demographic groups.
5. Per-customer explanations (e.g. SHAP) for the deployed model.
6. Monitoring for data drift and periodic retraining once deployed.
