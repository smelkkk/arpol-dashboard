"""
pages/03_Working_Capital.py — SKU rationalisation and working capital release.
"""

import streamlit as st

st.set_page_config(page_title="Working Capital | ARPOL", page_icon="📦", layout="wide")

from src.assumptions import get_default_assumptions, merge_overrides
from src.working_capital import compute_wc_release, compute_wc_timeline, get_sku_table
from components.sidebar import render_sidebar
from components.charts import wc_release_waterfall
from src.i18n import t, get_lang
from src.config import COLORS, fmt_eur


# ── State ──────────────────────────────────────────────────────────────────
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"

defaults    = get_default_assumptions()
overrides   = render_sidebar(defaults)
assumptions = merge_overrides(defaults, overrides)
lang        = get_lang()

wc = compute_wc_release(assumptions)


# ── Header ─────────────────────────────────────────────────────────────────
st.title(f"📦 {t('title_wc')}")
st.markdown(
    """
    > **Key strategic insight from Manuel (CEO interview):**
    > ARPOL currently holds ~8 different coil SKUs per material thickness to produce different ring geometries.
    > Switching to laser-cutting from **coil stock → sheet stock** collapses all rings of a given thickness
    > into **one sheet SKU**. This is a major working capital and procurement complexity reduction —
    > independent of which laser supplier is chosen.
    """
    if lang == "en" else
    """
    > **Perspectiva estratégica clave de Manuel (entrevista CEO):**
    > ARPOL actualmente mantiene ~8 SKU de bobinas diferentes por espesor de material para producir
    > diferentes geometrías de anillos. Cambiar de **stock de bobinas → stock de chapas** colapsa
    > todos los anillos de un espesor dado en **un único SKU de chapa**. Esta es una reducción
    > importante de capital de trabajo y complejidad de aprovisionamiento — independiente del proveedor de láser elegido.
    """
)
st.divider()


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1 — HEADLINE WC NUMBERS
# ═══════════════════════════════════════════════════════════════════════════

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Current Coil Inventory" if lang == "en" else "Inventario Bobinas Actual",
        fmt_eur(wc["total_coil_inv_value_eur"]),
        help=f"{wc['total_coil_skus_today']} SKUs × {fmt_eur(wc['avg_inventory_per_sku_eur'])} avg",
    )
with col2:
    st.metric(
        "One-Time WC Release" if lang == "en" else "Liberación Única Capital",
        fmt_eur(wc["inv_released_onetime_eur"]),
        delta="One-time benefit" if lang == "en" else "Beneficio único",
        delta_color="normal",
    )
with col3:
    st.metric(
        "Annual Holding Cost Saved" if lang == "en" else "Ahorro Anual Costo de Tenencia",
        fmt_eur(wc["annual_holding_saved_eur"]) + "/yr",
        help=f"{wc['inventory_holding_rate_pct']*100:.0f}% holding rate × released inventory",
    )
with col4:
    st.metric(
        "5-Year Total WC Benefit" if lang == "en" else "Beneficio Total Capital 5 Años",
        fmt_eur(wc["total_5yr_wc_benefit_eur"]),
        delta="Applies to BOTH insource scenarios" if lang == "en"
              else "Aplica a AMBOS escenarios de insourcing",
        delta_color="normal",
    )

st.divider()


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2 — WATERFALL CHART
# ═══════════════════════════════════════════════════════════════════════════

st.subheader("📊 " + (t("sku_impact")))
st.plotly_chart(wc_release_waterfall(wc), use_container_width=True)

st.divider()


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3 — SKU RATIONALISATION TABLE
# ═══════════════════════════════════════════════════════════════════════════

st.subheader("🗂️ " + ("SKU Profile: Before & After" if lang == "en"
                        else "Perfil SKU: Antes y Después"))

sku_df = get_sku_table(assumptions)
st.dataframe(
    sku_df.style
        .format({"Inventory Released (€)": "€{:,.0f}"})
        .highlight_max(subset=["SKUs Eliminated"], color="#d4edda")
        .bar(subset=["SKUs Eliminated"], color=COLORS["positive"] + "50"),
    use_container_width=True,
    hide_index=True,
)

# Summary
total_eliminated = sku_df["SKUs Eliminated"].sum()
total_remaining  = sku_df["Current SKUs (coil)"].sum() - total_eliminated
total_released   = sku_df["Inventory Released (€)"].sum()

col_a, col_b, col_c = st.columns(3)
with col_a:
    st.metric("Total SKUs Today" if lang == "en" else "SKU Totales Hoy",
              int(sku_df["Current SKUs (coil)"].sum()))
with col_b:
    st.metric("SKUs After Rationalisation" if lang == "en" else "SKU Tras Racionalización",
              int(total_remaining))
with col_c:
    st.metric("Total Inventory Released" if lang == "en" else "Inventario Total Liberado",
              fmt_eur(total_released))

st.divider()


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4 — CALCULATION LOGIC TRANSPARENCY
# ═══════════════════════════════════════════════════════════════════════════

with st.expander("🔎 Calculation Logic" if lang == "en" else "🔎 Lógica del Cálculo"):
    st.markdown(f"""
    | Parameter | Value | Source |
    |---|---|---|
    | Coil SKUs per thickness | {wc['coil_skus_per_thickness']} | ✅ Confirmed by Manuel |
    | Number of thickness grades | {wc['thickness_grades']} | 📐 Client estimate |
    | Total coil SKUs held today | {wc['total_coil_skus_today']} | = above × above |
    | Avg inventory value per SKU | {fmt_eur(wc['avg_inventory_per_sku_eur'])} | 📊 Steel pricing benchmark |
    | Current coil inventory value | {fmt_eur(wc['total_coil_inv_value_eur'])} | = SKUs × avg value |
    | SKU reduction rate | {wc['sku_reduction_rate_pct']*100:.0f}% | ⚠️ Hypothesis — validate |
    | SKUs eliminated | {wc['skus_eliminated']} | = total × reduction rate |
    | One-time inventory release | {fmt_eur(wc['inv_released_onetime_eur'])} | = eliminated × avg value |
    | Inventory holding cost rate | {wc['inventory_holding_rate_pct']*100:.0f}%/yr | 📊 Industry benchmark |
    | Annual holding cost saved | {fmt_eur(wc['annual_holding_saved_eur'])}/yr | = release × holding rate |
    | 5-year total WC benefit | {fmt_eur(wc['total_5yr_wc_benefit_eur'])} | = one-time + 5 × annual |
    """)
    st.info(
        "⚠️ The SKU reduction rate (70%) is a hypothesis based on the coil-to-sheet shift logic. "
        "This should be validated with the production and procurement team before the Board presentation."
        if lang == "en" else
        "⚠️ La tasa de reducción de SKU (70%) es una hipótesis basada en la lógica del cambio de bobina a chapa. "
        "Esto debe validarse con el equipo de producción y aprovisionamiento antes de la presentación al Consejo."
    )
