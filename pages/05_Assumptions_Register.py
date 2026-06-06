"""
pages/05_Assumptions_Register.py — Full assumption register with validation status.
Serves as the 'audit trail' for all model inputs.
"""

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Assumptions | ARPOL", page_icon="📋", layout="wide")

from src.assumptions import get_default_assumptions, merge_overrides, get_placeholder_flags
from components.sidebar import render_sidebar
from src.i18n import t, get_lang
from src.config import COLORS, fmt_eur, fmt_pct


# ── State ──────────────────────────────────────────────────────────────────
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"

defaults    = get_default_assumptions()
overrides   = render_sidebar(defaults)
assumptions = merge_overrides(defaults, overrides)
lang        = get_lang()
flags       = get_placeholder_flags()


# ── Header ─────────────────────────────────────────────────────────────────
st.title(f"📋 {t('title_assumptions')}")
st.markdown(
    "Full register of all model inputs with source attribution and validation status. "
    "Yellow = placeholder awaiting client data. Green = confirmed. Blue = benchmarked."
    if lang == "en" else
    "Registro completo de todos los inputs del modelo con atribución de fuente y estado de validación. "
    "Amarillo = estimado pendiente de datos del cliente. Verde = confirmado. Azul = benchmarked."
)

# Status legend
col_leg = st.columns(4)
badge = "<span style='color:white;background:{bg};padding:2px 10px;border-radius:3px;font-size:0.78rem;font-weight:600;letter-spacing:0.04em'>{label}</span>"
with col_leg[0]: st.markdown(badge.format(bg="#27AE60", label="Confirmed"),  unsafe_allow_html=True)
with col_leg[1]: st.markdown(badge.format(bg="#E67E22", label="Pending"),    unsafe_allow_html=True)
with col_leg[2]: st.markdown(badge.format(bg="#2980B9", label="Assumed"),    unsafe_allow_html=True)
with col_leg[3]: st.markdown(badge.format(bg="#7F8C8D", label="Benchmark"),  unsafe_allow_html=True)
st.divider()


# ── Build assumption table ──────────────────────────────────────────────────

