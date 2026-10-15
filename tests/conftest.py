import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from synthetic import make_synthetic_raw  # noqa: E402


@pytest.fixture
def synthetic_raw():
    return make_synthetic_raw(400, seed=0)


@pytest.fixture
def synthetic_csv(tmp_path, synthetic_raw):
    path = tmp_path / "synthetic.csv"
    synthetic_raw.to_csv(path, index=False)
    return path


@pytest.fixture(scope="session")
def trained_synthetic(tmp_path_factory):
    """A full (quick-mode) training run on SYNTHETIC data, saved to a temp dir."""
    from src.predict import load_model
    from src.train import run_training, save_outputs

    tmp = tmp_path_factory.mktemp("model")
    csv = tmp / "synthetic.csv"
    make_synthetic_raw(500, seed=0).to_csv(csv, index=False)
    outcome = run_training(csv, quick=True, verbose=False)
    paths = {
        "model_path": tmp / "model.joblib",
        "metadata_path": tmp / "metadata.json",
        "results_path": tmp / "results.json",
    }
    save_outputs(outcome, **paths)
    model = load_model(paths["model_path"], paths["metadata_path"])
    return {"outcome": outcome, "model": model, **paths}
