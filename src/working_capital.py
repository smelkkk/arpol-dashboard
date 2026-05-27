"""
working_capital.py — SKU rationalisation and working capital release model.

Key insight from Manuel interview:
    ARPOL currently holds ~8 different coil SKUs per thickness (to cover
    different ring geometries). Switching to sheet stock means one sheet
    SKU covers all rings of that thickness. → 70% SKU reduction hypothesis.
"""

from __future__ import annotations
import pandas as pd
from src.config import ANALYSIS_YEARS


def compute_wc_release(a: dict) -> dict:
    """
    Compute the full working capital release calculation from SKU rationalisation.

    Returns a dict of labelled line items for display.
    """
    coil_skus        = a["coil_skus_per_thickness"]
    thicknesses      = a["thickness_grades"]
    avg_inv_per_sku  = a["avg_inventory_per_sku"]
    holding_rate     = a["inventory_holding_rate"]
    sku_reduction    = a["sku_reduction_rate"]

    total_coil_skus      = coil_skus * thicknesses
    total_coil_inv_value = total_coil_skus * avg_inv_per_sku

    skus_eliminated      = round(total_coil_skus * sku_reduction)
    skus_remaining       = total_coil_skus - skus_eliminated

    inv_released_onetime = skus_eliminated * avg_inv_per_sku
    annual_holding_saved = inv_released_onetime * holding_rate
    total_5yr_wc_benefit = inv_released_onetime + annual_holding_saved * ANALYSIS_YEARS

    return {
        # Inputs
        "coil_skus_per_thickness"    : coil_skus,
        "thickness_grades"           : thicknesses,
        "avg_inventory_per_sku_eur"  : avg_inv_per_sku,
        "inventory_holding_rate_pct" : holding_rate,
        "sku_reduction_rate_pct"     : sku_reduction,

        # Derived
        "total_coil_skus_today"      : total_coil_skus,
        "total_coil_inv_value_eur"   : total_coil_inv_value,
        "skus_eliminated"            : skus_eliminated,
        "skus_remaining"             : skus_remaining,
        "inv_released_onetime_eur"   : inv_released_onetime,
        "annual_holding_saved_eur"   : annual_holding_saved,
        "total_5yr_wc_benefit_eur"   : total_5yr_wc_benefit,
    }


def compute_wc_timeline(a: dict) -> pd.DataFrame:
    """
    Build a year-by-year working capital benefit table.
    Year 0: one-time inventory release.
    Years 1-5: annual holding cost savings.
    """
    wc = compute_wc_release(a)
    rows = []
    for yr in range(ANALYSIS_YEARS + 1):
        annual_benefit = (
            wc["inv_released_onetime_eur"] if yr == 0
            else wc["annual_holding_saved_eur"]
        )
        rows.append({"year": yr, "wc_benefit": annual_benefit})
    df = pd.DataFrame(rows)
    df["wc_benefit_cumul"] = df["wc_benefit"].cumsum()
    return df


def get_sku_table(a: dict) -> pd.DataFrame:
    """
    Return a DataFrame comparing current SKU profile vs. post-rationalisation.
    Suitable for display as a table on the Working Capital page.
    """
    wc = compute_wc_release(a)
    thicknesses = a["thickness_grades"]
    coil_skus_per = a["coil_skus_per_thickness"]
    avg_inv = a["avg_inventory_per_sku"]
    after_skus_per = max(1, round(coil_skus_per * (1 - a["sku_reduction_rate"])))

    rows = []
    for t in range(1, thicknesses + 1):
        rows.append({
            "Thickness Grade"             : f"Grade {t}",
            "Current SKUs (coil)"         : coil_skus_per,
            "Post-Rationalisation SKUs"   : after_skus_per,
            "SKUs Eliminated"             : coil_skus_per - after_skus_per,
            "Inventory Released (€)"      : (coil_skus_per - after_skus_per) * avg_inv,
        })
    return pd.DataFrame(rows)
