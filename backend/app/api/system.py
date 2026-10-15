from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from ..schemas.analytics import Health, ModelSchema
from ..services.data_service import DataService
from ..services.model_service import ModelService
from ..services.results_service import ResultsService
from .deps import data_service, model_service, results_service

router = APIRouter(tags=["system"])


@router.get("/health", response_model=Health)
def health(data: DataService = Depends(data_service), model: ModelService = Depends(model_service),
           results: ResultsService = Depends(results_service)):
    ok = data.available and model.available and results.available
    name = None
    if model.available:
        try:
            name = model.model_name
        except Exception:  # noqa: BLE001 - health must never fail
            ok = False
    return {"status": "ok" if ok else "degraded", "dataset_available": data.available,
            "model_available": model.available, "results_available": results.available, "model_name": name}


@router.get("/schema", response_model=ModelSchema)
def schema(model: ModelService = Depends(model_service)):
    """Feature schema expected by the trained pipeline (drives the form and CSV template)."""
    return model.schema()


@router.get("/schema/template.csv", response_class=PlainTextResponse)
def template(model: ModelService = Depends(model_service)):
    return PlainTextResponse(
        model.template_csv(), media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="churniq_template.csv"'},
    )
