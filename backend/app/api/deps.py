from fastapi import Request

from ..services.data_service import DataService
from ..services.model_service import ModelService
from ..services.results_service import ResultsService


def data_service(request: Request) -> DataService:
    return request.app.state.data


def model_service(request: Request) -> ModelService:
    return request.app.state.model


def results_service(request: Request) -> ResultsService:
    return request.app.state.results
