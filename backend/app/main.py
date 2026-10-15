"""ChurnIQ API.

Run from the project root:
    uvicorn backend.app.main:app --reload --port 8000
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import analytics, predictions, system
from .core.config import Settings
from .core.errors import register_error_handlers
from .services.data_service import DataService
from .services.model_service import ModelService
from .services.results_service import ResultsService

logging.basicConfig(level=logging.INFO)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    app = FastAPI(
        title="ChurnIQ API",
        version="1.0.0",
        description="Research prototype API for customer churn prediction on the IBM Telco Customer Churn "
                    "sample dataset (fictional provider).",
    )
    app.state.settings = settings
    app.state.data = DataService(settings)
    app.state.model = ModelService(settings)
    app.state.results = ResultsService(settings)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    register_error_handlers(app)
    for module in (system, analytics, predictions):
        app.include_router(module.router, prefix="/api")
    return app


app = create_app()
