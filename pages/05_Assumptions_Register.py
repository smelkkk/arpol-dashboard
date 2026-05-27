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
with col_leg[0]: st.markdown(f"<span style='color:white;background:#27AE60;padding:2px 8px;border-radius:4px'>✅ Confirmed</span>", unsafe_allow_html=True)
with col_leg[1]: st.markdown(f"<span style='color:white;background:#E67E22;padding:2px 8px;border-radius:4px'>⚠️ Placeholder</span>", unsafe_allow_html=True)
with col_leg[2]: st.markdown(f"<span style='color:white;background:#2980B9;padding:2px 8px;border-radius:4px'>📐 Assumed</span>", unsafe_allow_html=True)
with col_leg[3]: st.markdown(f"<span style='color:white;background:#7F8C8D;padding:2px 8px;border-radius:4px'>📊 Benchmark</span>", unsafe_allow_html=True)
st.divider()


# ── Build assumption table ──────────────────────────────────────────────────

assumption_rows = [
    # ── CURRENT STATE ───────────────────────────────────────────────────
    ("Current State", "Annual subcontract spend",        fmt_eur(assumptions["subcontract_annual_spend"]),
     "€/yr", "Client (Manuel via Prof. Felipe)", "⚠️ Placeholder", True),
    ("Current State", "Press annual operational cost",   fmt_eur(assumptions["press_annual_opex"]),
     "€/yr", "Client / INE benchmark",            "⚠️ Placeholder", True),
    ("Current State", "Scrap & rework cost",             fmt_eur(assumptions["scrap_rework_cost"]),
     "€/yr", "Industry benchmark (% revenue)",    "⚠️ Placeholder", True),

    # ── VOLUME ──────────────────────────────────────────────────────────
    ("Volume", "Current production volume",              f"{assumptions['current_volume_units']:,}",
     "units/yr", "Client",                         "⚠️ Placeholder", True),
    ("Volume", "Volume growth rate (base)",              fmt_pct(assumptions["volume_growth_rate"]),
     "%/yr", "Derived: €4M→€8M by 2028",          "📐 Assumed", False),

    # ── EU CAPEX ────────────────────────────────────────────────────────
    ("EU CAPEX", "EU equipment cost (mid, after SME disc)", fmt_eur(assumptions["eu_equipment_cost"]),
     "€", "Bystronic/Trumpf published pricing −15%", "📊 Benchmark", False),
    ("EU CAPEX", "Installation & commissioning",         fmt_pct(assumptions["eu_install_pct"] + assumptions["eu_commissioning_pct"]),
     "% CAPEX", "Supplier whitepapers / industry benchmark", "📊 Benchmark", False),
    ("EU CAPEX", "Training cost",                        fmt_eur(assumptions["eu_training_cost"]),
     "€ one-off", "Supplier estimates",            "📊 Benchmark", False),
    ("EU CAPEX", "Ancillary equipment",                  fmt_eur(assumptions["eu_ancillary_cost"]),
     "€", "Industry benchmark",                    "📐 Assumed", False),
    ("EU CAPEX", "Spare parts buffer",                   fmt_eur(assumptions["eu_spares_buffer"]),
     "€", "Industry benchmark",                    "📐 Assumed", False),
    ("EU CAPEX", "Annual maintenance contract",          fmt_pct(assumptions["eu_maintenance_pct"]),
     "% CAPEX/yr", "Benchmark: 5–10% (mid 7%)",  "📊 Benchmark", False),
    ("EU CAPEX", "EU delivery lead time",                f"{assumptions['eu_delivery_weeks']} weeks",
     "", "Supplier published lead times",          "📊 Benchmark", False),

    # ── CHINA CAPEX ─────────────────────────────────────────────────────
    ("China CAPEX", "China equipment cost (ex-works mid)", fmt_eur(assumptions["china_equipment_cost"]),
     "€", "Bodor T230A published pricing",         "📊 Benchmark", False),
    ("China CAPEX", "MFN import duty",               fmt_pct(assumptions["china_duty_pct"]),
     "% of equipment", "TARIC HS 8456 (verify)",  "📊 Benchmark", False),
    ("China CAPEX", "Freight (China → Spain)",       fmt_eur(assumptions["china_freight"]),
     "€ one-off", "Freight forwarder benchmark",   "📊 Benchmark", False),
    ("China CAPEX", "China annual maintenance",      fmt_pct(assumptions["china_maintenance_pct"]),
     "% CAPEX/yr", "Benchmark: 3–8% (mid 5%)",    "📊 Benchmark", False),
    ("China CAPEX", "China parts lead time",         f"{assumptions['china_parts_lead_time_wks']} weeks",
     "", "Supplier / trade publications",          "📊 Benchmark", False),

    # ── OPERATIONS ──────────────────────────────────────────────────────
    ("Operations", "Annual operating hours",         f"{assumptions['annual_hours']:,}",
     "hrs/yr", "1-shift: 225 days × 8h",           "📐 Assumed", False),
    ("Operations", "Laser power consumption",        f"{assumptions['laser_power_kw']} kW",
     "kW", "Supplier specs (incl. chiller/extract)", "📊 Benchmark", False),
    ("Operations", "Spanish industrial electricity", f"€{assumptions['electricity_rate']:.2f}",
     "€/kWh", "Eurostat / INE Q4 2025",           "📊 Benchmark", False),
    ("Operations", "Consumables per hour",           f"€{assumptions['consumables_per_hr']:.2f}",
     "€/hr", "Trade publications (nozzles, lenses, gas)", "📊 Benchmark", False),
    ("Operations", "Operator wage (loaded)",         fmt_eur(assumptions["operator_wage"]),
     "€/yr", "INE manufacturing wages + social charges", "📊 Benchmark", False),
    ("Operations", "Operators required",             f"{int(assumptions['num_operators'])} FTE",
     "", "1-shift standard assumption",            "📐 Assumed", False),

    # ── WORKING CAPITAL ─────────────────────────────────────────────────
    ("Working Capital", "Coil SKUs per thickness",   f"{int(assumptions['coil_skus_per_thickness'])}",
     "SKUs/thickness", "Manuel interview",          "✅ Confirmed", False),
    ("Working Capital", "Thickness grades",          f"{int(assumptions['thickness_grades'])}",
     "", "Client estimate",                        "📐 Assumed", False),
    ("Working Capital", "Avg inventory per coil SKU", fmt_eur(assumptions["avg_inventory_per_sku"]),
     "€", "Steel pricing benchmark",               "📐 Assumed", False),
    ("Working Capital", "Inventory holding cost rate", fmt_pct(assumptions["inventory_holding_rate"]),
     "%/yr", "Industry benchmark (15–25% SME)",   "📊 Benchmark", False),
    ("Working Capital", "SKU reduction rate (coil→sheet)", fmt_pct(assumptions["sku_reduction_rate"]),
     "% eliminated", "Hypothesis from Manuel interview", "⚠️ Placeholder", True),

    # ── FINANCIAL ───────────────────────────────────────────────────────
    ("Financial", "Discount rate (WACC proxy)",       fmt_pct(assumptions["discount_rate"]),
     "%", "Spanish SME benchmark",                  "📐 Assumed", False),
    ("Financial", "Inflation rate",                   fmt_pct(assumptions["inflation_rate"]),
     "%/yr", "Eurozone consensus forecast",         "📊 Benchmark", False),
    ("Financial", "CAPEX payback hurdle",             f"{int(assumptions['payback_hurdle_years'])} years",
     "", "Spanish SME benchmark (validate with Finance)", "📐 Assumed", False),
    ("Financial", "Equipment useful life",            f"{int(assumptions['equipment_life_years'])} years",
     "", "Spanish accounting standards",            "📊 Benchmark", False),
]

df = pd.DataFrame(assumption_rows, columns=[
    "Category", "Assumption", "Value", "Unit", "Source", "Status", "Is Placeholder"
])

# ── Display by category ────────────────────────────────────────────────────

def status_color(status):
    if "Confirmed" in status:
        return f"background-color:#d4edda;color:#155724"
    elif "Placeholder" in status:
        return f"background-color:#fff3cd;color:#856404;font-weight:bold"
    elif "Assumed" in status:
        return f"background-color:#d1ecf1;color:#0c5460"
    else:
        return f"background-color:#f8f9fa;color:#383d41"


categories = df["Category"].unique()

for cat in categories:
    with st.expander(f"**{cat}**", expanded=(cat in ["Current State", "Working Capital"])):
        cat_df = df[df["Category"] == cat].drop(columns=["Category", "Is Placeholder"])

        styled = cat_df.style.applymap(
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
