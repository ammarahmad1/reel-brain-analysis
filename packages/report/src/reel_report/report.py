"""Builds the report dict that the frontend renders (schema: packages/report-schema)."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np

from .atlas import load_destrieux
from .config import ReportConfig
from .heatmap import render_heatmaps
from .insights import analyze
from .timeline import build_timeline

SCHEMA_VERSION = "0.1.0"
CREDITS = {
    "model": "TRIBE v2 by Meta FAIR",
    "model_url": "https://github.com/facebookresearch/tribev2",
    "model_license": "CC BY-NC 4.0",
    "text_model": "Llama 3.2 3B (Llama 3.2 Community License)",
}


def build_report(
    preds: np.ndarray,
    segment_starts: Sequence[float],
    video_duration_s: float,
    word_count: int = 0,
    config: ReportConfig | None = None,
    heatmap_dir: Path | None = None,
) -> dict[str, Any]:
    """preds: (T, 20484) TRIBE v2 output, left hemisphere first; segment_starts: seconds."""
    cfg = config or ReportConfig()
    timeline = build_timeline(
        preds, segment_starts, video_duration_s, load_destrieux(), cfg.channel_regions
    )
    ins = analyze(timeline, word_count, cfg)
    heatmaps = render_heatmaps(timeline, ins, heatmap_dir) if heatmap_dir else []

    return {
        "schema_version": SCHEMA_VERSION,
        "video": {"duration_s": round(float(video_duration_s), 2)},
        "timeline": {
            "seconds": timeline.seconds.tolist(),
            "overall": _r(timeline.overall_z()),
            "channels": {name: _r(z) for name, z in timeline.channels_z().items()},
        },
        "insights": {
            "hook": asdict(ins.hook) | {"score_z": round(ins.hook.score_z, 3)},
            "ending": asdict(ins.ending) | {"score_z": round(ins.ending.score_z, 3)},
            "peak": {"second": ins.peak.second, "z": round(ins.peak.z, 3)},
            "low": {"second": ins.low.second, "z": round(ins.low.z, 3)},
            "dips": [asdict(d) | {"min_z": round(d.min_z, 3)} for d in ins.dips],
            "carrier": {
                "channel": ins.carrier.channel,
                "correlations": {k: round(v, 3) for k, v in ins.carrier.correlations.items()},
            },
            "speech": {"word_count": ins.word_count, "detected": ins.speech_detected},
        },
        "heatmaps": [asdict(h) for h in heatmaps],
        "credits": CREDITS,
    }


def _r(x: np.ndarray) -> list[float]:
    return [round(float(v), 3) for v in x]
