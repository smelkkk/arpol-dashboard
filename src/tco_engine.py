"""
tco_engine.py — Core financial calculation engine for the ARPOL TCO model.

Pure functions only — no Streamlit imports, no side effects.
All functions take an `assumptions` dict and return numerical outputs.

Scenarios:
    outsource    → continue subcontracting + operate 25-yr press
    eu_insource  → buy EU laser cutter (Trumpf/Bystronic archetype)
    china_insource → buy Chinese laser cutter (Bodor/HSG archetype)
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from src.config import ANALYSIS_YEARS, YEAR_RANGE


# ══════════════════════════════════════════════════════════════════════════════
# CAPEX CALCULATIONS
# ══════════════════════════════════════════════════════════════════════════════

def compute_eu_capex_breakdown(a: dict) -> dict:
    """
    Return Year-0 EU CAPEX line-by-line breakdown.
    All values are positive (costs); sign applied at cashflow level.
    """
    n           = a.get("num_machines", 1)
    equip       = a["eu_equipment_cost"]
    install     = equip * a["eu_install_pct"]
    commission  = equip * a["eu_commissioning_pct"]
    training    = a["eu_training_cost"]
    tooling     = a["eu_tooling_cost"]
    spares      = a["eu_spares_buffer"]
    ancillary   = a["eu_ancillary_cost"]
    per_machine = equip + install + commission + training + tooling + spares + ancillary
    total       = per_machine * n
    return {
        "Equipment"                : equip * n,
        "Installation"             : install * n,
        "Commissioning"            : commission * n,
        "Training"                 : training * n,
        "Tooling & Fixtures"       : tooling * n,
        "Spare Parts Buffer"       : spares * n,
        "Ancillary (extraction/chiller)" : ancillary * n,
        "Total CAPEX"              : total,
    }


def compute_china_capex_breakdown(a: dict) -> dict:
    """
    Return Year-0 China CAPEX line-by-line breakdown.
    """
    n           = a.get("num_machines", 1)
    equip       = a["china_equipment_cost"]
    duty        = equip * a["china_duty_pct"]
    freight     = a["china_freight"]
    install     = equip * a["china_install_pct"]
    commission  = equip * a["china_commissioning_pct"]
    training    = a["china_training_cost"]
    tooling     = a["china_tooling_cost"]
    spares      = a["china_spares_buffer"]
    ancillary   = a["china_ancillary_cost"]
    per_machine = equip + duty + freight + install + commission + training + tooling + spares + ancillary
    total       = per_machine * n
    return {
        "Equipment (ex-works)"     : equip * n,
        "Import Duty (4.5% MFN)"   : duty * n,
        "Freight (China → Spain)"  : freight * n,
        "Installation"             : install * n,
        "Commissioning"            : commission * n,
        "Training"                 : training * n,
        "Tooling & Fixtures"       : tooling * n,
        "Spare Parts Buffer"       : spares * n,
        "Ancillary (extraction/chiller)" : ancillary * n,
        "Total CAPEX"              : total,
    }


def get_total_capex(a: dict, scenario: str) -> float:
    """Return total Year-0 CAPEX for eu_insource or china_insource (positive number)."""
    if scenario == "eu_insource":
        return compute_eu_capex_breakdown(a)["Total CAPEX"]
    elif scenario == "china_insource":
        return compute_china_capex_breakdown(a)["Total CAPEX"]
    return 0.0


# ══════════════════════════════════════════════════════════════════════════════
# ANNUAL OPERATING COST CALCULATIONS
# ══════════════════════════════════════════════════════════════════════════════

def compute_annual_insource_opex(a: dict, scenario: str, year: int) -> dict:
    """
    Return annual operating cost breakdown for year `year` (1-indexed).
    Inflation applied to labour and consumables; maintenance based on original CAPEX.
    Returns a dict of line items (all positive = costs).
    """
    inf = (1 + a["inflation_rate"]) ** (year - 1)
    n   = a.get("num_machines", 1)

    # Energy: hours × power × rate (inflated) — scales with machines
    energy = a["annual_hours"] * a["laser_power_kw"] * a["electricity_rate"] * inf * n

    # Consumables: per-hour rate (inflated) — scales with machines
    consumables = a["annual_hours"] * a["consumables_per_hr"] * inf * n

    # Maintenance: % of equipment cost only, inflated annually — scales with machines
    maint_pct = a["eu_maintenance_pct"] if scenario == "eu_insource" else a["china_maintenance_pct"]
    equip_cost = a["eu_equipment_cost"] if scenario == "eu_insource" else a["china_equipment_cost"]
    maintenance = equip_cost * maint_pct * inf * n

    # Labour: 1 operator per machine per shift (inflated)
    labour = a["operator_wage"] * n * inf

    total = energy + consumables + maintenance + labour
    return {
        "Energy"           : energy,
        "Consumables"      : consumables,
        "Maintenance"      : maintenance,
        "Labour"           : labour,
        "Total OpEx"       : total,
    }


def compute_annual_outsource_cost(a: dict, year: int) -> dict:
    """
    Return annual cost breakdown for the outsource scenario in year `year`.
    Subcontract spend grows with volume (revenue proxy).
    Convention: Year 1 = base rate; growth compounds from Year 2 onward.
    This matches the Excel model's Current State tab.
    Press OpEx and scrap inflate starting from Year 2.
    """
    vol_growth = (1 + a["volume_growth_rate"]) ** (year - 1)  # Year 1 = base, Year 2 = ×1.15
    inf        = (1 + a["inflation_rate"])      ** (year - 1)  # Year 1 = base, Year 2 inflated

    subcontract = a["subcontract_annual_spend"] * vol_growth
    press_opex  = a["press_annual_opex"]        * inf
    logistics   = a.get("logistics_cost", 0)    * inf
    scrap_rework= a["scrap_rework_cost"]        * inf
    total       = subcontract + press_opex + logistics + scrap_rework
    return {
        "Subcontract Laser-Cutting" : subcontract,
        "Press Operational Cost"    : press_opex,
        "Logistics (subcontract)"   : logistics,
        "Scrap & Rework"            : scrap_rework,
        "Total Cost"                : total,
    }


# ══════════════════════════════════════════════════════════════════════════════
# SCENARIO CASHFLOW TABLES
# ══════════════════════════════════════════════════════════════════════════════

def compute_scenario_cashflows(a: dict) -> pd.DataFrame:
    """
    Compute annual and cumulative cash flows for all three scenarios.
    Returns a DataFrame with columns:
        year | outsource | eu_insource | china_insource
        (negative = cash outflow)

    Also computes cumulative columns and savings-vs-outsource columns.
    """
    rows = []
    for yr in YEAR_RANGE:
        row = {"year": yr}

        # ── Outsource ──────────────────────────────────────────────────
        if yr == 0:
            row["outsource"] = 0.0
        else:
            row["outsource"] = -compute_annual_outsource_cost(a, yr)["Total Cost"]

        # ── EU Insource ────────────────────────────────────────────────
        if yr == 0:
            row["eu_insource"] = -get_total_capex(a, "eu_insource")
        else:
            row["eu_insource"] = -compute_annual_insource_opex(a, "eu_insource", yr)["Total OpEx"]

        # ── China Insource ─────────────────────────────────────────────
        if yr == 0:
            row["china_insource"] = -get_total_capex(a, "china_insource")
        else:
            row["china_insource"] = -compute_annual_insource_opex(a, "china_insource", yr)["Total OpEx"]

        rows.append(row)

    df = pd.DataFrame(rows)

    # Cumulative positions
    for col in ["outsource", "eu_insource", "china_insource"]:
        df[f"{col}_cumul"] = df[col].cumsum()

    # Cumulative savings vs outsourcing (positive = insource is better overall).
    # Logic: insource_cumul - outsource_cumul
    #   Year 0: EU(-371K) - 0 = -371K  → EU has spent more (CAPEX upfront)
    #   Year 3: EU(-582K) - Outsource(-709K) = +127K → EU cumulative is now cheaper
    # Matches Excel TCO Comparison "savings" rows.
    df["eu_insource_savings_cumul"]    = df["eu_insource_cumul"]    - df["outsource_cumul"]
    df["china_insource_savings_cumul"] = df["china_insource_cumul"] - df["outsource_cumul"]
    # Short-form aliases used by chart components
    df["eu_savings_cumul"]    = df["eu_insource_savings_cumul"]
    df["china_savings_cumul"] = df["china_insource_savings_cumul"]

    return df


# ══════════════════════════════════════════════════════════════════════════════
# KPI COMPUTATIONS
# ══════════════════════════════════════════════════════════════════════════════

def compute_payback_year(df: pd.DataFrame, scenario: str) -> int | None:
    """
    Return the first year where cumulative savings vs outsourcing turn positive.
    Returns None if payback doesn't occur within the analysis horizon.
    """
    savings_col = f"{scenario}_savings_cumul"
    positive = df[df[savings_col] > 0]
    if positive.empty:
        return None
    return int(positive["year"].iloc[0])


def compute_5yr_totals(df: pd.DataFrame) -> dict:
    """Return 5-year cumulative totals for each scenario (Year 0–5)."""
    last = df[df["year"] == ANALYSIS_YEARS].iloc[0]
    return {
        "outsource"    : last["outsource_cumul"],
        "eu_insource"  : last["eu_insource_cumul"],
        "china_insource": last["china_insource_cumul"],
    }


def compute_5yr_savings(df: pd.DataFrame) -> dict:
    """Return 5-year cumulative savings vs outsourcing for each insource scenario."""
    last = df[df["year"] == ANALYSIS_YEARS].iloc[0]
    return {
        "eu_insource"   : last["eu_savings_cumul"],
        "china_insource": last["china_savings_cumul"],
    }


def compute_roi(a: dict, df: pd.DataFrame) -> dict:
    """Return simple 5-year ROI = 5yr savings / CAPEX for each insource scenario."""
    savings = compute_5yr_savings(df)
    eu_capex    = get_total_capex(a, "eu_insource")
    china_capex = get_total_capex(a, "china_insource")
    return {
        "eu_insource"   : savings["eu_insource"]    / eu_capex    if eu_capex    > 0 else None,
        "china_insource": savings["china_insource"] / china_capex if china_capex > 0 else None,
    }


def compute_npv(a: dict, df: pd.DataFrame) -> dict:
    """
    Compute NPV of incremental cash flows (insource vs outsource) at WACC.
    Positive NPV = insource creates more value than outsourcing.
    """
    r = a["discount_rate"]
    npvs = {}
    for scenario in ["eu_insource", "china_insource"]:
        # Incremental cash flow: (insource CF) - (outsource CF) for each year
        # Year 0: -CAPEX vs 0 → incremental = -CAPEX
        # Year 1-5: outsource is more negative → incremental should be positive
        incremental = df[scenario] - df["outsource"]
        npv = sum(cf / (1 + r) ** yr for yr, cf in zip(df["year"], incremental))
        npvs[scenario] = npv
    return npvs


def compute_breakeven_utilization(a: dict) -> dict:
    """
    Find the minimum utilization rate (as % of annual_hours) at which
    each insource scenario breaks even with outsourcing on an annual basis (Year 1).
    Assumes all other assumptions are base-case.

    Returns the utilization fraction (0.0–1.0) or None if always better.
    """
    # Annual outsource cost (Year 1)
    outsource_yr1 = compute_annual_outsource_cost(a, 1)["Total Cost"]

    results = {}
    for scenario in ["eu_insource", "china_insource"]:
        # OpEx varies linearly with hours (energy + consumables) + fixed (maintenance + labour)
        # We solve: fixed + variable_rate × hours = outsource_yr1
        n            = a.get("num_machines", 1)
        maint_pct    = a["eu_maintenance_pct"] if scenario == "eu_insource" else a["china_maintenance_pct"]
        equip_cost   = a["eu_equipment_cost"] if scenario == "eu_insource" else a["china_equipment_cost"]
        fixed        = equip_cost * maint_pct * n + a["operator_wage"] * n
        variable_phr = a["laser_power_kw"] * a["electricity_rate"] + a["consumables_per_hr"]

        if variable_phr <= 0:
            results[scenario] = None
            continue

        # hours_needed s.t. fixed + variable_phr × hours = outsource_yr1
        hours_needed = (outsource_yr1 - fixed) / variable_phr
        util_fraction = hours_needed / a["annual_hours"]
        results[scenario] = max(0.0, min(util_fraction, 1.5))  # cap at 150% for display

    return results


def build_summary_kpis(a: dict) -> dict:
    """
    Single entry-point: returns all headline KPIs in one dict.
    Used by Executive Summary page.
    """
    df = compute_scenario_cashflows(a)
    totals  = compute_5yr_totals(df)
    savings = compute_5yr_savings(df)
    roi     = compute_roi(a, df)
    npv     = compute_npv(a, df)

    return {
        "df"                        : df,
        "capex_eu"                  : get_total_capex(a, "eu_insource"),
        "capex_china"               : get_total_capex(a, "china_insource"),
        "payback_eu"                : compute_payback_year(df, "eu_insource"),
        "payback_china"             : compute_payback_year(df, "china_insource"),
        "tco_5yr_outsource"         : totals["outsource"],
        "tco_5yr_eu"                : totals["eu_insource"],
        "tco_5yr_china"             : totals["china_insource"],
        "savings_5yr_eu"            : savings["eu_insource"],
        "savings_5yr_china"         : savings["china_insource"],
        "roi_eu"                    : roi["eu_insource"],
        "roi_china"                 : roi["china_insource"],
        "npv_eu"                    : npv["eu_insource"],
        "npv_china"                 : npv["china_insource"],
        "breakeven_util"            : compute_breakeven_utilization(a),
    }
