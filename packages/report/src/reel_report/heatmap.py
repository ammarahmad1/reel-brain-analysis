"""Brain heatmap PNGs (lateral views of both hemispheres) rendered with nilearn."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .atlas import N_VERTICES_PER_HEMI
from .insights import Insights
from .timeline import Timeline


@dataclass(frozen=True)
class Heatmap:
    kind: str  # "average" | "hook" | "peak" | "dip"
    label: str
    second: int | None
    file: str  # filename inside the output directory


def render_heatmaps(timeline: Timeline, ins: Insights, out_dir: Path) -> list[Heatmap]:
    """One image for the whole-reel average plus key moments, on a shared colour scale."""
    out_dir.mkdir(parents=True, exist_ok=True)
    preds, seconds = timeline.preds, timeline.seconds
    row_of = {int(s): i for i, s in enumerate(seconds)}
    hook_rows = (seconds >= ins.hook.start_s) & (seconds < ins.hook.end_s)

    frames: list[tuple[Heatmap, np.ndarray]] = [
        (Heatmap("average", "Whole reel (average)", None, "average.png"), preds.mean(axis=0)),
        (
            Heatmap("hook", f"Hook ({ins.hook.start_s}–{ins.hook.end_s}s)", None, "hook.png"),
            preds[hook_rows].mean(axis=0),
        ),
        (
            Heatmap("peak", f"Peak moment ({ins.peak.second}s)", ins.peak.second, "peak.png"),
            preds[row_of[ins.peak.second]],
        ),
    ]
    if ins.dips:
        dip = min(ins.dips, key=lambda d: d.min_z)
        frames.append(
            (
                Heatmap("dip", f"Deepest dip ({dip.lowest_second}s)", dip.lowest_second, "dip.png"),
                preds[row_of[dip.lowest_second]],
            )
        )

    vmax = float(np.percentile(np.abs(preds), 99)) or 1.0
    for meta, values in frames:
        _render(values, vmax, meta.label, out_dir / meta.file)
    return [meta for meta, _ in frames]


def _render(values: np.ndarray, vmax: float, title: str, path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.cm import ScalarMappable
    from matplotlib.colors import Normalize
    from nilearn import datasets, plotting

    fsaverage = datasets.fetch_surf_fsaverage("fsaverage5")
    fig, axes = plt.subplots(1, 2, subplot_kw={"projection": "3d"}, figsize=(8, 3.6))
    halves = (values[:N_VERTICES_PER_HEMI], values[N_VERTICES_PER_HEMI:])  # left first
    for ax, hemi, hemi_values in zip(axes, ("left", "right"), halves, strict=True):
        plotting.plot_surf_stat_map(
            fsaverage[f"infl_{hemi}"],
            hemi_values,
            hemi=hemi,
            view="lateral",
            bg_map=fsaverage[f"sulc_{hemi}"],
            axes=ax,
            figure=fig,
            colorbar=False,
            vmax=vmax,
            threshold=0.15 * vmax,  # let the anatomy show through near-zero values
            cmap="cold_hot",
        )
        ax.set_title(hemi.capitalize(), y=0.85)
    fig.colorbar(
        ScalarMappable(Normalize(-vmax, vmax), "cold_hot"),
        ax=axes,
        orientation="horizontal",
        fraction=0.05,
        pad=0.02,
        label="Predicted response (lower ← → higher)",
    )
    fig.suptitle(title)
    fig.savefig(path, dpi=110, bbox_inches="tight")
    plt.close(fig)
