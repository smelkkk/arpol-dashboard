"""
sensitivity.py — Sensitivity and risk analysis for the ARPOL TCO model.

Three analysis types:
    1. Tornado chart  — one-at-a-time ±DELTA swing on EU payback
    2. Payback heatmap — 2D grid: volume growth × CAPEX level
    3. One-way table  — any variable swept across a range
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from copy import deepcopy

from src.tco_engine import (
    compute_scenario_cashflows,
    compute_payback_year,
    compute_5yr_savings,
    build_summary_kpis,
)
from src.config import SENSITIVITY_DELTA, HEATMAP_VOLUME_STEPS, HEATMAP_CAPEX_STEPS


# ── Helpers ────────────────────────────────────────────────────────────────

def _payback(a: dict, scenario: str) -> float:
    """Run full model and return payback year for `scenario`. Returns 6 if no payback."""
    df = compute_scenario_cashflows(a)
    pb = compute_payback_year(df, scenario)
    return float(pb) if pb is not None else 6.0   # 6 = "beyond 5 years"


def _savings_5yr(a: dict, scenario: str) -> float:
    """Return 5-year cumulative savings vs outsourcing (continuous € metric)."""
    df = compute_scenario_cashflows(a)
    return compute_5yr_savings(df)[scenario]


# ══════════════════════════════════════════════════════════════════════════════
# 1. TORNADO ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

# Variables to include in the tornado, with display labels and delta overrides
TORNADO_VARIABLES = [
    {
        "key"           : "subcontract_annual_spend",
        "label_en"      : "Subcontract Annual Spend",
        "label_es"      : "Gasto Anual en Subcontrato",
        "delta"         : SENSITIVITY_DELTA,
        "format"        : "eur",
    },
    {
        "key"           : "volume_growth_rate",
        "label_en"      : "Volume Growth Rate",
        "label_es"      : "Tasa Crecimiento Volumen",
        "delta"         : SENSITIVITY_DELTA,
        "format"        : "pct",
    },
    {
        "key"           : "eu_equipment_cost",
        "label_en"      : "EU Equipment Cost",
        "label_es"      : "Costo Equipo UE",
        "delta"         : SENSITIVITY_DELTA,
        "format"        : "eur",
    },
    {
        "key"           : "china_equipment_cost",
        "label_en"      : "China Equipment Cost",
        "label_es"      : "Costo Equipo China",
        "delta"         : SENSITIVITY_DELTA,
        "format"        : "eur",
    },
    {
        "key"           : "num_operators",
        "label_en"      : "Operators Required",
        "label_es"      : "Operadores Requeridos",
        "delta"         : 1.0,          # absolute: +1 / -0 (min 1)
        "format"        : "int",
        "abs_delta"     : 1,            # add/subtract 1 operator
    },
    {
        "key"           : "annual_hours",
        "label_en"      : "Annual Operating Hours",
        "label_es"      : "Horas Operativas Anuales",
        "delta"         : SENSITIVITY_DELTA,
        "format"        : "int",
    },
    {
        "key"           : "eu_maintenance_pct",
        "label_en"      : "EU Maintenance % CAPEX",
        "label_es"      : "Mantenimiento UE % CAPEX",
        "delta"         : SENSITIVITY_DELTA,
        "format"        : "pct",
    },
    {
        "key"           : "china_maintenance_pct",
        "label_en"      : "China Maintenance % CAPEX",
        "label_es"      : "Mantenimiento China % CAPEX",
        "delta"         : SENSITIVITY_DELTA,
        "format"        : "pct",
    },
    {
        "key"           : "press_annual_opex",
        "label_en"      : "Press Annual OpEx",
        "label_es"      : "OpEx Prensa Anual",
        "delta"         : SENSITIVITY_DELTA,
        "format"        : "eur",
    },
    {
        "key"           : "electricity_rate",
        "label_en"      : "Electricity Rate",
        "label_es"      : "Tarifa Eléctrica",
        "delta"         : SENSITIVITY_DELTA,
        "format"        : "eur",
    },
]


def run_tornado(base_assumptions: dict, scenario: str = "eu_insource") -> pd.DataFrame:
    """
    Run one-at-a-time sensitivity for all TORNADO_VARIABLES.

    Metric: 5-year cumulative savings vs outsourcing (continuous €).
    Using a continuous metric avoids the flat-bar problem that arises
    when discrete payback years don't cross integer boundaries on ±20% swings.

    For each variable:
      - savings_effect_high = savings(high value) − savings(base)
      - savings_effect_low  = savings(low value)  − savings(base)
    Positive effect = variable increase HELPS the insource case.
    Negative effect = variable increase HURTS the insource case.

    Returns a DataFrame sorted by total impact magnitude (largest first).
    """
    base_savings = _savings_5yr(base_assumptions, scenario)
    base_payback = _payback(base_assumptions, scenario)
    rows = []

    for var in TORNADO_VARIABLES:
        key      = var["key"]
        base_val = base_assumptions.get(key, 0)

        # ── Determine high / low values ────────────────────────────────
        if "abs_delta" in var:
            val_high = base_val + var["abs_delta"]
            val_low  = max(1, base_val - var["abs_delta"])
        else:
            pct      = var["delta"]
            val_high = base_val * (1 + pct)
            val_low  = base_val * (1 - pct)

        # ── Run high scenario ──────────────────────────────────────────
        a_high             = deepcopy(base_assumptions)
        a_high[key]        = val_high
        savings_high       = _savings_5yr(a_high, scenario)
        effect_high        = savings_high - base_savings   # + = better, − = worse

        # ── Run low scenario ───────────────────────────────────────────
        a_low              = deepcopy(base_assumptions)
        a_low[key]         = val_low
        savings_low        = _savings_5yr(a_low, scenario)
        effect_low         = savings_low - base_savings

        # Total swing = spread between high and low outcomes
        impact             = abs(savings_high - savings_low)

        rows.append({
            "key"            : key,
            "label_en"       : var["label_en"],
            "label_es"       : var["label_es"],
            "base_value"     : base_val,
            "val_low"        : val_low,
            "val_high"       : val_high,
            "savings_base"   : base_savings,
            "savings_high"   : savings_high,
            "savings_low"    : savings_low,
            "effect_high"    : effect_high,   # € change vs base when var goes UP
            "effect_low"     : effect_low,    # € change vs base when var goes DOWN
            "payback_base"   : base_payback,
            "impact"         : impact,        # total swing in € (used for sort)
            "format"         : var["format"],
        })

    df = pd.DataFrame(rows).sort_values("impact", ascending=False).reset_index(drop=True)
    return df


# ══════════════════════════════════════════════════════════════════════════════
# 2. PAYBACK HEATMAP
# ══════════════════════════════════════════════════════════════════════════════

def compute_payback_heatmap(
    base_assumptions: dict,
    scenario: str,
    volume_growth_range: tuple[float, float] = (0.05, 0.25),
    capex_pct_range:     tuple[float, float] = (0.60, 1.40),
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute 2D payback heatmap.

    X-axis: volume_growth_rate from min to max
    Y-axis: CAPEX multiplier applied to the relevant equipment cost

    Returns:
        vol_grid   — 1D array of volume growth values
        capex_grid — 1D array of CAPEX multiplier values
        payback_matrix — 2D array [capex_steps × vol_steps]
    """
    vol_grid   = np.linspace(*volume_growth_range, HEATMAP_VOLUME_STEPS)
    capex_grid = np.linspace(*capex_pct_range,     HEATMAP_CAPEX_STEPS)

    capex_key = "eu_equipment_cost" if scenario == "eu_insource" else "china_equipment_cost"
    base_capex = base_assumptions[capex_key]

    matrix = np.zeros((len(capex_grid), len(vol_grid)))
    for i, capex_mult in enumerate(capex_grid):
        for j, vol_growth in enumerate(vol_grid):
            a = deepcopy(base_assumptions)
            a["volume_growth_rate"] = vol_growth
            a[capex_key]            = base_capex * capex_mult
            # Recompute derived (China landed cost depends on equipment cost)
            if scenario == "china_insource":
                a["china_landed_cost"] = (
                    a["china_equipment_cost"] * (1 + a["china_duty_pct"]) + a["china_freight"]
                )
            matrix[i, j] = _payback(a, scenario)

    return vol_grid, capex_grid, matrix


