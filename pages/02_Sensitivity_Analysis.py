"""
pages/02_Sensitivity_Analysis.py — Tornado chart, heatmaps, and subcontract sensitivity.
"""

import streamlit as st

st.set_page_config(page_title="Sensitivity Analysis | ARPOL", page_icon="🎯", layout="wide")

from src.assumptions import get_default_assumptions, merge_overrides
from src.sensitivity import run_tornado, compute_payback_heatmap, subcontract_sensitivity
from components.sidebar import render_sidebar
from components.charts import tornado_chart, payback_heatmap, subcontract_sensitivity_chart
from src.i18n import t, get_lang
from src.config import COLORS


# ── State ──────────────────────────────────────────────────────────────────
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"

defaults    = get_default_assumptions()
overrides   = render_sidebar(defaults)
assumptions = merge_overrides(defaults, overrides)
lang        = get_lang()


# ── Header ─────────────────────────────────────────────────────────────────
st.title(f"🎯 {t('title_sensitivity')}")
st.divider()


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1 — TORNADO CHART (EU Payback)
# ═══════════════════════════════════════════════════════════════════════════

st.subheader(f"🌪️ {t('tornado_title')}")

scenario_choice = st.radio(
    "Analyze payback for:" if lang == "en" else "Analizar recuperación para:",
    options=["eu_insource", "china_insource"],
    format_func=lambda x: t("scenario_eu") if x == "eu_insource" else t("scenario_china"),
    horizontal=True,
)

with st.spinner("Computing sensitivity..." if lang == "en" else "Calculando sensibilidad..."):
    tornado_df = run_tornado(assumptions, scenario=scenario_choice)

st.plotly_chart(tornado_chart(tornado_df, scenario=scenario_choice), use_container_width=True)

# ── Tornado table ────────────────────────────────────────────────────────
with st.expander("📋 Tornado Data Table" if lang == "en" else "📋 Tabla Datos Tornado"):
    label_col = "label_en" if lang == "en" else "label_es"
    display_tornado = tornado_df[[
        label_col, "base_value", "val_low", "val_high",
        "savings_base", "savings_low", "savings_high", "effect_low", "effect_high", "impact"
    ]].copy()
    display_tornado.columns = [
        "Variable", "Base Value", "Low (−20%)", "High (+20%)",
        "Base Savings (€)", "Savings Low (€)", "Savings High (€)",
        "Δ Low (€)", "Δ High (€)", "Total Swing (€)",
    ]
    st.dataframe(
        display_tornado.style.format({
            col: "€{:,.0f}" for col in display_tornado.columns if "(€)" in col
        }),
        use_container_width=True, hide_index=True,
    )

st.divider()


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2 — PAYBACK HEATMAPS
# ═══════════════════════════════════════════════════════════════════════════

st.subheader("🗺️ " + ("Payback Heatmaps — Volume Growth × CAPEX" if lang == "en"
                       else "Mapas de Calor — Crecimiento de Volumen × CAPEX"))
st.markdown(
    "Color = payback year. **Green = better, Red = worse.** "
    "Find the 'safe zone' where the recommendation holds across assumption ranges."
    if lang == "en" else
    "Color = año de recuperación. **Verde = mejor, Rojo = peor.** "
    "Identifique la 'zona segura' donde la recomendación se mantiene."
)

col_eu, col_cn = st.columns(2)

with st.spinner("Building heatmaps..." if lang == "en" else "Generando mapas de calor..."):
    vol_eu, capex_eu, mat_eu = compute_payback_heatmap(assumptions, "eu_insource")
    vol_cn, capex_cn, mat_cn = compute_payback_heatmap(assumptions, "china_insource")

with col_eu:
    st.plotly_chart(payback_heatmap(vol_eu, capex_eu, mat_eu, "eu_insource"),
                    use_container_width=True)

with col_cn:
    st.plotly_chart(payback_heatmap(vol_cn, capex_cn, mat_cn, "china_insource"),
                    use_container_width=True)

st.caption(
    "X-axis: annual volume growth rate. Y-axis: CAPEX as % of base-case mid estimate. "
    "Payback '6' means beyond 5-year horizon."
    if lang == "en" else
    "Eje X: tasa de crecimiento de volumen anual. Eje Y: CAPEX como % del caso base. "
    "Recuperación '6' significa más de 5 años."
)

