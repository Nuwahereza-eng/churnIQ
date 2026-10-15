from typing import Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile

from ..core.errors import APIError
from ..schemas.prediction import BatchPredictionResponse, BatchValidation, PredictionResult, PredictRequest
from ..services.model_service import ModelService
from .deps import model_service

router = APIRouter(tags=["predictions"])


@router.post("/predict", response_model=PredictionResult)
def predict(body: PredictRequest, model: ModelService = Depends(model_service)):
    return model.predict(body.customer.model_dump(), body.threshold)


async def _read(file: UploadFile, limit: int) -> tuple[str, bytes]:
    if file is None or not file.filename:
        raise APIError(422, "missing_file", "No file was uploaded.")
    content = await file.read(limit + 1)  # read at most limit+1 bytes
    return file.filename, content


@router.post("/predict/batch/validate", response_model=BatchValidation)
async def validate_batch(file: UploadFile = File(...), model: ModelService = Depends(model_service)):
    """Check an uploaded CSV and return a preview without predicting."""
    name, content = await _read(file, model.settings.max_upload_bytes)
    return model.validate_batch(name, content)


@router.post("/predict/batch", response_model=BatchPredictionResponse)
async def predict_batch(file: UploadFile = File(...),
                        threshold: Optional[float] = Query(None, gt=0, lt=1),
                        model: ModelService = Depends(model_service)):
    name, content = await _read(file, model.settings.max_upload_bytes)
    return model.predict_batch(name, content, threshold)
