"""End-to-end on real TRIBE v2 output saved by the spike (22.6 s music reel, 2 words)."""

import csv
import json

import jsonschema
import numpy as np

from reel_report import build_report

from .conftest import SPIKE_FIXTURE


def _load_fixture():
    preds = np.load(SPIKE_FIXTURE / "preds.npy")
    starts = [s["start"] for s in json.loads((SPIKE_FIXTURE / "segments.json").read_text())]
    duration = json.loads((SPIKE_FIXTURE / "metrics.json").read_text())["video_duration_s"]
    with open(SPIKE_FIXTURE / "events.csv", newline="", encoding="utf-8") as f:
        words = sum(1 for row in csv.DictReader(f) if row["type"] == "Word")
    return preds, starts, duration, words


def test_report_from_spike_matches_schema(schema, tmp_path):
    preds, starts, duration, words = _load_fixture()
    report = build_report(preds, starts, duration, word_count=words, heatmap_dir=tmp_path)

    jsonschema.validate(report, schema)
    assert report["timeline"]["seconds"] == list(range(23))
    assert report["insights"]["speech"] == {"word_count": 2, "detected": False}
    # The only words ("Purple rain", 9.0–10.3 s) line up with the speech spike at second 9,
    # which confirms row i = video second i (TRIBE's 5 s offset is already applied).
    speech = report["timeline"]["channels"]["speech"]
    assert int(np.argmax(speech[:15])) == 9
    assert report["insights"]["hook"]["rating"] == "weak"
    assert [(d["start_s"], d["end_s"]) for d in report["insights"]["dips"]] == [(2, 4), (16, 20)]
    for heatmap in report["heatmaps"]:
        assert (tmp_path / heatmap["file"]).stat().st_size > 10_000
