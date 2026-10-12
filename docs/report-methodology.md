# Report methodology

This document describes how `packages/report` turns TRIBE v2 output into the report. The
thresholds referenced here live in `packages/report/src/reel_report/config.py`. If you change
one there, change it here too.

## Input

- `preds`: `(T, 20484)` float array from `TribeModel.predict`, on fsaverage5. The **left
  hemisphere comes first** (`[:10242]`), matching tribev2's own plotting code.
- `segment_starts`: `segment.start` for each row. TR is 1 s.
- `word_count`: the number of `Word` rows in the events dataframe (whisperx transcript).

## Timing

TRIBE v2 is trained with `data.neuro.offset: 5.0`, which pairs each stimulus second with the
brain response 5 s later. As a result, **row i already means "the response to video second
i"**, and we apply no further shift. This is confirmed on the spike fixture: the only spoken
words ("Purple rain", 9.0–10.3 s) coincide with the speech channel's spike at second 9.

TRIBE drops segments that contain no events, so seconds always come from `segment.start` and
never from the row index. Rows that start after the end of the video are discarded.

## Channels

Each channel is the mean prediction over the vertices of its Destrieux regions:

| Channel | Destrieux regions |
|---|---|
| visual | S_calcarine, G_cuneus, Pole_occipital, G_occipital_sup, G_occipital_middle, G_and_S_occipital_inf |
| faces | G_oc-temp_lat-fusifor |
| sound | G_temp_sup-G_T_transv, S_temporal_transverse, G_temp_sup-Plan_tempo |
| speech | G_temp_sup-Lateral, S_temporal_sup, G_front_inf-Opercular, G_front_inf-Triangul |

**Overall** is the mean over all cortex, excluding `Medial_wall` and `Unknown`.

These region sets are coarse proxies. The "faces" channel in particular uses the whole
fusiform gyrus, not a localized FFA. tribev2 also ships HCP-MMP atlas helpers, which may give
finer channels later.

## Normalization

All scores are **within-reel z-scores**: `(x − mean) / std` over the reel's own seconds. A
"weak hook" therefore means weak *compared with the rest of this reel*, not compared with
other reels. Comparing across reels would need a reference set of reels to calibrate against.
We don't have one yet.

## Insights

| Insight | Rule | Default |
|---|---|---|
| Hook | mean overall z over `[0, hook_s)` | `hook_s = 3` |
| Ending | mean overall z over the last `ending_s` seconds | `ending_s = 3` |
| Rating | strong if z ≥ `strong_z`, weak if z ≤ `weak_z`, else average | `0.5` / `−0.5` |
| Dips | runs of consecutive seconds with overall z ≤ `dip_z`, lasting ≥ `dip_min_s`; deepest `max_dips` kept | `−0.75`, `2`, `3` |
| Dip cause | the channel with the lowest mean z during the dip (speech is excluded if the reel has no speech) | |
| Peak / low | seconds with the highest / lowest overall z | |
| Carrier | the channel whose raw timeline correlates best with overall, if r ≥ `carrier_min_r`; otherwise none | `0.5` |
| Speech detected | word count ≥ `speech_min_words` | `5` |

## Fixes

The rules emit candidates with a priority. The top `max_fixes` (3) are kept. Rule order breaks
ties, so the output is deterministic.

| Fix | When | Priority |
|---|---|---|
| Strengthen the first N seconds | hook weak | 100 + 10·\|z\| |
| Channel-specific dip fix | one per dip (up to 2 deepest), skipped if inside a weak hook | 80 + 10·\|z\| |
| End on a stronger beat | ending weak | 60 + 10·\|z\| |
| Consider a voiceover | no speech detected | 50 |
| Make the first N seconds stand out | hook average and peak outside hook | 30 |
| Lean into <channel> | always (carrier, or the closest channel) | 20 / 6 |
| Build around your peak | always | 10 |
| Tighten around the weakest second | unless a dip already covers it | 8 |

The last three always apply, so every report has exactly 3 fixes.

## Heatmaps

Lateral left/right views on the inflated fsaverage5 surface, rendered with nilearn. The images
are: the whole-reel average, the hook window average, the peak second, and the deepest dip's
lowest second. All of them share one symmetric colour scale (99th percentile of |preds|), so
they can be compared. Values below 15% of that scale are hidden, so the anatomy shows through.
The images show **raw** predictions, not z-scores.

## Known limitations

- The first seconds have less temporal context, because the video features use 4 s clips. The
  hook score may be slightly biased by this. This needs checking against more reels.
- The rules were tuned on one music reel. Validate them on a speech-heavy reel and a few
  others before launch.
