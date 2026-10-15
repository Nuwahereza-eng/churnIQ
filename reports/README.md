# Reports

| File | Created by | Content |
|---|---|---|
| `evaluation_results.json` | `python -m src.train` | All experimental results: data-quality report, best hyperparameters and CV scores for each model, test-set metrics, confusion matrices, classification reports, ROC/PR/calibration curves, threshold tables, deployed (calibrated) model results, majority-class baseline, permutation and model-specific importances. |
| `training_log.txt` | redirected output of training | Console log of the last training run. |
| `figures/01–05_*.png` | `notebooks/exploratory_analysis.ipynb` | EDA figures: class distribution, numeric distributions, correlation, churn rate by group, associations. |
| `figures/06–10_*.png` | `python scripts/make_figures.py` | ROC/PR curves, metric comparison, confusion matrices, threshold and calibration, permutation importance. |

All values are produced by code from the dataset; none are typed in by hand. Re-running training and the figure
script regenerates everything.
