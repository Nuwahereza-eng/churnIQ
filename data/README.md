# Data

## Source

**IBM Telco Customer Churn** sample dataset, published by IBM in the repository
[IBM/telco-customer-churn-on-icp4d](https://github.com/IBM/telco-customer-churn-on-icp4d)
(file `data/Telco-Customer-Churn.csv`). It describes a **fictional** telecommunications company that provided home
phone and internet services. It is demonstration data, not records from a real company.

Expected file: `data/raw/Telco-Customer-Churn.csv` (970,457 bytes; SHA-256
`16320c9c1ec72448db59aa0a26a0b95401046bef5d02fd3aeb906448e3055e91` for the copy used in this project).

## How to obtain it

Automatic:

```bash
python scripts/download_data.py
```

Manual (no internet on the project machine):

1. On a connected computer open
   https://github.com/IBM/telco-customer-churn-on-icp4d/blob/master/data/Telco-Customer-Churn.csv
2. Click **Download raw file** (or open
   https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv and save it).
3. Copy it to `data/raw/Telco-Customer-Churn.csv` in this project. Do not edit it in Excel (Excel may change
   number formats and blank values).

The raw file is not committed to Git (see `.gitignore`).

## Structure

7,043 rows (one per customer), 21 columns:

| Column | Type | Values / meaning |
|---|---|---|
| customerID | identifier | Unique ID. **Excluded from modelling.** |
| gender | categorical | Female, Male |
| SeniorCitizen | binary | 1 if 65 or older, else 0 |
| Partner, Dependents | categorical | Yes, No |
| tenure | integer | Months with the company (0–72) |
| PhoneService | categorical | Yes, No |
| MultipleLines | categorical | Yes, No, No phone service |
| InternetService | categorical | DSL, Fiber optic, No |
| OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies | categorical | Yes, No, No internet service |
| Contract | categorical | Month-to-month, One year, Two year |
| PaperlessBilling | categorical | Yes, No |
| PaymentMethod | categorical | Electronic check, Mailed check, Bank transfer (automatic), Credit card (automatic) |
| MonthlyCharges | numeric | Current monthly charge (18.25–118.75) |
| TotalCharges | numeric (stored as text) | Total charged to date |
| **Churn** | **target** | Yes = left within the last month (1,869 customers, 26.5%); No (5,174) |

## Quality checks (performed by `src/data_loader.py`)

| Check | Result |
|---|---|
| Required columns | All present |
| Missing values | Only `TotalCharges`: 11 blank strings |
| Blank `TotalCharges` | All 11 have `tenure = 0` (not yet billed), so they are set to 0 |
| Duplicate customer IDs | 0 |
| Fully duplicated rows | 0 |
| Rows identical apart from customerID | 22, kept (different customers) |
| Unexpected target or category values | None |

## Limitations

- Fictional data from a single (US-style) provider; patterns may not hold for other markets, including Uganda.
- A single snapshot without dates: no seasonality, trends or time-to-churn analysis.
- No information on network quality, complaints, competitor offers, prices relative to competitors, or customer
  service interactions, all of which plausibly influence churn.
- `gender` and `SeniorCitizen` are personal attributes; their use in decisions requires ethical review even though
  they carry little predictive weight here.
- Being a widely used teaching dataset, results are not a novel contribution by themselves.

## Using another dataset

Any CSV with the same column names and value formats can replace the file. The loader validates the schema and
reports missing columns, unexpected values and duplicates before training.
