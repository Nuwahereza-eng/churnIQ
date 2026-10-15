"""Backend settings.

Paths default to the shared project locations in ``src/config.py`` so the
API serves exactly the model and results produced by ``python -m src.train``.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import METADATA_PATH, MODEL_PATH, RAW_DATA_PATH, RESULTS_PATH  # noqa: E402

DEFAULT_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173,http://127.0.0.1:4173"


def _static_dir_from_env() -> Path | None:
    raw = os.environ.get("CHURNIQ_STATIC_DIR", "").strip()
    return Path(raw) if raw else None


def _origins_from_env() -> list[str]:
    raw = os.environ.get("CHURNIQ_CORS_ORIGINS", DEFAULT_ORIGINS)
    return [o.strip() for o in raw.split(",") if o.strip()]


@dataclass
class Settings:
    data_path: Path = RAW_DATA_PATH
    model_path: Path = MODEL_PATH
    metadata_path: Path = METADATA_PATH
    results_path: Path = RESULTS_PATH
    cors_origins: list[str] = field(default_factory=_origins_from_env)
    max_upload_bytes: int = 5 * 1024 * 1024
    max_batch_rows: int = 10_000
    max_page_size: int = 100
    # Built React app (frontend/dist) to serve from the same origin in production.
    # Unset in development, where the Vite dev server serves the frontend.
    static_dir: Path | None = field(default_factory=_static_dir_from_env)
