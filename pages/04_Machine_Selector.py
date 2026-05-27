"""
pages/04_Machine_Selector.py — Interactive machine selection and CAPEX explorer.
Lets the user browse all EU and China machine options and see their impact on payback.
"""

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Machine Selector | ARPOL", page_icon="🏭", layout="wide")

from src.assumptions import get_default_assumptions, merge_overrides, get_capex_machine_options
from src.tco_engine import build_summary_kpis, get_total_capex
from components.sidebar import render_sidebar
from src.i18n import t, get_lang
from src.config import COLORS, fmt_eur
import json
from pathlib import Path
from src.config import CAPEX_JSON


# ── State ──────────────────────────────────────────────────────────────────
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"

defaults    = get_default_assumptions()
overrides   = render_sidebar(defaults)
assumptions = merge_overrides(defaults, overrides)
lang        = get_lang()

eu_machines    = get_capex_machine_options("eu")
china_machines = get_capex_machine_options("china")

with open(CAPEX_JSON) as f:
    capex_data = json.load(f)

sme_discount = capex_data["metadata"]["eu_sme_discount_pct"]
mfn_duty     = capex_data["metadata"]["china_mfn_duty_pct"]
freight_mid  = capex_data["metadata"]["china_freight_mid"]


# ── Header ─────────────────────────────────────────────────────────────────
st.title("🏭 " + ("Machine Selector & CAPEX Explorer" if lang == "en"
                   else "Selector de Máquinas y Explorador de CAPEX"))
st.markdown(
    "Compare all available EU and China laser cutter options. "
    "Select a machine to see its full CAPEX impact on the TCO model."
    if lang == "en" else
    "Compare todas las opciones de cortadoras láser europeas y chinas. "
    "Seleccione una máquina para ver su impacto completo en el modelo TCO."
)
st.divider()


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1 — EU MACHINES
# ═══════════════════════════════════════════════════════════════════════════

st.subheader("🇪🇺 " + ("EU Fiber Laser Options" if lang == "en" else "Opciones Láser de Fibra UE"))
st.caption(f"List prices shown. {sme_discount*100:.0f}% SME discount typically applicable."
           if lang == "en" else
           f"Precios de lista mostrados. Descuento SME del {sme_discount*100:.0f}% típicamente aplicable.")

# Build EU table
eu_rows = []
for m in eu_machines:
    disc_mid = m["capex_mid"] * (1 - sme_discount)
    eu_rows.append({
        "Brand"          : m["brand"],
        "Model"          : m["model"],
        "Power (kW)"     : m["power_kw"],
        "List Low (€)"   : m["capex_low"],
        "List Mid (€)"   : m["capex_mid"],
        "List High (€)"  : m["capex_high"],
        f"Mid w/ {sme_discount*100:.0f}% disc (€)": round(disc_mid),
        "ARPOL Fit"      : m["arpol_fit"].upper(),
        "Note"           : m["note"],
    })

eu_df = pd.DataFrame(eu_rows)

# Colour fit column
def colour_fit(val):
    if val == "HIGH":
        return "background-color: #d4edda; color: #155724; font-weight: bold"
    elif val == "MEDIUM":
        return "background-color: #fff3cd; color: #856404"
    return "background-color: #f8d7da; color: #721c24"

st.dataframe(
    eu_df.style
        .map(colour_fit, subset=["ARPOL Fit"])
        .format({col: "€{:,.0f}" for col in eu_df.columns if "(€)" in col}),
    use_container_width=True,
    hide_index=True,
)

# EU Machine picker
st.markdown("**Select EU machine to model:**" if lang == "en" else "**Seleccionar máquina UE para modelar:**")
eu_options = [f"{m['brand']} {m['model']} {m['power_kw']}kW" for m in eu_machines]
eu_selected_idx = st.selectbox("EU Machine", options=range(len(eu_options)),
                                format_func=lambda i: eu_options[i], key="eu_machine_select")
eu_sel = eu_machines[eu_selected_idx]

eu_disc_mid = eu_sel["capex_mid"] * (1 - sme_discount)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("List Price Mid", f"€{eu_sel['capex_mid']:,.0f}")
with col2:
    st.metric(f"After {sme_discount*100:.0f}% SME Discount", f"€{eu_disc_mid:,.0f}")
with col3:
    a_test = {**assumptions, "eu_equipment_cost": eu_disc_mid}
    capex_total = get_total_capex(a_test, "eu_insource")
    st.metric("Total CAPEX (incl. install etc.)", fmt_eur(capex_total))
with col4:
    kpis_test = build_summary_kpis(a_test)
    pb = kpis_test["payback_eu"]
    st.metric("Payback Period", f"Year {pb}" if pb else t("not_within_5yr"))

st.info(f"ℹ️ {eu_sel['note']}")
st.divider()


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2 — CHINA MACHINES
# ═══════════════════════════════════════════════════════════════════════════

