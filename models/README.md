# Models

Created by `python -m src.train`. Nothing in this folder is edited by hand.

| File | Content |
|---|---|
| `churn_pipeline.joblib` | The deployed, fitted scikit-learn object: `CalibratedClassifierCV` wrapping the full pipeline (type coercion → imputation/scaling/one-hot encoding → Random Forest). Accepts raw feature columns and returns churn probabilities. |
| `model_metadata.json` | Selected algorithm, hyperparameters, decision threshold, feature schema, training ranges, CV and test metrics, data hash, library versions, training timestamp. |

Load and use:

```python
from src.predict import load_model, predict_records
model = load_model()
predictions, warnings = predict_records(model, customers_df)  # validates input first
```

Notes:

- The pickle is tied to the scikit-learn version recorded in the metadata (1.9.1). If you upgrade scikit-learn,
  retrain rather than loading an old file.
- Only load joblib files you created yourself; unpickling untrusted files can execute code.
- File size is about 6.5 MB, compressed (the calibrator keeps five fitted copies of the 300-tree Random Forest
  pipeline, one per internal cross-validation fold).
