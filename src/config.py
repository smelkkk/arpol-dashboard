"""
config.py — Global constants, paths, and colour system for the ARPOL dashboard.
"""

import os
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent          # arpol-dashboard/
DATA_RAW       = ROOT / "data" / "raw"
DATA_ASSUMP    = ROOT / "data" / "assumptions"
DATA_OUTPUTS   = ROOT / "data" / "outputs"
EXCEL_MODEL    = DATA_RAW / "ARPOL_TCO_Model.xlsx"
CAPEX_JSON     = DATA_ASSUMP / "capex_benchmarks.json"
DEFAULTS_JSON  = DATA_ASSUMP / "scenario_defaults.json"

# ── Dashboard metadata ─────────────────────────────────────────────────────
DASHBOARD_TITLE = "ARPOL — Laser-Cutting Investment Decision"
VERSION         = "1.0.0"
PROJECT_YEAR    = 2026
DEADLINE        = ""

# ── Scenario identifiers ───────────────────────────────────────────────────
SCENARIO_OUTSOURCE = "outsource"
SCENARIO_EU        = "eu_insource"
SCENARIO_CHINA     = "china_insource"
SCENARIOS          = [SCENARIO_OUTSOURCE, SCENARIO_EU, SCENARIO_CHINA]

# ── Colour palette ─────────────────────────────────────────────────────────
COLORS = {
    "outsource"    : "#E74C3C",   # red — status-quo / cost
    "eu_insource"  : "#2980B9",   # blue — EU scenario
    "china_insource": "#27AE60",  # green — China scenario
    "positive"     : "#1E8449",   # dark green — savings / good
    "negative"     : "#C0392B",   # dark red — cost / risk
    "neutral"      : "#7F8C8D",   # grey — neutral
    "background"   : "#F4F6F8",   # page background
    "card_bg"      : "#FFFFFF",   # KPI card background
    "primary"      : "#1B2A4A",   # navy — header text
    "accent"       : "#E67E22",   # amber — warnings, placeholders
    "border"       : "#D5DBDB",   # table/card borders
}

# Plotly colour list for multi-scenario charts
SCENARIO_COLORS = [
    COLORS["outsource"],
    COLORS["eu_insource"],
    COLORS["china_insource"],
]

PLOTLY_TEMPLATE = "plotly_white"

# ── Model horizons ─────────────────────────────────────────────────────────
ANALYSIS_YEARS = 5          # 5-year TCO horizon
YEAR_RANGE     = list(range(ANALYSIS_YEARS + 1))   # [0, 1, 2, 3, 4, 5]
YEAR_LABELS    = [f"Year {y}" for y in YEAR_RANGE]

# ── Sensitivity sweep parameters ───────────────────────────────────────────
SENSITIVITY_DELTA = 0.20    # ±20% for tornado analysis
HEATMAP_VOLUME_STEPS = 8
HEATMAP_CAPEX_STEPS  = 8

# ── Monte Carlo ────────────────────────────────────────────────────────────
MC_SIMULATIONS = 10_000
MC_SEED        = 42

# ── Currency formatting helper ─────────────────────────────────────────────
def fmt_eur(value: float, decimals: int = 0) -> str:
    """Format a number as a Euro string with thousands separator."""
    if value is None:
        return "n/a"
    sign = "-" if value < 0 else ""
    abs_val = abs(value)
    if abs_val >= 1_000_000:
        return f"{sign}€{abs_val/1_000_000:.2f}M"
    elif abs_val >= 1_000:
        return f"{sign}€{abs_val/1_000:,.{decimals}f}K"
    else:
        return f"{sign}€{abs_val:,.{decimals}f}"

def fmt_pct(value: float, decimals: int = 1) -> str:
    """Format a float as a percentage string."""
    if value is None:
        return "n/a"
    return f"{value * 100:.{decimals}f}%"
