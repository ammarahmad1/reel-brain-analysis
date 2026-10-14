"""Run TRIBE v2 on a video and write report.json plus heatmaps.

    python -m reel_report VIDEO [--out DIR]

Needs tribev2 installed and a GPU; the Colab notebook sets both up.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

import numpy as np

from .report import build_report


def video_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return float(out)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="python -m reel_report", description="Run TRIBE v2 on a video and build its report."
    )
    parser.add_argument("video", type=Path)
    parser.add_argument("--out", type=Path, default=Path("report"))
    parser.add_argument("--cache", type=Path, default=Path.home() / ".cache" / "tribev2")
    args = parser.parse_args(argv)
    if not args.video.is_file():
        parser.error(f"no such video: {args.video}")

    from tribev2 import TribeModel

    start = time.time()
    model = TribeModel.from_pretrained("facebook/tribev2", cache_folder=str(args.cache))
    events = model.get_events_dataframe(video_path=str(args.video))
    preds, segments = model.predict(events=events)

    args.out.mkdir(parents=True, exist_ok=True)
    report = build_report(
        np.asarray(preds),
        [float(s.start) for s in segments],
        video_duration(args.video),
        word_count=int((events["type"] == "Word").sum()),
        heatmap_dir=args.out,
    )
    report_json = json.dumps(report, indent=2, ensure_ascii=False)
    (args.out / "report.json").write_text(report_json, encoding="utf-8")

    ins = report["insights"]
    print(f"\nDone in {(time.time() - start) / 60:.0f} min.\n")
    print(f"Hook (first {ins['hook']['end_s']}s): {ins['hook']['rating']}")
    print(f"Peak moment: {ins['peak']['second']}s")
    print(f"Carried by: {ins['carrier']['channel'] or 'no single channel'}")
    print("\nTop fixes:")
    for i, fix in enumerate(report["fixes"], 1):
        print(f"  {i}. {fix['title']}")


if __name__ == "__main__":
    main()
