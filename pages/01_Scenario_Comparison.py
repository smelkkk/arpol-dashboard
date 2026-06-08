"""
pages/01_Scenario_Comparison.py — Side-by-side TCO scenario analysis.
"""

import streamlit as st

st.set_page_config(page_title="Scenario Comparison | ARPOL", page_icon="📊", layout="wide")

from src.assumptions import get_default_assumptions, merge_overrides
from src.tco_engine import (
    build_summary_kpis,
    compute_eu_capex_breakdown,
    compute_china_capex_breakdown,
    compute_annual_insource_opex,
    compute_annual_outsource_cost,
    compute_scenario_cashflows,
    compute_payback_year,
    get_total_capex,
)
from src.working_capital import compute_wc_release
from components.sidebar import render_sidebar
from components.charts import (
    annual_cashflow_grouped_bar,
    capex_breakdown_chart,
    cumulative_savings_chart,
)
from src.i18n import t, get_lang
from src.config import COLORS, fmt_eur


# ── State ──────────────────────────────────────────────────────────────────
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"

defaults    = get_default_assumptions()
overrides   = render_sidebar(defaults)
assumptions = merge_overrides(defaults, overrides)
kpis        = build_summary_kpis(assumptions)
df          = kpis["df"]
df_chart    = compute_scenario_cashflows(assumptions, year_range=range(10))
lang        = get_lang()

pb_eu    = compute_payback_year(df_chart, "eu_insource")
pb_china = compute_payback_year(df_chart, "china_insource")


# ── Header ─────────────────────────────────────────────────────────────────
st.title(f"📊 {t('title_scenario')}")
st.warning(t("placeholder_warning"))
st.divider()


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1 — CAPEX Breakdown Side-by-Side
# ═══════════════════════════════════════════════════════════════════════════

st.subheader(f"🔧 {t('capex_breakdown')}")

eu_breakdown    = compute_eu_capex_breakdown(assumptions)
china_breakdown = compute_china_capex_breakdown(assumptions)

col_eu, col_china = st.columns(2)

with col_eu:
    st.markdown(f"**{t('scenario_eu')}** — {assumptions['eu_model_name']}")
    for item, val in eu_breakdown.items():
        if item == "Total CAPEX":
            st.markdown(f"**TOTAL: {fmt_eur(val)}**")
        else:
            st.markdown(f"- {item}: {fmt_eur(val)}")

with col_china:
    st.markdown(f"**{t('scenario_china')}** — {assumptions['china_model_name']}")
    for item, val in china_breakdown.items():
        if item == "Total CAPEX":
            st.markdown(f"**TOTAL: {fmt_eur(val)}**")
        else:
            st.markdown(f"- {item}: {fmt_eur(val)}")

st.plotly_chart(
    capex_breakdown_chart(eu_breakdown, china_breakdown),
    use_container_width=True,
)
st.divider()


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2 — Annual Operating Cost Comparison
# ═══════════════════════════════════════════════════════════════════════════

st.subheader(f"💸 {t('annual_opex')} — Year 1")

col1, col2, col3 = st.columns(3)

outsource_yr1 = compute_annual_outsource_cost(assumptions, 1)
eu_yr1        = compute_annual_insource_opex(assumptions, "eu_insource", 1)
china_yr1     = compute_annual_insource_opex(assumptions, "china_insource", 1)

with col1:
    st.markdown(f"**{t('scenario_outsource')}**")
    for item, val in outsource_yr1.items():
        weight = "**" if item == "Total Cost" else ""
        st.markdown(f"{weight}{item}: {fmt_eur(val)}{weight}")

with col2:
    st.markdown(f"**{t('scenario_eu')}**")
    for item, val in eu_yr1.items():
        weight = "**" if item == "Total OpEx" else ""
        st.markdown(f"{weight}{item}: {fmt_eur(val)}{weight}")

with col3:
    st.markdown(f"**{t('scenario_china')}**")
    for item, val in china_yr1.items():
        weight = "**" if item == "Total OpEx" else ""
        st.markdown(f"{weight}{item}: {fmt_eur(val)}{weight}")

st.divider()


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3 — Year-by-Year Cashflow
# ═══════════════════════════════════════════════════════════════════════════

st.subheader(f"📅 {t('annual_cash_flow')}")
st.plotly_chart(annual_cashflow_grouped_bar(df), use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4 — Cumulative Savings & Payback
# ═══════════════════════════════════════════════════════════════════════════

st.subheader(f"🏁 {t('cumulative_savings')} & Payback")

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.metric(
        t("payback_eu"),
        f"Year {pb_eu}" if pb_eu else t("not_within_5yr"),
        help="First year cumulative EU savings exceed cumulative outsource cost",
    )
with col_b:
    st.metric(
        t("payback_china"),
        f"Year {pb_china}" if pb_china else t("not_within_5yr"),
        help="First year cumulative China savings exceed cumulative outsource cost",
    )
with col_c:
    hurdle = assumptions["payback_hurdle_years"]
    eu_ok  = "✅ Within hurdle" if (pb_eu or 99) <= hurdle else "⚠️ Exceeds hurdle"
    china_ok = "✅ Within hurdle" if (pb_china or 99) <= hurdle else "⚠️ Exceeds hurdle"
    st.markdown(f"**Payback Hurdle:** {hurdle} years")
    st.markdown(f"EU: {eu_ok}")
    st.markdown(f"China: {china_ok}")

st.plotly_chart(cumulative_savings_chart(df_chart), use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5 — Full TCO Table
# ═══════════════════════════════════════════════════════════════════════════

with st.expander("📋 Full 5-Year Cash Flow Table" if lang == "en" else "📋 Tabla Completa Flujo de Caja 5 Años"):
    display = df[["year", "outsource", "eu_insource", "china_insource",
                   "outsource_cumul", "eu_insource_cumul", "china_insource_cumul",
                   "eu_savings_cumul", "china_savings_cumul"]].copy()

    display.columns = [
        "Year", "Outsource (€)", "EU Insource (€)", "China Insource (€)",
        "Outsource Cumul (€)", "EU Cumul (€)", "China Cumul (€)",
        "EU Savings Cumul (€)", "China Savings Cumul (€)",
    ]
    st.dataframe(
        display.style.format({col: "€{:,.0f}" for col in display.columns[1:]}),
        use_container_width=True,
        hide_index=True,
    )
