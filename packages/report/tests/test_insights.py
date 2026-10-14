import numpy as np

from reel_report.config import CHANNEL_REGIONS, ReportConfig
from reel_report.insights import analyze
from reel_report.timeline import build_timeline

CFG = ReportConfig()


def _analyze(atlas, preds, word_count=0):
    n = preds.shape[0]
    tl = build_timeline(preds, range(n), float(n), atlas, CHANNEL_REGIONS)
    return analyze(tl, word_count, CFG)


def _all_channels(series):
    return {c: series for c in CHANNEL_REGIONS}


def test_weak_hook_and_peak(atlas, make_preds):
    series = np.r_[[-1.0] * 3, np.ones(12)]
    series[9] = 2.0  # clear peak
    ins = _analyze(atlas, make_preds(15, _all_channels(series)))
    assert ins.hook.rating == "weak"
    assert ins.peak.second == 9


def test_dip_found_and_attributed_to_weakest_channel(atlas, make_preds):
    n = 20
    base = np.ones(n)
    visual = base.copy()
    visual[8:12] = -3.0  # visual collapses at 8–11 s and drags the overall down
    series = {"visual": visual, "faces": base, "sound": base, "speech": base}
    ins = _analyze(atlas, make_preds(n, series))
    assert len(ins.dips) == 1
    dip = ins.dips[0]
    assert (dip.start_s, dip.end_s, dip.weakest_channel) == (8, 12, "visual")


def test_dip_not_blamed_on_speech_when_reel_has_no_speech(atlas, make_preds):
    n = 20
    base = np.ones(n)
    speech = base.copy()
    speech[8:12] = -6.0
    visual = base.copy()
    visual[8:12] = -1.0
    series = {"visual": visual, "faces": base, "sound": base, "speech": speech}
    assert _analyze(atlas, make_preds(n, series), word_count=50).dips[0].weakest_channel == "speech"
    assert _analyze(atlas, make_preds(n, series), word_count=0).dips[0].weakest_channel == "visual"


def test_single_low_second_is_not_a_dip(atlas, make_preds):
    series = np.ones(15)
    series[7] = -5.0
    ins = _analyze(atlas, make_preds(15, _all_channels(series)))
    assert ins.dips == []


def test_carrier_is_channel_tracking_overall(atlas, make_preds):
    t = np.arange(20)
    ins = _analyze(atlas, make_preds(20, {"sound": 2 * np.sin(t / 2)}))
    assert ins.carrier.channel == "sound"


def test_speech_detection_threshold(atlas, make_preds):
    preds = make_preds(10, {})
    assert not _analyze(atlas, preds, word_count=CFG.speech_min_words - 1).speech_detected
    assert _analyze(atlas, preds, word_count=CFG.speech_min_words).speech_detected


def test_insights_are_deterministic(atlas, make_preds):
    preds = make_preds(15, _all_channels(np.cos(np.arange(15))))
    assert _analyze(atlas, preds) == _analyze(atlas, preds)