st.divider()


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3 — SUBCONTRACT SPEND SENSITIVITY (highest-impact variable)
# ═══════════════════════════════════════════════════════════════════════════

st.subheader("💰 " + ("Subcontract Spend Sensitivity" if lang == "en"
                       else "Sensibilidad al Gasto en Subcontrato"))
st.markdown(
    "⚠️ **This is the highest-impact unknown.** "
    "The baseline (€120K/yr) is a placeholder. "
    "This chart shows how payback changes if the real spend is higher or lower."
    if lang == "en" else
    "⚠️ **Esta es la variable desconocida de mayor impacto.** "
    "La base (€120K/año) es un estimado. "
    "Este gráfico muestra cómo cambia la recuperación si el gasto real es mayor o menor."
)

with st.spinner("Running subcontract sensitivity..." if lang == "en"
                else "Ejecutando sensibilidad subcontrato..."):
    sens_df = subcontract_sensitivity(assumptions)

st.plotly_chart(subcontract_sensitivity_chart(sens_df), use_container_width=True)

st.dataframe(
    sens_df.style.format({
        "Subcontract Multiplier"   : "{:.0%}",
        "Subcontract Spend (€/yr)" : "€{:,.0f}",
        "EU Payback (yrs)"         : "{:.1f}",
        "China Payback (yrs)"      : "{:.1f}",
    }),
    use_container_width=True,
    hide_index=True,
)

st.divider()


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4 — RISK FLAGS
# ═══════════════════════════════════════════════════════════════════════════

st.subheader(f"🚩 {t('risk_flags')}")

risks_en = [
    ("🔴 Critical", "Subcontract spend & production volume are placeholders. A 30% error changes payback by ~1 year."),
    ("🔴 Critical", "Machine power class (3kW vs 6kW) not yet confirmed — €100K+ CAPEX swing."),
    ("🟠 High",     "China spare parts lead time of 4–12 weeks creates hidden downtime risk not captured in the base model."),
    ("🟠 High",     "SKU reduction rate (70%) is a hypothesis — needs validation with production team."),
    ("🟡 Medium",   "2-shift operation not modeled — if capacity requires 2 shifts, labour cost doubles."),
    ("🟡 Medium",   "EU tariff scenarios on Chinese equipment (15% / 25%) could reduce China's payback advantage."),
    ("🟢 Low",      "Electricity rate sensitivity is modest: ±20% changes OpEx by only ~€1.3K/yr."),
]

risks_es = [
    ("🔴 Crítico", "El gasto en subcontrato y el volumen de producción son estimados. Un error del 30% cambia la recuperación ~1 año."),
    ("🔴 Crítico", "La clase de potencia del equipo (3kW vs 6kW) aún no confirmada — diferencia de >€100K en CAPEX."),
    ("🟠 Alto",    "El plazo de entrega de repuestos de China (4–12 semanas) crea riesgo de tiempo de inactividad no capturado en el modelo base."),
    ("🟠 Alto",    "La tasa de reducción de SKU (70%) es una hipótesis — necesita validación con el equipo de producción."),
    ("🟡 Medio",   "Operación en 2 turnos no modelada — si la capacidad lo requiere, el costo de personal se duplica."),
    ("🟡 Medio",   "Escenarios arancelarios de la UE sobre equipos chinos (15% / 25%) podrían reducir la ventaja de recuperación de China."),
    ("🟢 Bajo",    "La sensibilidad de la tarifa eléctrica es modesta: ±20% cambia el OpEx en solo ~€1.3K/año."),
]

risks = risks_en if lang == "en" else risks_es

for level, desc in risks:
    color = (COLORS["negative"] if "🔴" in level else
             COLORS["accent"]   if "🟠" in level else
             "#F1C40F"          if "🟡" in level else
             COLORS["positive"])
    st.markdown(
        f"""<div style='background:#f8f9fa;border-left:4px solid {color};
                        padding:8px 14px;border-radius:0 6px 6px 0;margin:4px 0;
                        font-size:0.88rem'>
            <b>{level}</b> — {desc}
        </div>""",
        unsafe_allow_html=True,
    )
