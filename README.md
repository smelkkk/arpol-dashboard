# ARPOL — Laser-Cutting Investment Decision Dashboard

An interactive Streamlit dashboard that supports ARPOL's decision on whether to bring laser cutting in-house. It was built for the ESADE MSc Consulting course, Challenge 4: *Production Improvement & Laser-Cutting Investment Assessment*.

ARPOL currently subcontracts laser-cut parts (about €105k/year in 2026) and forms them on a 25-year-old press. The dashboard compares the total cost of ownership (TCO) of three options over a multi-year horizon and shows how robust the answer is to the underlying assumptions.

## Scenarios compared

| Scenario | Description |
|---|---|
| **Outsource** (status quo) | Keep subcontracting and keep running the existing press |
| **EU in-source** | Buy a European laser cutter (Trumpf / Bystronic archetype) |
| **China in-source** | Buy a Chinese laser cutter (Bodor / HSG archetype) |

## Features

- **Home**: headline KPIs (CAPEX, payback, ROI, NPV, working-capital release), cumulative cash flow, TCO comparison and cumulative savings charts over a 9-year horizon.
- **Scenario Comparison**: side-by-side TCO and CAPEX breakdowns for each scenario.
- **Sensitivity Analysis**: tornado chart (±20%), payback heatmaps and subcontract-spend sensitivity.
- **Working Capital**: SKU rationalisation and the one-time inventory release it produces.
- **Machine Selector**: browse the EU and China machine options and see their effect on CAPEX and payback.
- **Assumptions Register**: audit trail of every model input, with source and validation status (confirmed vs. placeholder).
- **Sidebar controls**: override key assumptions live, including the number of machines (scales CAPEX and OpEx), and switch language (i18n).

## Getting started

Requires Python 3.10+.

```bash
git clone https://github.com/smelkkk/arpol-dashboard.git
cd arpol-dashboard
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run Home.py
```

The app opens at http://localhost:8501.

## Project structure

```
Home.py                  Landing page / entry point
pages/                   Streamlit multipage views (01–05)
components/              UI building blocks: sidebar, KPI cards, Plotly charts
src/
  tco_engine.py          Core TCO / cash-flow / payback calculations (pure functions)
  sensitivity.py         Tornado, heatmap and one-way sensitivity analysis
  working_capital.py     SKU rationalisation and working-capital release
  assumptions.py         Loads defaults and merges user overrides
  i18n.py                Translations
  config.py              Paths, scenario IDs, colour palette, horizons
data/
  assumptions/           scenario_defaults.json, capex_benchmarks.json
  raw/                   ARPOL_TCO_Model.xlsx (source Excel model)
.streamlit/config.toml   Theme and server settings
```

## Data and assumptions

All inputs live in [data/assumptions/scenario_defaults.json](data/assumptions/scenario_defaults.json) and [data/assumptions/capex_benchmarks.json](data/assumptions/capex_benchmarks.json). Each value carries a unit, source and status (`CONFIRMED` or placeholder). Client-confirmed actuals are as of June 2026. Values that are still placeholders trigger a warning banner in the app, and the Assumptions Register lists them.

The calculation engine in `src/tco_engine.py` has no Streamlit dependency, so it can be tested or reused on its own.

## Tech stack

Streamlit, pandas, NumPy, SciPy, Plotly, openpyxl.

## Credits

ARPOL × ESADE Consulting Team, 2026.
