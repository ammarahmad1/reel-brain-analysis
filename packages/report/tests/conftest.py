from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from pathlib import Path

import numpy as np
import pytest

from reel_report.atlas import Atlas, load_destrieux
from reel_report.config import CHANNEL_REGIONS

REPO_ROOT = Path(__file__).resolve().parents[3]
SPIKE_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "spike_t4_22s"
SCHEMA_PATH = REPO_ROOT / "packages" / "report-schema" / "report.schema.json"


@pytest.fixture(scope="session")
def atlas() -> Atlas:
    return load_destrieux()


@pytest.fixture(scope="session")
def schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def make_preds(atlas: Atlas) -> Callable[..., np.ndarray]:
    """Synthetic preds: small noise everywhere, plus a given series per channel's regions."""

    def make(n: int, channel_series: Mapping[str, np.ndarray], seed: int = 0) -> np.ndarray:
        rng = np.random.default_rng(seed)
        preds = rng.normal(0, 0.01, size=(n, atlas.labels.size))
        for channel, series in channel_series.items():
            preds[:, atlas.mask(CHANNEL_REGIONS[channel])] += np.asarray(series)[:, None]
        return preds

    return make
