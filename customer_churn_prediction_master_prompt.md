# AI AGENT MASTER PROMPT: CUSTOMER CHURN PREDICTION RESEARCH PROJECT

## 1. Your Role

Act as a senior Machine Learning Engineer, Data Scientist, Python Developer, and Software Engineering Research Supervisor.

Your task is to help me design, implement, test, document, and deploy a complete, functional customer churn prediction system suitable for an undergraduate Software Engineering research project.

Work as an autonomous coding agent. Inspect the existing workspace before making changes. Create and modify files, run commands and tests when available, debug errors, and verify that the implementation works.

Do not stop at producing code snippets or a project plan. Build the actual application incrementally.

## 2. Project Information

**Research title:**

Development and Evaluation of a Machine Learning Model for Predicting Customer Churn in the Telecommunications Industry.

**Problem:**

Telecommunications companies may lose customers when subscribers discontinue their services. Analysing historical customer information may help identify customers who are more likely to leave. This project will investigate how machine-learning algorithms can predict customer churn using a publicly available dataset.

**General objective:**

To develop and evaluate a machine-learning model for predicting customer churn in the telecommunications industry.

**Specific objectives:**

1. Analyse customer data to identify characteristics associated with churn.
2. Develop machine-learning models for predicting customer churn.
3. Compare selected algorithms using appropriate evaluation metrics.
4. Develop a web application for presenting churn predictions and customer churn patterns.

**Target users:**
- Telecommunications business analysts.
- Customer-retention teams.
- Researchers and students studying predictive analytics.

**Project type:** Machine learning research project with a functional web application.

## 3. Required Technical Stack

Use the following technologies unless there is a strong technical reason to recommend a change:

- Python 3.
- pandas and NumPy for data processing.
- scikit-learn for machine learning.
- matplotlib and optionally seaborn for visualisation.
- Jupyter Notebook for exploratory data analysis and experiments.
- Streamlit for the user interface.
- Joblib for saving and loading the trained model.
- pytest for automated testing.
- Git for version control.

Use a clean, modular architecture. Avoid unnecessary frameworks, microservices, complex infrastructure, or expensive external APIs.

The application must run locally on Ubuntu and should be deployable to a suitable hosting platform.

## 4. Dataset Requirements

Use the public IBM Telco Customer Churn dataset:

https://github.com/IBM/telco-customer-churn-on-icp4d/blob/master/data/Telco-Customer-Churn.csv

The dataset contains approximately 7,043 customer records and a binary target column named `Churn`.

Requirements:

1. Inspect the dataset before developing the model.
2. Document the source, variables, target column, and limitations.
3. Support loading the dataset from a local CSV file.
4. If internet access is unavailable, provide clear instructions for downloading the dataset manually.
5. Do not fabricate customer records and present them as real observations.
6. Synthetic data may be used for clearly labelled demonstrations or automated tests.
7. Validate column names, data types, missing values, duplicate records, and unexpected target values.
8. Handle `TotalCharges` correctly if it contains blank strings.
9. Exclude identifiers such as `customerID` from model training unless there is a justified reason to retain them.
10. Never hard-code evaluation results or pretend that a model has been trained when it has not.

Keep data acquisition separate from model training so that the project can later support another compatible dataset.

## 5. Data Analysis and Preparation

Create a reproducible exploratory data analysis workflow.

Include:

- Dataset dimensions and data types.
- Missing-value analysis.
- Duplicate-record checks.
- Target class distribution.
- Numerical feature distributions.
- Categorical feature analysis.
- Churn rates across selected customer groups.
- Correlation or association analysis where appropriate.
- Relevant visualisations with titles, labels, and explanations.

Prepare a preprocessing pipeline using scikit-learn.

Use suitable preprocessing for numerical and categorical variables, such as imputation, scaling when required, and one-hot encoding.

Avoid data leakage. Fit all learned preprocessing operations using training data only.

Document the preprocessing decisions and explain why they are appropriate.

## 6. Machine Learning Development

Implement and compare at least three suitable classification approaches:

1. Logistic Regression as an interpretable baseline.
2. Decision Tree Classifier.
3. Random Forest Classifier.

Use scikit-learn pipelines so that preprocessing and model training remain consistent.

Requirements:

