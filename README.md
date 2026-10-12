# Reel Brain Report

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ammarahmad1/reel-brain-analysis/blob/main/notebooks/reel_brain_report.ipynb)

Run a short video through Meta FAIR's [TRIBE v2](https://github.com/facebookresearch/tribev2) and get a
second-by-second report on how an average brain is predicted to respond to it:

- a timeline of the overall response and four channels: visuals, faces, sound and speech
- how strong the hook is, where the reel dips, and which channel carries it
- three concrete things to fix
- brain heatmaps for the whole reel, the hook, the peak and the deepest dip

**Viewer:** [reel-brain-analysis.vercel.app](https://reel-brain-analysis.vercel.app) · [sample report](https://reel-brain-analysis.vercel.app/report/sample)

Everything runs on Google Colab's free GPU. The report opens in your browser; your video never leaves your
Colab session.

## Make a report

You'll need a Google account and a Hugging Face account.

1. **One time:** request access to [Llama 3.2 3B](https://huggingface.co/meta-llama/Llama-3.2-3B) (TRIBE v2
   uses it for the spoken words). Approval usually takes minutes to a few hours. Then create a **Read** token at
   [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
2. Open the notebook in Colab (badge above), set the runtime to **T4 GPU**, and add your token as a Colab
   secret named `HF_TOKEN`.
3. Run the cells one at a time and pick your reel (60 seconds max). A 20-second reel takes about 15–20
   minutes on the free T4; a full minute can take 40 or more.
4. Download `report.zip` and drop it on the [report viewer](https://reel-brain-analysis.vercel.app).

## How the report is made

TRIBE v2 predicts fMRI responses at 20,484 points on the cortex (fsaverage5), one row per second. The
`reel_report` package averages those points over regions of the Destrieux atlas, turns each channel into
within-reel z-scores, and applies a fixed set of rules for the hook, dips, carrier and fixes. There's no
language model in the loop, so the same reel always gives the same report.

The exact regions, thresholds and rules are in [docs/report-methodology.md](docs/report-methodology.md).

Scores compare moments **within one reel**. "Weak hook" means weaker than the rest of that reel, not weaker
than other people's reels.

## Repo layout

```
notebooks/reel_brain_report.ipynb   the Colab notebook
packages/report/                    reel_report: TRIBE output → report.json + heatmaps
packages/report-schema/             JSON Schema for report.json
apps/web/                           Next.js report viewer (runs entirely in the browser)
tests/fixtures/spike_t4_22s/        real TRIBE v2 output for a 22.6 s reel, used in tests
scripts/build_sample_report.py      rebuilds the viewer's sample report from the fixture
docs/report-methodology.md          how every number in the report is computed
```

## Development

Report package (Python 3.11+, CPU only):

```sh
python -m venv .venv
.venv/bin/pip install -e "packages/report[test]"     # .venv\Scripts\pip on Windows
cd packages/report && ../../.venv/bin/pytest
```

Viewer:

```sh
cd apps/web
npm install
npm run dev            # http://localhost:3000
npm run gen:types      # after changing packages/report-schema
```

The viewer is a static Next.js site, so it can be hosted for free (for example on Vercel with `apps/web` as the
root directory).

## Licenses and credits

- This repository's code is under the [MIT License](LICENSE).
- **TRIBE v2** is by Meta FAIR and licensed [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/):
  **non-commercial use only.** The notebook downloads it; it isn't included here.
- **Llama 3.2** is used under the [Llama 3.2 Community License](https://www.llama.com/llama3_2/license/).
  Built with Llama.
- Brain atlas: Destrieux et al. (2010), via [nilearn](https://nilearn.github.io).

Anyone running the notebook is responsible for following the model licenses. This project isn't affiliated
with or endorsed by Meta.
