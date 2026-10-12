"""Per-second channel timelines from TRIBE v2 predictions.

TRIBE v2 is trained with a 5 s neuro offset, so prediction row i already describes the
response to video second i. Rows for segments without events are dropped by TRIBE, so
seconds come from the segment starts, never from row indices.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import numpy as np

from .atlas import Atlas


@dataclass(frozen=True)
class Timeline:
    seconds: np.ndarray  # (T,) int, video second each row describes; strictly increasing
    overall: np.ndarray  # (T,) mean predicted response over all cortex
    channels: dict[str, np.ndarray]  # channel → (T,) mean over its regions
    preds: np.ndarray  # (T, n_vertices) rows kept, for heatmaps

    def overall_z(self) -> np.ndarray:
        return zscore(self.overall)

    def channels_z(self) -> dict[str, np.ndarray]:
        return {name: zscore(values) for name, values in self.channels.items()}


def zscore(x: np.ndarray) -> np.ndarray:
    """Within-reel z-score; a flat series maps to zeros."""
    std = float(x.std())
    if std < 1e-8:
        return np.zeros_like(x, dtype=np.float64)
    return (x - x.mean()) / std


def build_timeline(
    preds: np.ndarray,
    segment_starts: Sequence[float],
    video_duration_s: float,
    atlas: Atlas,
    channel_regions: Mapping[str, Sequence[str]],
) -> Timeline:
    preds = np.asarray(preds, dtype=np.float64)
    starts = np.asarray(segment_starts, dtype=np.float64)
    if preds.ndim != 2 or preds.shape[1] != atlas.labels.size:
        raise ValueError(f"preds must be (T, {atlas.labels.size}), got {preds.shape}")
    if starts.shape != (preds.shape[0],):
        raise ValueError(f"{starts.size} segment starts for {preds.shape[0]} prediction rows")

    keep = starts < video_duration_s
    preds, seconds = preds[keep], np.floor(starts[keep] + 1e-6).astype(int)
    if seconds.size == 0:
        raise ValueError("No prediction rows fall inside the video")
    if np.any(np.diff(seconds) <= 0):
        raise ValueError("Segment starts must be strictly increasing whole seconds")

    return Timeline(
        seconds=seconds,
        overall=preds[:, atlas.cortex_mask].mean(axis=1),
        channels={
            name: preds[:, atlas.mask(regions)].mean(axis=1)
            for name, regions in channel_regions.items()
        },
        preds=preds,
    )
