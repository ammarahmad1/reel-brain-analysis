"""Thresholds and the channel → Destrieux region map. Documented in docs/report-methodology.md."""

from __future__ import annotations

from dataclasses import dataclass, field

CHANNELS: tuple[str, ...] = ("visual", "faces", "sound", "speech")

CHANNEL_REGIONS: dict[str, tuple[str, ...]] = {
    "visual": (
        "S_calcarine",
        "G_cuneus",
        "Pole_occipital",
        "G_occipital_sup",
        "G_occipital_middle",
        "G_and_S_occipital_inf",
    ),
    "faces": ("G_oc-temp_lat-fusifor",),
    "sound": ("G_temp_sup-G_T_transv", "S_temporal_transverse", "G_temp_sup-Plan_tempo"),
    "speech": (
        "G_temp_sup-Lateral",
        "S_temporal_sup",
        "G_front_inf-Opercular",
        "G_front_inf-Triangul",
    ),
}


@dataclass(frozen=True)
class ReportConfig:
    hook_s: int = 3
    ending_s: int = 3
    strong_z: float = 0.5  # window mean z needed for "strong"
    weak_z: float = -0.5  # ...and at or below this for "weak"
    dip_z: float = -0.75
    dip_min_s: int = 2
    max_dips: int = 3
    carrier_min_r: float = 0.5  # correlation with overall needed to "carry" the reel
    speech_min_words: int = 5
    max_fixes: int = 3
    channel_regions: dict[str, tuple[str, ...]] = field(
        default_factory=lambda: dict(CHANNEL_REGIONS)
    )