# ══════════════════════════════════════════════════════════════════════════════
# 3. ONE-WAY SENSITIVITY TABLE
# ══════════════════════════════════════════════════════════════════════════════

def one_way_sensitivity(
    base_assumptions: dict,
    variable_key: str,
    values: list[float],
    scenarios: list[str] | None = None,
) -> pd.DataFrame:
    """
    Sweep `variable_key` across `values` and return a DataFrame of
    payback periods per scenario.

    Useful for building a line chart of how payback changes with a variable.
    """
    if scenarios is None:
        scenarios = ["eu_insource", "china_insource"]

    rows = []
    for val in values:
        a = deepcopy(base_assumptions)
        a[variable_key] = val
        row = {variable_key: val}
        for s in scenarios:
            row[s] = _payback(a, s)
        rows.append(row)

    return pd.DataFrame(rows)


# ══════════════════════════════════════════════════════════════════════════════
# 4. SUBCONTRACT SENSITIVITY (high-priority standalone)
# ══════════════════════════════════════════════════════════════════════════════

def subcontract_sensitivity(base_assumptions: dict) -> pd.DataFrame:
    """
    Test how robust the recommendation is if subcontract spend is
    -30% to +30% of the base case.
    Returns EU and China payback across 7 subcontract scenarios.
    """
    base_spend = base_assumptions["subcontract_annual_spend"]
    multipliers = [0.70, 0.80, 0.90, 1.00, 1.10, 1.20, 1.30]
    rows = []
    for m in multipliers:
        a = deepcopy(base_assumptions)
        a["subcontract_annual_spend"] = base_spend * m
        rows.append({
            "Subcontract Multiplier"  : m,
            "Subcontract Spend (€/yr)": round(base_spend * m),
            "EU Payback (yrs)"        : _payback(a, "eu_insource"),
            "China Payback (yrs)"     : _payback(a, "china_insource"),
        })
    return pd.DataFrame(rows)
