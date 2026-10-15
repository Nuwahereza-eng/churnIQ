"""ChurnIQ API.

Run from the project root:
    uvicorn backend.app.main:app --reload --port 8000

In production, set CHURNIQ_STATIC_DIR to the built frontend (frontend/dist) and
the API also serves the React app, so one service hosts the whole application.
"""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

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
    if settings.static_dir is not None:
        _serve_frontend(app, settings.static_dir)
    return app


def _serve_frontend(app: FastAPI, static_dir: Path) -> None:
    """Serve the built single-page app; unknown non-API paths return index.html."""
    root = static_dir.resolve()
    index = root / "index.html"
    if not index.is_file():
        logging.getLogger("churniq").warning("CHURNIQ_STATIC_DIR %s has no index.html; frontend not served", root)
        return
    if (root / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=root / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        if full_path == "api" or full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not found.")
        candidate = (root / full_path).resolve()
        if full_path and candidate.is_file() and candidate.is_relative_to(root):
            return FileResponse(candidate)
        return FileResponse(index)


app = create_app()