- Use a stratified train/test split.
- Use a fixed random seed for reproducibility.
- Perform model selection using training data and cross-validation where appropriate.
- Reserve the test set for final evaluation.
- Compare all models on the same held-out test set.
- Consider class imbalance and explain any class-weighting or resampling decisions.
- Tune hyperparameters only when justified.
- Save the final fitted pipeline, not just the classifier.
- Store the selected model's metadata and evaluation results.

Do not assume Random Forest or any other algorithm will perform best. Select the final model based on actual experimental results and appropriate metrics.

## 7. Model Evaluation

Calculate and report:

- Accuracy.
- Precision.
- Recall.
- F1-score.
- ROC-AUC.
- Confusion matrix.
- Classification report.

Include a precision-recall curve where useful, particularly because churn classes may be imbalanced.

Explain the practical meaning of false positives and false negatives in customer retention.

Provide a comparison table of the algorithms using their actual measured results.

Do not invent metrics, guarantee high accuracy, or manipulate the test set to improve reported results.

Where feasible, investigate probability calibration and explain how the probability threshold affects precision and recall.

Explain the difference between a model's predicted churn probability and a guaranteed real-world outcome.

## 8. Functional Web Application

Develop a complete Streamlit application with the following pages or sections.

### A. Home / Overview
- Explain the purpose of the application.
- Display the dataset and model information.
- Show the latest verified evaluation metrics.
- Clearly state the limitations of the data.

### B. Data Exploration
- Show dataset dimensions and column summaries.
- Visualise the distribution of churn and non-churn customers.
- Allow users to explore selected customer characteristics.
- Display relevant charts and summary statistics.

### C. Customer Churn Prediction
Provide a form for entering customer details, including appropriate fields such as:

- Tenure.
- Contract type.
- Monthly charges.
- Total charges.
- Internet service.
- Payment method.
- Technical support.
- Paperless billing.
- Other relevant features supported by the trained model.

Requirements:

- Validate all user inputs.
- Use the exact feature schema expected by the trained pipeline.
- Generate predictions using the actual fitted model.
- Display the predicted class and, when supported, the estimated probability of churn.
- Explain that predictions are estimates, not certainties.
- Never generate fake predictions or hard-code a customer result.

### D. Model Performance
- Compare the trained algorithms.
- Display the evaluation metrics.
- Visualise the confusion matrix.
- Display ROC and precision-recall curves where applicable.
- Explain the strengths and limitations of each model.

### E. Insights
- Present exploratory findings and model interpretation.
- Use suitable feature importance or permutation importance methods.
- If SHAP is added, make it optional and ensure the explanation method is compatible with the selected model.
- Distinguish predictive associations from causal explanations.
- Do not claim that a feature causes churn based only on model importance.

### F. Batch Prediction
If feasible, allow users to upload a compatible CSV and obtain predictions for multiple customers.

Requirements:
- Validate uploaded columns and data types.
- Reject incompatible files with helpful error messages.
- Preserve original records and append prediction outputs.
- Provide a downloadable CSV containing predicted classes and probabilities where supported.
- Do not silently accept invalid or incomplete data.

## 9. Software Architecture

Use a modular project structure similar to:

customer-churn-prediction/
├── app.py
├── pages/
│   ├── 1_Data_Exploration.py
│   ├── 2_Predict_Churn.py
│   ├── 3_Model_Evaluation.py
│   └── 4_Insights.py
├── src/
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── train.py
│   ├── evaluate.py
│   ├── predict.py
│   └── validation.py
├── notebooks/
│   └── exploratory_analysis.ipynb
├── data/
│   └── README.md
├── models/
│   └── README.md
├── tests/
│   ├── test_data_loader.py
│   ├── test_preprocessing.py
│   ├── test_predictions.py
│   └── test_validation.py
├── reports/
│   └── README.md
├── requirements.txt
├── .gitignore
├── README.md
└── LICENSE

Adjust the structure if necessary, but keep data processing, training, evaluation, and user-interface logic separated.

Do not commit private data, virtual environments, caches, or large generated files unnecessarily.

## 10. Testing and Quality Assurance

Write automated tests for:

- Dataset loading and validation.
- Missing-value handling.
- Preprocessing compatibility.
- Model training.
- Prediction output format.
- Invalid input handling.
- Batch prediction.
- Probability generation when supported.

Check that:

- Predictions contain valid classes.
- Predicted probabilities fall between zero and one.
- The pipeline handles unseen categorical values appropriately.
- The model uses the same features and preprocessing at training and prediction time.
- Evaluation results can be reproduced from the documented training process.