st.subheader("🇨🇳 " + ("China Fiber Laser Options" if lang == "en" else "Opciones Láser de Fibra China"))
st.caption(
    f"Ex-works prices. Add {mfn_duty*100:.0f}% MFN import duty + €{freight_mid:,.0f} freight (mid estimate)."
    if lang == "en" else
    f"Precios en origen. Añadir {mfn_duty*100:.0f}% arancel MFN + €{freight_mid:,.0f} flete (estimado medio)."
)

china_rows = []
for m in china_machines:
    landed_mid = m["capex_mid"] * (1 + mfn_duty) + freight_mid
    china_rows.append({
        "Brand"            : m["brand"],
        "Model"            : m["model"],
        "Power (kW)"       : m["power_kw"],
        "Ex-Works Low (€)" : m["capex_low"],
        "Ex-Works Mid (€)" : m["capex_mid"],
        "Ex-Works High (€)": m["capex_high"],
        f"Landed Mid (€)"  : round(landed_mid),
        "ARPOL Fit"        : m["arpol_fit"].upper(),
        "Note"             : m["note"],
    })

china_df = pd.DataFrame(china_rows)

st.dataframe(
    china_df.style
        .map(colour_fit, subset=["ARPOL Fit"])
        .format({col: "€{:,.0f}" for col in china_df.columns if "(€)" in col}),
    use_container_width=True,
    hide_index=True,
)

# China Machine picker
st.markdown("**Select China machine to model:**" if lang == "en" else "**Seleccionar máquina China para modelar:**")
cn_options = [f"{m['brand']} {m['model']} {m['power_kw']}kW" for m in china_machines]
cn_selected_idx = st.selectbox("China Machine", options=range(len(cn_options)),
                                 format_func=lambda i: cn_options[i], key="cn_machine_select")
cn_sel = china_machines[cn_selected_idx]

cn_landed_mid = cn_sel["capex_mid"] * (1 + mfn_duty) + freight_mid

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Ex-Works Mid", f"€{cn_sel['capex_mid']:,.0f}")
with col2:
    st.metric(f"+{mfn_duty*100:.0f}% duty + freight", f"€{cn_landed_mid:,.0f} landed")
with col3:
    a_test_cn = {**assumptions, "china_equipment_cost": cn_sel["capex_mid"],
                 "china_landed_cost": cn_landed_mid}
    capex_total_cn = get_total_capex(a_test_cn, "china_insource")
    st.metric("Total CAPEX (incl. install etc.)", fmt_eur(capex_total_cn))
with col4:
    kpis_test_cn = build_summary_kpis(a_test_cn)
    pb_cn = kpis_test_cn["payback_china"]
    st.metric("Payback Period", f"Year {pb_cn}" if pb_cn else t("not_within_5yr"))

st.info(f"ℹ️ {cn_sel['note']}")

st.divider()


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3 — SIDE-BY-SIDE COMPARISON
# ═══════════════════════════════════════════════════════════════════════════

st.subheader("⚖️ " + ("Head-to-Head: Selected Machines" if lang == "en"
                        else "Comparación Directa: Máquinas Seleccionadas"))

comp_data = {
    "Metric": [
        "Brand / Model",
        "Power Class",
        "Equipment Cost (mid, after discounts)",
        "Est. Total CAPEX",
        "Annual Maintenance (% CAPEX)",
        "Payback Period",
        "ARPOL Product Fit",
        "After-Sales in Spain",
        "Parts Lead Time",
    ],
    t("scenario_eu"): [
        f"{eu_sel['brand']} {eu_sel['model']}",
        f"{eu_sel['power_kw']} kW",
        fmt_eur(eu_disc_mid),
        fmt_eur(capex_total),
        f"{assumptions['eu_maintenance_pct']*100:.0f}%/yr",
        f"Year {kpis_test['payback_eu']}" if kpis_test.get("payback_eu") else "Beyond Yr 5",
        eu_sel["arpol_fit"].title(),
        "✅ Strong (Iberian service network)",
        "2–4 weeks",
    ],
    t("scenario_china"): [
        f"{cn_sel['brand']} {cn_sel['model']}",
        f"{cn_sel['power_kw']} kW",
        fmt_eur(cn_landed_mid) + " (landed)",
        fmt_eur(capex_total_cn),
        f"{assumptions['china_maintenance_pct']*100:.0f}%/yr",
        f"Year {kpis_test_cn['payback_china']}" if kpis_test_cn.get("payback_china") else "Beyond Yr 5",
        cn_sel["arpol_fit"].title(),
        "⚠️ Limited (check distributor)",
        "4–12 weeks ex-China",
    ],
}

comp_df = pd.DataFrame(comp_data)
st.dataframe(comp_df, use_container_width=True, hide_index=True)
