"""
assumptions.py — Assumption registry with defaults, validation, and override support.

The canonical values live in scenario_defaults.json and capex_benchmarks.json.
All dashboard sliders produce an `overrides` dict that gets merged here.
"""

import json
from pathlib import Path
from typing import Any

from src.config import DEFAULTS_JSON, CAPEX_JSON


# ── Load JSON files ────────────────────────────────────────────────────────

def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


_defaults_raw   = _load_json(DEFAULTS_JSON)
_capex_raw      = _load_json(CAPEX_JSON)


# ── Default assumption dict (flat, ready for tco_engine) ──────────────────

def get_default_assumptions() -> dict:
    """
    Return a flat dict of all base-case assumptions.
    Values are mid-range estimates.
    """
    cs  = _defaults_raw["current_state"]
    vol = _defaults_raw["volume"]
    eu  = _defaults_raw["eu_insource"]
    cn  = _defaults_raw["china_insource"]
    ops = _defaults_raw["operations"]
    wc  = _defaults_raw["working_capital"]
    fin = _defaults_raw["financial"]
    cap = _capex_raw

    # EU equipment with SME discount applied at mid
    eu_equip_mid = eu["eu_equipment_cost_mid"]

    # China equipment + duty + freight at mid
    cn_equip_mid   = cn["china_equipment_cost_mid"]
    cn_duty_mid    = cn["china_duty_pct_mid"]
    cn_freight_mid = cn["china_freight_mid"]
    cn_landed_mid  = cn_equip_mid * (1 + cn_duty_mid) + cn_freight_mid

    return {
        # ── Current state (outsourcing baseline) ────────────────────────
        "subcontract_annual_spend" : cs["subcontract_annual_spend"]["value"],
        "press_annual_opex"        : cs["press_annual_opex"]["value"],
        "logistics_cost"           : cs["logistics_cost"]["value"],
        "scrap_rework_cost"        : cs["scrap_rework_cost"]["value"],

        # ── Volume ──────────────────────────────────────────────────────
        "current_volume_units"     : vol["current_volume_units"]["value"],
        "volume_growth_rate"       : vol["volume_growth_base"]["value"],

        # ── EU CAPEX ────────────────────────────────────────────────────
        "eu_equipment_cost"        : eu_equip_mid,
        "eu_equipment_cost_low"    : eu["eu_equipment_cost_low"],
        "eu_equipment_cost_high"   : eu["eu_equipment_cost_high"],
        "eu_install_pct"           : eu["eu_install_pct"],
        "eu_commissioning_pct"     : eu["eu_commissioning_pct"],
        "eu_training_cost"         : eu["eu_training_cost"],
        "eu_tooling_cost"          : eu["eu_tooling_cost"],
        "eu_spares_buffer"         : eu["eu_spares_buffer"],
        "eu_ancillary_cost"        : eu["eu_ancillary_cost"],
        "eu_maintenance_pct"       : eu["eu_maintenance_pct"],
        "eu_consumables_pct"       : eu["eu_consumables_pct"],
        "eu_delivery_weeks"        : eu["eu_delivery_weeks"],
        "eu_model_name"            : eu["eu_equipment_model"],

        # ── China CAPEX ─────────────────────────────────────────────────
        "china_equipment_cost"     : cn_equip_mid,
        "china_equipment_cost_low" : cn["china_equipment_cost_low"],
        "china_equipment_cost_high": cn["china_equipment_cost_high"],
        "china_duty_pct"           : cn_duty_mid,
        "china_freight"            : cn_freight_mid,
        "china_landed_cost"        : cn_landed_mid,
        "china_install_pct"        : cn["china_install_pct"],
        "china_commissioning_pct"  : cn["china_commissioning_pct"],
        "china_training_cost"      : cn["china_training_cost"],
        "china_tooling_cost"       : cn["china_tooling_cost"],
        "china_spares_buffer"      : cn["china_spares_buffer"],
        "china_ancillary_cost"     : cn["china_ancillary_cost"],
        "china_maintenance_pct"    : cn["china_maintenance_pct"],
        "china_consumables_pct"    : cn["china_consumables_pct"],
        "china_delivery_weeks"     : cn["china_delivery_weeks"],
        "china_parts_lead_time_wks": cn["china_parts_lead_time_weeks"],
        "china_model_name"         : cn["china_equipment_model"],

        # ── Operations ──────────────────────────────────────────────────
        "num_machines"             : 1,
        "annual_hours"             : ops["annual_hours"]["value"],
        "laser_power_kw"           : ops["laser_power_kw"]["value"],
        "electricity_rate"         : ops["electricity_rate"]["value"],
        "consumables_per_hr"       : ops["consumables_per_hr"]["value"],
        "operator_wage"            : ops["operator_wage_loaded"]["value"],
        "num_operators"            : ops["operators_required"]["value"],

        # ── Working capital ─────────────────────────────────────────────
        "coil_skus_per_thickness"  : wc["coil_skus_per_thickness"]["value"],
        "thickness_grades"         : wc["thickness_grades"]["value"],
        "avg_inventory_per_sku"    : wc["avg_inventory_per_sku_eur"]["value"],
        "inventory_holding_rate"   : wc["inventory_holding_rate"]["value"],
        "sku_reduction_rate"       : wc["sku_reduction_rate"]["value"],

        # ── Financial parameters ────────────────────────────────────────
        "discount_rate"            : fin["discount_rate"]["value"],
        "inflation_rate"           : fin["inflation_rate"]["value"],
        "payback_hurdle_years"     : fin["payback_hurdle_years"]["value"],
        "equipment_life_years"     : fin["equipment_life_years"]["value"],
    }


def merge_overrides(base: dict, overrides: dict) -> dict:
    """Merge sidebar overrides into the base assumptions dict."""
    merged = base.copy()
    for key, val in overrides.items():
        if key in merged:
            merged[key] = val
        else:
            merged[key] = val   # allow new keys from sidebar experiments
    # Recompute derived values that depend on overridden primitives
    merged = _recompute_derived(merged)
    return merged


def _recompute_derived(a: dict) -> dict:
    """Recalculate values that are derived from other assumptions."""
    # China landed cost must reflect latest equipment + duty + freight
    a["china_landed_cost"] = (
        a["china_equipment_cost"] * (1 + a["china_duty_pct"]) + a["china_freight"]
    )
    return a


def get_placeholder_flags() -> dict[str, bool]:
    """Return a dict of assumption keys that are still placeholders."""
    flags = {}
    for section_key, section in _defaults_raw.items():
        if section_key == "metadata":
            continue
        if isinstance(section, dict):
            for k, v in section.items():
                if isinstance(v, dict) and v.get("validated") is False:
                    flags[k] = True
    return flags


def get_capex_machine_options(origin: str) -> list[dict]:
    """Return list of machine dicts for 'eu_machines' or 'china_machines'."""
    key = "eu_machines" if origin == "eu" else "china_machines"
    return _capex_raw.get(key, [])
