"""Build the website's sample report from the spike fixture.

Writes apps/web/src/data/sample-report.json and apps/web/public/sample/*.png.
Run from the repo root: .venv/Scripts/python scripts/build_sample_report.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import jsonschema
import numpy as np

from reel_report import build_report

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "spike_t4_22s"
SCHEMA = ROOT / "packages" / "report-schema" / "report.schema.json"
OUT_JSON = ROOT / "apps" / "web" / "src" / "data" / "sample-report.json"
OUT_IMAGES = ROOT / "apps" / "web" / "public" / "sample"


def main() -> None:
    preds = np.load(FIXTURE / "preds.npy")
    starts = [s["start"] for s in json.loads((FIXTURE / "segments.json").read_text())]
    duration = json.loads((FIXTURE / "metrics.json").read_text())["video_duration_s"]
    with open(FIXTURE / "events.csv", newline="", encoding="utf-8") as f:
        words = sum(1 for row in csv.DictReader(f) if row["type"] == "Word")

    report = build_report(preds, starts, duration, word_count=words, heatmap_dir=OUT_IMAGES)
    jsonschema.validate(report, json.loads(SCHEMA.read_text(encoding="utf-8")))

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_JSON.relative_to(ROOT)} and {len(report['heatmaps'])} heatmaps")


if __name__ == "__main__":
    main()