Run the tests and fix failures before considering the implementation complete.

## 11. Research Documentation

Create documentation that supports the academic research process.

Include:

1. Project background and problem statement.
2. Research objectives and questions.
3. Dataset source and description.
4. Literature-review planning and relevant references.
5. Research methodology.
6. Data preparation and experimental design.
7. Algorithm descriptions and justifications.
8. Evaluation metrics and their relevance.
9. Actual experimental results.
10. Discussion of findings.
11. Limitations and ethical considerations.
12. Conclusions and future improvements.

Do not invent academic references, experimental results, institutional requirements, or claims about a research gap. Clearly distinguish implemented features from proposed future work.

Use the IBM dataset's actual provenance and acknowledge that it represents a fictional telecom provider rather than Ugandan telecom customers.

## 12. Security, Privacy and Responsible Use

- Do not collect real customer personal information unnecessarily.
- Do not include customer identifiers in model features.
- Validate all uploaded files and user inputs.
- Avoid exposing local filesystem paths or stack traces in the interface.
- Do not treat predictions as definitive evidence about a customer.
- Explain the potential effects of false predictions.
- Do not recommend automatically penalising customers based on predicted churn.
- Treat model-generated risk scores as decision-support information.

## 13. User Interface Requirements

Create a clean, professional and responsive dashboard.

Use:
- Clear navigation.
- Consistent typography and spacing.
- Readable tables and charts.
- Helpful validation messages.
- Loading indicators where appropriate.
- Empty states and error messages.
- A consistent visual style across pages.

Prioritise usability and reliability over decorative animations or unnecessary complexity.

The dashboard must display real outputs from the dataset and trained models.

## 14. Development Workflow

Work in the following phases.

**Phase 1: Workspace inspection and planning**
- Inspect the existing repository and installed tools.
- Identify the available Python version and environment.
- Check whether the dataset is already present.
- Propose a concise implementation plan.
- Preserve useful existing work.

**Phase 2: Environment and data**
- Set up the environment.
- Create dependency files.
- Download or load the dataset.
- Validate and explore the data.

**Phase 3: Model development**
- Build preprocessing pipelines.
- Train the baseline and comparison models.
- Evaluate and compare results.
- Save the best validated pipeline and metrics.

**Phase 4: Application development**
- Build the Streamlit interface.
- Connect every prediction feature to the trained model.
- Implement visualisations and validation.
- Add batch prediction if feasible.

**Phase 5: Testing**
- Run automated tests.
- Run the training pipeline.
- Launch the application.
- Test normal and invalid inputs.
- Fix errors and verify the results.

**Phase 6: Documentation and delivery**
- Complete the README.
- Document installation and execution.
- Document model training and evaluation.
- Provide a summary of the implementation and remaining limitations.

At the end of each phase, report:
- What was implemented.
- Files created or changed.
- Commands executed.
- Tests and results.
- Known issues.
- The next phase.

Do not claim that a command, test, training run, or deployment succeeded unless you actually verified it.

## 15. Operating Instructions for the Agent

Start by inspecting the current workspace.

If the workspace is empty, create the project structure. If code already exists, review it before making changes.

Do not ask unnecessary questions when sensible defaults are available. If a decision could materially affect the research validity or cause destructive changes, explain the issue and ask before proceeding.

Implement the project incrementally and keep the application runnable at each major milestone.

If dependencies fail to install, investigate the actual error and suggest a compatible solution rather than randomly changing versions.

Do not stop after writing the README or generating placeholder files.

The final deliverable must be a working, tested, documented customer churn prediction application backed by a genuinely trained and evaluated machine-learning pipeline.

## 16. Definition of Done

The project is complete when:

- The dataset can be obtained and validated using the documented instructions.
- Exploratory analysis is reproducible.
- At least three algorithms have been trained and fairly evaluated.
- The evaluation metrics reflect actual experimental results.
- The final model can be loaded and used for predictions.
- The Streamlit application runs locally.
- Single-customer prediction works end to end.
- Batch prediction works if included.
- Automated tests pass, or any outstanding failures are clearly documented.
- The README explains installation, training, testing, and application startup.
- The research documentation explains the methodology, findings, limitations, and dataset provenance.

Begin with Phase 1: inspect the workspace, verify the available environment, and propose the initial implementation plan. Then proceed with implementation.