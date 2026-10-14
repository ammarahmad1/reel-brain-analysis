"""python -m reel_report with a stand-in for tribev2 that replays the spike fixture."""

import json
import sys
import types
from types import SimpleNamespace

import numpy as np
import pandas as pd

from reel_report import __main__ as cli

from .conftest import SPIKE_FIXTURE


class FakeTribeModel:
    @classmethod
    def from_pretrained(cls, name, cache_folder):
        return cls()

    def get_events_dataframe(self, video_path):
        return pd.read_csv(SPIKE_FIXTURE / "events.csv")

    def predict(self, events):
        starts = json.loads((SPIKE_FIXTURE / "segments.json").read_text())
        return np.load(SPIKE_FIXTURE / "preds.npy"), [SimpleNamespace(**s) for s in starts]


def test_cli_writes_report(tmp_path, monkeypatch, capsys):
    monkeypatch.setitem(sys.modules, "tribev2", types.SimpleNamespace(TribeModel=FakeTribeModel))
    monkeypatch.setattr(cli, "video_duration", lambda path: 22.64)
    video = tmp_path / "reel.mp4"
    video.write_bytes(b"")

    cli.main([str(video), "--out", str(tmp_path / "report")])

    report = json.loads((tmp_path / "report" / "report.json").read_text(encoding="utf-8"))
    assert report["insights"]["speech"]["word_count"] == 2
    for heatmap in report["heatmaps"]:
        assert (tmp_path / "report" / heatmap["file"]).is_file()
    assert "Peak moment:" in capsys.readouterr().out
