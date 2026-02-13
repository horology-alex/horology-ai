# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run locally (port 5001)
pip install -r requirements.txt
python api.py

# Run with gunicorn (production-style)
gunicorn api:app
```

## Deployment (Railway)

1. Push repo to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Select the repo — Railway auto-detects the `Procfile`
4. App will be live at a `*.up.railway.app` URL

The `Procfile` contains: `web: gunicorn api:app`

## Architecture

Two files run the entire app:

- **[api.py](api.py)** — Flask server. Loads `data/pricing_model.pkl` and `data/encoders.json` at startup. Exposes `/` (serves `index.html`), `/api/models` (returns all Rolex model names), and `/api/predict` (takes watch params, returns price estimate + charts data).
- **[index.html](index.html)** — Self-contained Bloomberg-terminal-style frontend. Vanilla JS + Chart.js. Calls the two API endpoints above.

## Model & feature schema

`data/pricing_model.pkl` is a RandomForest trained on a small dataset (Submariner watches). Feature vector: `[año, caja, papeles, rayaduras=0, pulido=0, estado_num, material_num, es_hulk, es_kermit]`

`api.py` maps frontend inputs to these features:
- `estado` string → `estado_num` via `ESTADO_MAP` (Unworn=3, Very good=2, Good=1, Fair=0)
- `material` string → `material_num` (gold types=1, Gold/Steel=2, rest=0)
- `modelo` string → `es_hulk` / `es_kermit` flags via substring match

`data/encoders.json` holds the full list of Rolex model/condition/material names (used only for populating dropdowns via `/api/models`).
`data/dataset_stats.json` holds global dataset stats (81,725 watches) used in the response payload.

## After every change

After making any change to the repo, always:
1. Update `CHANGELOG.md` — add an entry under today's date describing what changed and why
2. Update `GUIDE.md` if any files were added, removed, or their purpose changed

## Data files (all committed, no large files)

| File | Size | Purpose |
|---|---|---|
| `data/pricing_model.pkl` | 0.1 MB | Loaded by `api.py` at startup |
| `data/encoders.json` | ~3 KB | Model/condition/material label lists |
| `data/dataset_stats.json` | ~100 B | Global stats shown in UI |
