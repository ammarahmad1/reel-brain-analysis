"""Deterministic insight rules over a Timeline. All scores are within-reel z-scores."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import ReportConfig
from .timeline import Timeline


@dataclass(frozen=True)
class WindowScore:
    start_s: int
    end_s: int  # exclusive
    score_z: float
    rating: str  # "strong" | "average" | "weak"


@dataclass(frozen=True)
class Dip:
    start_s: int
    end_s: int  # exclusive
    min_z: float
    lowest_second: int
    weakest_channel: str


@dataclass(frozen=True)
class Moment:
    second: int
    z: float


@dataclass(frozen=True)
class Carrier:
    channel: str | None  # None when no channel tracks the overall response closely
    correlations: dict[str, float]


@dataclass(frozen=True)
class Insights:
    hook: WindowScore
    ending: WindowScore
    peak: Moment
    low: Moment
    dips: list[Dip]  # chronological
    carrier: Carrier
    word_count: int
    speech_detected: bool


def analyze(timeline: Timeline, word_count: int, cfg: ReportConfig) -> Insights:
    overall_z = timeline.overall_z()
    seconds = timeline.seconds
    end = int(seconds[-1]) + 1
    speech_detected = word_count >= cfg.speech_min_words
    channels_z = timeline.channels_z()
    if not speech_detected:
        # A reel without speech always has a quiet speech channel, so it would "cause" every dip.
        channels_z.pop("speech", None)
    return Insights(
        hook=_window(seconds, overall_z, 0, cfg.hook_s, cfg),
        ending=_window(seconds, overall_z, max(0, end - cfg.ending_s), end, cfg),
        peak=Moment(int(seconds[overall_z.argmax()]), float(overall_z.max())),
        low=Moment(int(seconds[overall_z.argmin()]), float(overall_z.min())),
        dips=_dips(seconds, overall_z, channels_z, cfg),
        carrier=_carrier(timeline, cfg),
        word_count=word_count,
        speech_detected=speech_detected,
    )


def _rating(z: float, cfg: ReportConfig) -> str:
    if z >= cfg.strong_z:
        return "strong"
    if z <= cfg.weak_z:
        return "weak"
    return "average"


def _window(
    seconds: np.ndarray, z: np.ndarray, start: int, end: int, cfg: ReportConfig
) -> WindowScore:
    in_window = (seconds >= start) & (seconds < end)
    score = float(z[in_window].mean()) if in_window.any() else 0.0
    return WindowScore(start, end, score, _rating(score, cfg))


def _dips(
    seconds: np.ndarray, z: np.ndarray, channels_z: dict[str, np.ndarray], cfg: ReportConfig
) -> list[Dip]:
    runs: list[list[int]] = []  # row indices of consecutive low seconds
    for i in np.flatnonzero(z <= cfg.dip_z):
        if runs and seconds[i] == seconds[runs[-1][-1]] + 1:
            runs[-1].append(int(i))
        else:
            runs.append([int(i)])

    dips = []
    for run in runs:
        if len(run) < cfg.dip_min_s:
            continue
        lowest = run[int(np.argmin(z[run]))]
        weakest = min(channels_z, key=lambda c: float(channels_z[c][run].mean()))
        dips.append(
            Dip(
                start_s=int(seconds[run[0]]),
                end_s=int(seconds[run[-1]]) + 1,
                min_z=float(z[lowest]),
                lowest_second=int(seconds[lowest]),
                weakest_channel=weakest,
            )
        )
    deepest = sorted(dips, key=lambda d: d.min_z)[: cfg.max_dips]
    return sorted(deepest, key=lambda d: d.start_s)


def _carrier(timeline: Timeline, cfg: ReportConfig) -> Carrier:
    correlations = {
        name: _pearson(values, timeline.overall) for name, values in timeline.channels.items()
    }
    best = max(correlations, key=correlations.__getitem__)
    return Carrier(best if correlations[best] >= cfg.carrier_min_r else None, correlations)


def _pearson(a: np.ndarray, b: np.ndarray) -> float:
    if a.size < 2 or a.std() < 1e-8 or b.std() < 1e-8:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])
