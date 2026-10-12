import numpy as np
import pytest

from reel_report.atlas import N_VERTICES_PER_HEMI
from reel_report.config import CHANNEL_REGIONS
from reel_report.timeline import build_timeline, zscore


def test_atlas_matches_tribe_layout(atlas):
    assert atlas.labels.shape == (2 * N_VERTICES_PER_HEMI,)
    for regions in CHANNEL_REGIONS.values():
        assert atlas.mask(regions).any()
    medial = atlas.names.index("Medial_wall")
    assert not atlas.cortex_mask[atlas.labels == medial].any()


def test_unknown_region_raises(atlas):
    with pytest.raises(KeyError):
        atlas.mask(["Not_a_region"])


def test_channel_series_recovered(atlas, make_preds):
    visual = np.sin(np.arange(10))
    preds = make_preds(10, {"visual": visual})
    tl = build_timeline(preds, range(10), 10.0, atlas, CHANNEL_REGIONS)
    assert np.corrcoef(tl.channels["visual"], visual)[0, 1] > 0.99
    assert abs(np.corrcoef(tl.channels["speech"], visual)[0, 1]) < 0.9


def test_seconds_come_from_segment_starts(atlas, make_preds):
    starts = [0.0, 1.0, 3.0, 4.0, 5.0]  # second 2 dropped by TRIBE (no events)
    tl = build_timeline(make_preds(5, {}), starts, 4.5, atlas, CHANNEL_REGIONS)
    assert tl.seconds.tolist() == [0, 1, 3, 4]  # start 5.0 is past the video end
    assert tl.preds.shape[0] == 4


def test_shape_mismatches_raise(atlas, make_preds):
    with pytest.raises(ValueError):
        build_timeline(make_preds(3, {}), [0.0, 1.0], 3.0, atlas, CHANNEL_REGIONS)
    with pytest.raises(ValueError):
        build_timeline(np.zeros((3, 100)), [0.0, 1.0, 2.0], 3.0, atlas, CHANNEL_REGIONS)


def test_zscore_flat_is_zero():
    assert zscore(np.ones(5)).tolist() == [0.0] * 5
