"""Obtain the IBM Telco Customer Churn CSV.

Kept separate from loading/training so another compatible dataset can be
used simply by placing its CSV at the configured path.
"""

from __future__ import annotations

import urllib.request
from pathlib import Path

from src.config import DATASET_URL, RAW_DATA_PATH

MAX_BYTES = 20 * 1024 * 1024  # the real file is ~1 MB


def download_dataset(dest: Path = RAW_DATA_PATH, force: bool = False, url: str = DATASET_URL) -> Path:
    """Download the dataset to ``dest`` (skips if it already exists unless ``force``)."""
    dest = Path(dest)
    if dest.exists() and not force:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=60) as resp:
        content = resp.read(MAX_BYTES + 1)
    if len(content) > MAX_BYTES:
        raise OSError("Downloaded file is unexpectedly large; aborting.")
    if not content.startswith(b"customerID,"):
        raise OSError("Downloaded file does not look like the Telco churn CSV.")
    tmp = dest.with_suffix(".part")
    tmp.write_bytes(content)
    tmp.replace(dest)
    return dest
