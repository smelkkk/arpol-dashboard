"""
Home.py — ARPOL Laser-Cutting Investment Decision Dashboard
Main entry point (landing page).

Run:  streamlit run Home.py
"""

import streamlit as st

# ── Page config (MUST be first Streamlit call) ─────────────────────────────
st.set_page_config(
    page_title="ARPOL Investment Dashboard",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.i18n import t, get_lang
from src.assumptions import get_default_assumptions, merge_overrides
from src.tco_engine import build_summary_kpis
from src.working_capital import compute_wc_release
from components.sidebar import render_sidebar
from components.kpi_cards import render_executive_kpis, render_capex_row, render_roi_npv_row
from components.charts import (
    cumulative_cashflow_chart,
    tco_comparison_bar,
    cumulative_savings_chart,
)
from src.config import COLORS, fmt_eur


# ── Session state defaults ─────────────────────────────────────────────────
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"


# ── Sidebar + assumption loading ────────────────────────────────────────────
defaults  = get_default_assumptions()
overrides = render_sidebar(defaults)
assumptions = merge_overrides(defaults, overrides)


# ── Compute KPIs ────────────────────────────────────────────────────────────
kpis = build_summary_kpis(assumptions)
wc   = compute_wc_release(assumptions)
kpis["wc_release"]    = wc["inv_released_onetime_eur"]
kpis["discount_rate"] = assumptions["discount_rate"] * 100


# ═══════════════════════════════════════════════════════════════════════════
# PAGE HEADER
# ═══════════════════════════════════════════════════════════════════════════

st.markdown(
    f"""
    <div style='background:linear-gradient(135deg,{COLORS["primary"]} 0%,#2c4a7c 100%);
                padding:28px 36px;border-radius:12px;margin-bottom:24px'>
        <h1 style='color:white;margin:0;font-size:1.8rem;font-weight:700'>
            ⚙️ ARPOL — Laser-Cutting Investment Decision
        </h1>
        <p style='color:#cce0ff;margin:8px 0 0 0;font-size:0.95rem'>
            ESADE MSc Consulting · Challenge 4: Production Improvement &amp; Laser-Cutting Investment Assessment
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ── Placeholder warning banner ─────────────────────────────────────────────
st.warning(t("placeholder_warning"))


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1 — HEADLINE KPIs
# ═══════════════════════════════════════════════════════════════════════════

st.subheader(t("title_exec"))
render_executive_kpis(kpis)

st.divider()
render_capex_row(kpis)

st.divider()
render_roi_npv_row(kpis)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2 — SIGNATURE CHARTS
# ═══════════════════════════════════════════════════════════════════════════

st.subheader("📈 " + ("Cash Flow Analysis" if get_lang() == "en" else "Análisis de Flujo de Caja"))

col_left, col_right = st.columns(2)
df = kpis["df"]

with col_left:
    st.plotly_chart(cumulative_cashflow_chart(df), use_container_width=True)

with col_right:
    st.plotly_chart(tco_comparison_bar(kpis), use_container_width=True)

st.plotly_chart(cumulative_savings_chart(df), use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3 — KEY MESSAGES
# ═══════════════════════════════════════════════════════════════════════════

st.subheader("📋 " + t("key_messages"))

msg_color_map = {
    "msg1": COLORS["positive"],
    "msg2": COLORS["eu_insource"],
    "msg3": COLORS["accent"],
    "msg4": COLORS["positive"],
    "msg5": COLORS["negative"],
}

for key, color in msg_color_map.items():
    msg = t(key)
    st.markdown(
        f"""<div style='background:#f8f9fa;border-left:4px solid {color};
                        padding:10px 16px;border-radius:0 8px 8px 0;margin:6px 0;
                        font-size:0.92rem;color:{COLORS["primary"]}'>
            {msg}
        </div>""",
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4 — YEAR-BY-YEAR CASHFLOW TABLE
# ═══════════════════════════════════════════════════════════════════════════

with st.expander(
    "📊 " + ("Year-by-Year Cash Flow Detail" if get_lang() == "en" else "Detalle Flujo de Caja por Año")
):
    display_df = df[["year", "outsource", "eu_insource", "china_insource",
                      "eu_savings_cumul", "china_savings_cumul"]].copy()
    display_df.columns = [
        t("year"),
        t("scenario_outsource") + " (€)",
        t("scenario_eu") + " (€)",
        t("scenario_china") + " (€)",
        "EU Cumul. Savings (€)" if get_lang() == "en" else "Ahorro Acum. UE (€)",
        "China Cumul. Savings (€)" if get_lang() == "en" else "Ahorro Acum. China (€)",
    ]
    st.dataframe(
        display_df.style.format({col: "€{:,.0f}" for col in display_df.columns[1:]}),
        use_container_width=True,
        hide_index=True,
    )


# ── Footer ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style='margin-top:40px;padding:12px;text-align:center;
                color:#95a5a6;font-size:0.78rem;border-top:1px solid #ecf0f1'>
        ARPOL × ESADE Consulting 2026 · Indicative model — figures subject to final supplier confirmation
    </div>
    """,
    unsafe_allow_html=True,
)
