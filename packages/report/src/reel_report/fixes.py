"""Fix suggestions ranked from Insights.

Every rule adds candidates with a priority and the top `max_fixes` are kept. The last three
rules (nearly) always fire, so a report always gets enough fixes.
"""

from __future__ import annotations

from dataclasses import dataclass

from .config import ReportConfig
from .insights import Insights

DIP_ADVICE = {
    "visual": (
        "Add visual change at {span}",
        "Predicted visual response drops here. Try a cut, camera move, zoom, or new shot.",
    ),
    "faces": (
        "Put a face on screen at {span}",
        "Predicted face-area response drops here. A close-up or a person reacting can "
        "bring it back.",
    ),
    "sound": (
        "Lift the audio at {span}",
        "Predicted auditory response drops here. Try a beat drop, sound effect, or music change.",
    ),
    "speech": (
        "Add a spoken line at {span}",
        "Predicted language-area response drops here. A voiceover line or a remark to camera "
        "can help.",
    ),
}


@dataclass(frozen=True)
class Fix:
    id: str
    title: str
    detail: str
    priority: float
    start_s: int | None = None
    end_s: int | None = None  # exclusive


def suggest_fixes(ins: Insights, cfg: ReportConfig) -> list[Fix]:
    hook, ending, peak, low = ins.hook, ins.ending, ins.peak.second, ins.low.second
    fixes: list[Fix] = []

    if hook.rating == "weak":
        if peak < hook.end_s:
            tip = f"Tighten it so it reaches the {peak}s moment faster."
        else:
            tip = f"Your strongest predicted moment is at {peak}s. Open with it, or tease it early."
        fixes.append(
            Fix(
                id="weak_hook",
                title=f"Strengthen the first {cfg.hook_s} seconds",
                detail=f"Your opening is predicted to land below the rest of the reel. {tip}",
                priority=100 + 10 * abs(hook.score_z),
                start_s=hook.start_s,
                end_s=hook.end_s,
            )
        )
    elif hook.rating == "average" and peak >= hook.end_s:
        fixes.append(
            Fix(
                id="average_hook",
                title=f"Make the first {cfg.hook_s} seconds stand out",
                detail="Your opening is predicted to land about the same as the rest of the "
                f"reel. Opening on your strongest moment ({peak}s) would give it an edge.",
                priority=30,
                start_s=hook.start_s,
                end_s=hook.end_s,
            )
        )

    # The weak-hook fix already covers dips inside the opening.
    dips = [d for d in ins.dips if hook.rating != "weak" or d.start_s >= hook.end_s]
    for dip in sorted(dips, key=lambda d: d.min_z)[:2]:
        title, detail = DIP_ADVICE[dip.weakest_channel]
        fixes.append(
            Fix(
                id=f"dip_{dip.start_s}",
                title=title.format(span=f"{dip.start_s}–{dip.end_s}s"),
                detail=detail,
                priority=80 + 10 * abs(dip.min_z),
                start_s=dip.start_s,
                end_s=dip.end_s,
            )
        )

    if ending.rating == "weak":
        fixes.append(
            Fix(
                id="weak_ending",
                title="End on a stronger beat",
                detail=f"The last {cfg.ending_s} seconds are predicted to land below the rest "
                "of the reel. Trim the tail, or end on a payoff that loops back to the start.",
                priority=60 + 10 * abs(ending.score_z),
                start_s=ending.start_s,
                end_s=ending.end_s,
            )
        )

    if not ins.speech_detected:
        fixes.append(
            Fix(
                id="no_speech",
                title="Consider a voiceover or spoken hook",
                detail="Few or no spoken words were detected, so language areas are predicted "
                "to stay quiet. A short spoken line adds another channel. Skip this if the reel "
                "is meant to be music-only.",
                priority=50,
            )
        )

    corr = ins.carrier.correlations
    top = ins.carrier.channel or max(corr, key=corr.__getitem__)
    if ins.carrier.channel:
        detail = (
            f"{top.capitalize()} track the predicted ups and downs of this reel most closely. "
            "More of what's working there is a safe bet."
        )
    else:
        detail = (
            f"No single channel drives this reel; {top} come closest. Giving one channel a "
            "clear lead can make the reel feel more focused."
        )
    fixes.append(
        Fix(
            id="lean_in",
            title=f"Lean into {top}",
            detail=detail,
            priority=20 if ins.carrier.channel else 6,
        )
    )

    fixes.append(
        Fix(
            id="build_on_peak",
            title=f"Build around your {peak}s moment",
            detail="This is the reel's strongest predicted moment. Work out what makes it land "
            "and do more of it.",
            priority=10,
            start_s=peak,
            end_s=peak + 1,
        )
    )

    if not any(d.start_s <= low < d.end_s for d in ins.dips):
        fixes.append(
            Fix(
                id="trim_low",
                title=f"Tighten around {low}s",
                detail="This is the reel's weakest predicted moment. Trimming or speeding up "
                "this part keeps momentum.",
                priority=8,
                start_s=low,
                end_s=low + 1,
            )
        )

    # sorted() is stable, so rule order breaks ties.
    return sorted(fixes, key=lambda f: f.priority, reverse=True)[: cfg.max_fixes]
