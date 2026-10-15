"""Dataset access and descriptive analytics.

The dataset is loaded once (lazily, thread-safe) and summaries are computed
once and cached; requests never re-read the CSV.
"""

from __future__ import annotations

import math
import threading
from functools import cached_property

import numpy as np
import pandas as pd

from src.data_loader import DatasetError, check_quality, load_dataset, read_raw_csv
from src.eda import add_tenure_band, association_with_churn, churn_rate_by

from ..core.config import Settings
from ..core.errors import APIError, ServiceUnavailable

TABLE_COLUMNS = ["customerID", "tenure", "Contract", "InternetService", "PaymentMethod",
                 "TechSupport", "MonthlyCharges", "TotalCharges", "Churn"]
SORTABLE = set(TABLE_COLUMNS)
CHARGE_BANDS = [0, 35, 60, 80, 100, np.inf]
CHARGE_LABELS = ["< 35", "35–60", "60–80", "80–100", "≥ 100"]


def _rates(df: pd.DataFrame, col: str) -> list[dict]:
    t = churn_rate_by(df, col)
    return [
        {"group": str(r.group), "customers": int(r.customers), "churned": int(r.churned),
         "churn_rate": round(float(r.churn_rate), 4)}
        for r in t.itertuples()
    ]


class DataService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._lock = threading.Lock()
        self._df: pd.DataFrame | None = None

    # ---------- loading ----------

    @property
    def available(self) -> bool:
        return self.settings.data_path.exists()

    @property
    def df(self) -> pd.DataFrame:
        if self._df is None:
            with self._lock:
                if self._df is None:
                    try:
                        self._df = load_dataset(self.settings.data_path)
                    except DatasetError as exc:
                        raise ServiceUnavailable(
                            "The dataset is not available. Run `python scripts/download_data.py` on the server."
                        ) from exc
        return self._df

    # ---------- shared summaries ----------

    def monthly_charges_summary(self) -> list[dict]:
        out = []
        for label in ["No", "Yes"]:
            s = self.df.loc[self.df["Churn"] == label, "MonthlyCharges"]
            out.append({"churn": label, "count": int(s.size), "mean": round(float(s.mean()), 2),
                        "median": round(float(s.median()), 2), "q1": round(float(s.quantile(0.25)), 2),
                        "q3": round(float(s.quantile(0.75)), 2), "min": round(float(s.min()), 2),
                        "max": round(float(s.max()), 2)})
        return out

    def monthly_charges_histogram(self, width: float = 10.0) -> list[dict]:
        values = self.df["MonthlyCharges"]
        lo = math.floor(values.min() / width) * width
        hi = math.ceil(values.max() / width) * width
        edges = np.arange(lo, hi + width, width)
        churn = self.df["Churn"] == "Yes"
        stayed, _ = np.histogram(values[~churn], bins=edges)
        churned, _ = np.histogram(values[churn], bins=edges)
        return [
            {"start": float(edges[i]), "end": float(edges[i + 1]), "stayed": int(stayed[i]),
             "churned": int(churned[i]), "stayed_share": round(float(stayed[i] / stayed.sum()), 4),
             "churned_share": round(float(churned[i] / churned.sum()), 4)}
            for i in range(len(edges) - 1)
        ]

    # ---------- overview ----------

    @cached_property
    def overview(self) -> dict:
        df = self.df
        churned = int((df["Churn"] == "Yes").sum())
        quality = check_quality(read_raw_csv(self.settings.data_path))
        checks = [
            ("Required columns present", "Yes" if not quality.missing_columns else ", ".join(quality.missing_columns)),
            ("Blank TotalCharges values", f"{quality.blank_total_charges} (all with tenure 0: "
                                          f"{quality.blank_total_charges_with_zero_tenure}); set to 0"),
            ("Duplicate customer IDs", str(quality.duplicate_ids)),
            ("Fully duplicated rows", str(quality.duplicate_rows)),
            ("Rows identical apart from ID", f"{quality.duplicate_feature_rows} (kept: distinct customers)"),
            ("Unexpected target values", "None" if not quality.unexpected_target_values else str(quality.unexpected_target_values)),
        ]
        return {
            "total_customers": int(len(df)),
            "churned": churned,
            "stayed": int(len(df) - churned),
            "churn_rate": round(churned / len(df), 4),
            "churn_by_contract": _rates(df, "Contract"),
            "churn_by_tenure": _rates(add_tenure_band(df), "tenure_band"),
            "monthly_charges_summary": self.monthly_charges_summary(),
            "monthly_charges_histogram": self.monthly_charges_histogram(),
            "dataset_summary": {
                "name": "IBM Telco Customer Churn (sample dataset)",
                "provider": "Fictional telecom provider created by IBM for demonstrations",
                "rows": int(len(df)),
                "columns": int(df.shape[1]),
                "model_features": 19,
                "numeric_features": 3,
                "categorical_features": 16,
                "tenure_range_months": f"{int(df['tenure'].min())}–{int(df['tenure'].max())}",
                "monthly_charges_range": f"{df['MonthlyCharges'].min():.2f}–{df['MonthlyCharges'].max():.2f}",
            },
            "quality_checks": [{"check": c, "result": r} for c, r in checks],
        }

    # ---------- insights (descriptive part) ----------

    @cached_property
    def descriptive_insights(self) -> dict:
        df = self.df
        banded = df.assign(monthly_charge_band=pd.cut(df["MonthlyCharges"], CHARGE_BANDS, labels=CHARGE_LABELS,
                                                      right=False))
        assoc = association_with_churn(df)
        return {
            "overall_churn_rate": round(float((df["Churn"] == "Yes").mean()), 4),
            "churn_by_contract": _rates(df, "Contract"),
            "churn_by_tenure": _rates(add_tenure_band(df), "tenure_band"),
            "churn_by_internet_service": _rates(df, "InternetService"),
            "churn_by_payment_method": _rates(df, "PaymentMethod"),
            "churn_by_monthly_charge_band": _rates(banded, "monthly_charge_band"),
            "monthly_charges_summary": self.monthly_charges_summary(),
            "associations": [
                {"feature": r.feature, "measure": r.measure, "strength": round(float(r.strength), 4),
                 "p_value": float(r.p_value)}
                for r in assoc.itertuples()
            ],
        }

    # ---------- customer explorer ----------

    def customers(self, *, page: int, page_size: int, search: str | None, contract: list[str],
                  internet_service: list[str], churn: str | None, tenure_min: int | None,
                  tenure_max: int | None, sort_by: str, sort_dir: str) -> dict:
        if sort_by not in SORTABLE:
            raise APIError(422, "invalid_request", f"Cannot sort by '{sort_by}'.",
                           [f"Sortable columns: {', '.join(TABLE_COLUMNS)}"])
        df = self.df
        mask = pd.Series(True, index=df.index)
        if search:
            mask &= df["customerID"].str.contains(search.strip(), case=False, regex=False)
        if contract:
            mask &= df["Contract"].isin(contract)
        if internet_service:
            mask &= df["InternetService"].isin(internet_service)
        if churn:
            mask &= df["Churn"] == churn
        if tenure_min is not None:
            mask &= df["tenure"] >= tenure_min
        if tenure_max is not None:
            mask &= df["tenure"] <= tenure_max

        view = df.loc[mask, TABLE_COLUMNS].sort_values(
            [sort_by, "customerID"], ascending=[sort_dir == "asc", True], kind="mergesort"
        )
        total = int(len(view))
        total_pages = max(1, math.ceil(total / page_size))
        start = (page - 1) * page_size
        items = view.iloc[start:start + page_size].to_dict(orient="records")
        return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}

    def sample_records(self, n: int = 3) -> pd.DataFrame:
        return self.df.drop(columns=["Churn"]).head(n)