assumption_rows = [
    # ── CURRENT STATE ───────────────────────────────────────────────────
    ("Current State", "Annual subcontract spend",        fmt_eur(assumptions["subcontract_annual_spend"]),
     "€/yr", "Client-confirmed 2026 (Seyer invoices: Contracurva + Carcasa + Acero)", "Confirmed", False),
    ("Current State", "Press annual operational cost",   fmt_eur(assumptions["press_annual_opex"]),
     "€/yr", "Client-confirmed — €23/h × 643 h/yr (403h production + 240h setup)", "Confirmed", False),
    ("Current State", "Logistics cost (subcontract)",    fmt_eur(assumptions["logistics_cost"]),
     "€/yr", "Client-confirmed — 2 trips/week × 3h × €23/h × 50 weeks",             "Confirmed", False),
    ("Current State", "Scrap & rework cost",             fmt_eur(assumptions["scrap_rework_cost"]),
     "€/yr", "Client-confirmed actual (2025)",          "Confirmed", False),

    # ── VOLUME ──────────────────────────────────────────────────────────
    ("Volume", "Current production volume",              f"{assumptions['current_volume_units']:,}",
     "units/yr", "Client-confirmed — 2025 total; laser-cut subset ~35,265 units",    "Confirmed", False),
    ("Volume", "Volume growth rate (base)",              fmt_pct(assumptions["volume_growth_rate"]),
     "%/yr", "Derived: €4M→€8M plan; supported by 2025 revenue of €6.1M (confirmed)", "Assumed", False),

    # ── EU CAPEX ────────────────────────────────────────────────────────
    ("EU CAPEX", "EU equipment cost — mid (Trumpf TruLaser 3030 6kW)", fmt_eur(assumptions["eu_equipment_cost"]),
     "€", "Trumpf product portfolio + MM MaschinenMarkt trade press, 2023", "Benchmark", False),
    ("EU CAPEX", "Installation & commissioning",         fmt_pct(assumptions["eu_install_pct"] + assumptions["eu_commissioning_pct"]),
     "% of equipment", "VDMA benchmarks — typical 8–15% range (mid 12%)", "Benchmark", False),
    ("EU CAPEX", "Training cost",                        fmt_eur(assumptions["eu_training_cost"]),
     "€ one-off", "Trumpf/Bystronic operator programme — 2–5 days",       "Benchmark", False),
    ("EU CAPEX", "Ancillary equipment",                  fmt_eur(assumptions["eu_ancillary_cost"]),
     "€", "Fume extraction + chiller (Sideros ECO6-class), supplier config data 2024", "Benchmark", False),
    ("EU CAPEX", "Annual maintenance contract",          fmt_pct(assumptions["eu_maintenance_pct"]),
     "% of equipment/yr", "VDMA — typical 5–10% (mid 7%), ~2 preventive visits/yr", "Benchmark", False),
    ("EU CAPEX", "EU delivery lead time",                f"{assumptions['eu_delivery_weeks']} weeks",
     "", "Supplier published lead times",                "Benchmark", False),

    # ── CHINA CAPEX ─────────────────────────────────────────────────────
    ("China CAPEX", "China equipment cost — mid (Bodor P3015E 6kW)", fmt_eur(assumptions["china_equipment_cost"]),
     "€", "Bodor official site + Made-in-China listings, 2024; CNY/EUR ECB 2025 avg 8.1185", "Benchmark", False),
    ("China CAPEX", "MFN import duty",               fmt_pct(assumptions["china_duty_pct"]),
     "% of equipment", "EU Access2Markets HS 8456.11.90, CN→ES, 4.5% MFN — verified 27 May 2026", "Confirmed", False),
    ("China CAPEX", "Freight (China → Spain)",       fmt_eur(assumptions["china_freight"]),
     "€ one-off", "Sea-freight forwarder benchmarks, FCL China→Spain, 2024", "Benchmark", False),
    ("China CAPEX", "China annual maintenance",      fmt_pct(assumptions["china_maintenance_pct"]),
     "% of equipment/yr", "Industry estimates — 3–8%/yr; often pay-per-incident", "Benchmark", False),
    ("China CAPEX", "China parts lead time",         f"{assumptions['china_parts_lead_time_wks']} weeks",
     "", "Supplier / trade publications — 4–12 weeks ex-China risk",       "Benchmark", False),

    # ── OPERATIONS ──────────────────────────────────────────────────────
    ("Operations", "Annual operating hours",         f"{assumptions['annual_hours']:,}",
     "hrs/yr", "1-shift: 225 days × 8h (client / standard assumption)",    "Assumed", False),
    ("Operations", "Laser power consumption",        f"{assumptions['laser_power_kw']} kW",
     "kW", "IPG resonator + chiller + extraction — supplier specs, 2024",  "Benchmark", False),
    ("Operations", "Spanish industrial electricity", f"€{assumptions['electricity_rate']:.4f}",
     "€/kWh", "Eurostat nrg_pc_205, Spain 2025-S2, Band IC, all taxes (I_TAX)", "Benchmark", False),
    ("Operations", "Consumables per hour",           f"€{assumptions['consumables_per_hr']:.2f}",
     "€/hr", "VDMA — nozzles, lenses, assist gas; ~6% of CAPEX/yr at 1,800 hrs", "Benchmark", False),
    ("Operations", "Operator wage (loaded)",         fmt_eur(assumptions["operator_wage"]),
     "€/yr", "Eurostat lc_an_struc_r2, Spain Mfg + INE EACL — ~€20/hr incl. social charges", "Benchmark", False),
    ("Operations", "Operators required",             f"{int(assumptions['num_operators'])} FTE",
     "", "Standard 1-shift operation",                    "Assumed", False),

    # ── WORKING CAPITAL ─────────────────────────────────────────────────
    ("Working Capital", "Coil SKUs per thickness",   f"{int(assumptions['coil_skus_per_thickness'])}",
     "SKUs/thickness", "Manuel Pérez interview — confirmed",               "Confirmed", False),
    ("Working Capital", "Thickness grades",          f"{int(assumptions['thickness_grades'])}",
     "", "Client estimate",                              "Assumed", False),
    ("Working Capital", "Avg inventory per coil SKU", fmt_eur(assumptions["avg_inventory_per_sku"]),
     "€", "Client / steel pricing benchmark",            "Assumed", False),
    ("Working Capital", "Inventory holding cost rate", fmt_pct(assumptions["inventory_holding_rate"]),
     "%/yr", "Industry benchmark — 15–25% for industrial SMEs",           "Benchmark", False),
    ("Working Capital", "SKU reduction rate (coil→sheet)", fmt_pct(assumptions["sku_reduction_rate"]),
     "% eliminated", "Hypothesis from Manuel interview — to validate with procurement team", "Pending", True),

    # ── FINANCIAL ───────────────────────────────────────────────────────
    ("Financial", "Discount rate (WACC proxy)",       fmt_pct(assumptions["discount_rate"]),
     "%", "Spanish SME WACC proxy 7–10%; validate with ARPOL Finance",    "Assumed", False),
    ("Financial", "Inflation rate",                   fmt_pct(assumptions["inflation_rate"]),
     "%/yr", "ECB price-stability objective + Eurozone consensus",         "Benchmark", False),
    ("Financial", "CAPEX payback hurdle",             f"{int(assumptions['payback_hurdle_years'])} years",
     "", "Spanish SME norm 3–5 years; validate with ARPOL Finance",       "Assumed", False),
    ("Financial", "Equipment useful life",            f"{int(assumptions['equipment_life_years'])} years",
     "", "Ley 27/2014 IS — industrial machinery 8–10 year useful life",   "Benchmark", False),
]

df = pd.DataFrame(assumption_rows, columns=[
    "Category", "Assumption", "Value", "Unit", "Source", "Status", "Is Placeholder"
])

# ── Display by category ────────────────────────────────────────────────────

def status_color(status):
    if status == "Confirmed":
        return "background-color:#d4edda;color:#155724"
    elif status == "Pending":
        return "background-color:#fff3cd;color:#856404;font-weight:600"
    elif status == "Assumed":
        return "background-color:#d1ecf1;color:#0c5460"
    else:
        return "background-color:#f8f9fa;color:#383d41"


categories = df["Category"].unique()

for cat in categories:
    with st.expander(f"**{cat}**", expanded=(cat in ["Current State", "Working Capital"])):
        cat_df = df[df["Category"] == cat].drop(columns=["Category", "Is Placeholder"])

        styled = cat_df.style.map(
            lambda v: status_color(v),
            subset=["Status"],
        )
        st.dataframe(styled, use_container_width=True, hide_index=True)

st.divider()


# ── Placeholder summary ────────────────────────────────────────────────────

st.subheader(f"🚨 {t('data_gaps')}")

placeholder_df = df[df["Is Placeholder"]][["Category", "Assumption", "Value", "Source"]]
placeholder_df.columns = ["Category", "Assumption", "Current Value (Placeholder)", "Source"]

st.error(
    f"**{len(placeholder_df)} assumptions still require client validation.** "
    "Model results are directional until these are confirmed."
    if lang == "en" else
    f"**{len(placeholder_df)} supuestos aún requieren validación del cliente.** "
    "Los resultados del modelo son indicativos hasta que sean confirmados."
)

st.dataframe(placeholder_df, use_container_width=True, hide_index=True)
