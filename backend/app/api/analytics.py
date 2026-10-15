from typing import Literal, Optional

from fastapi import APIRouter, Depends, Query, Request

from src.schema import CATEGORICAL_FEATURES

from ..schemas.analytics import CustomerPage, Insights, ModelMetricsResponse, Overview
from ..services.data_service import DataService
from ..services.results_service import ResultsService
from .deps import data_service, results_service

router = APIRouter(tags=["analytics"])

ContractValue = Literal[tuple(CATEGORICAL_FEATURES["Contract"])]
InternetValue = Literal[tuple(CATEGORICAL_FEATURES["InternetService"])]


@router.get("/overview", response_model=Overview)
def overview(data: DataService = Depends(data_service)):
    return data.overview


@router.get("/customers", response_model=CustomerPage)
def customers(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1),
    search: Optional[str] = Query(None, max_length=40),
    contract: list[ContractValue] = Query(default=[]),  # type: ignore[valid-type]
    internet_service: list[InternetValue] = Query(default=[]),  # type: ignore[valid-type]
    churn: Optional[Literal["Yes", "No"]] = None,
    tenure_min: Optional[int] = Query(None, ge=0, le=1200),
    tenure_max: Optional[int] = Query(None, ge=0, le=1200),
    sort_by: str = "customerID",
    sort_dir: Literal["asc", "desc"] = "asc",
    data: DataService = Depends(data_service),
):
    page_size = min(page_size, request.app.state.settings.max_page_size)
    return data.customers(page=page, page_size=page_size, search=search, contract=contract,
                          internet_service=internet_service, churn=churn, tenure_min=tenure_min,
                          tenure_max=tenure_max, sort_by=sort_by, sort_dir=sort_dir)


@router.get("/insights", response_model=Insights)
def insights(data: DataService = Depends(data_service), results: ResultsService = Depends(results_service)):
    out = dict(data.descriptive_insights)
    if results.available:
        out.update(results.importance())
    return out


@router.get("/model/metrics", response_model=ModelMetricsResponse)
def model_metrics(results: ResultsService = Depends(results_service)):
    return results.model_metrics()
