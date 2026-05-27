"""
kpi_cards.py — Reusable KPI metric card components for the ARPOL dashboard.
"""

import streamlit as st
from src.config import COLORS, fmt_eur, fmt_pct
from src.i18n import t


def metric_card(
    label: str,
    value: str,
    delta: str | None = None,
    color: str = COLORS["primary"],
    icon: str = "",
    help_text: str | None = None,
):
    """Render a single styled KPI card using st.metric."""
    col_label = f"{icon} {label}" if icon else label
    st.metric(
        label=col_label,
        value=value,
        delta=delta,
        help=help_text,
    )


def payback_badge(years: int | None, scenario_color: str, lang: str = "en") -> str:
    """Return an HTML-styled payback badge string."""
    if years is None:
        label = t("not_within_5yr")
        color = COLORS["negative"]
    elif years <= 2:
        label = f"Year {years}" if lang == "en" else f"Año {years}"
        color = COLORS["positive"]
    elif years <= 4:
        label = f"Year {years}" if lang == "en" else f"Año {years}"
        color = COLORS["accent"]
    else:
        label = f"Year {years}" if lang == "en" else f"Año {years}"
        color = COLORS["negative"]
    return f'<span style="background:{color};color:white;padding:4px 12px;border-radius:12px;font-weight:700">{label}</span>'


def render_executive_kpis(kpis: dict):
    """
    Render the top KPI row for the Executive Summary page.
    kpis: output of build_summary_kpis()
    """
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label=f"🏭 {t('payback_eu')}",
            value=f"Year {kpis['payback_eu']}" if kpis["payback_eu"] else t("not_within_5yr"),
            help="Year in which EU insource scenario cumulative cost < outsourcing cumulative cost",
        )

    with col2:
        st.metric(
            label=f"🌏 {t('payback_china')}",
            value=f"Year {kpis['payback_china']}" if kpis["payback_china"] else t("not_within_5yr"),
            help="Year in which China insource scenario cumulative cost < outsourcing cumulative cost",
        )

    with col3:
        sv_eu = kpis["savings_5yr_eu"]
        st.metric(
            label=f"💰 {t('5yr_savings_eu')}",
            value=fmt_eur(sv_eu),
            delta="vs outsourcing",
            delta_color="normal" if sv_eu > 0 else "inverse",
        )

    with col4:
        sv_cn = kpis["savings_5yr_china"]
        st.metric(
            label=f"💰 {t('5yr_savings_china')}",
            value=fmt_eur(sv_cn),
            delta="vs outsourcing",
            delta_color="normal" if sv_cn > 0 else "inverse",
        )

    with col5:
        wc = kpis.get("wc_release", 112_000)  # passed from WC module
        st.metric(
            label=f"📦 {t('wc_release')}",
            value=fmt_eur(wc),
            help="One-time working capital release from coil-to-sheet SKU rationalisation",
        )


def render_capex_row(kpis: dict):
    """Render CAPEX comparison row."""
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(t("capex_year0") + " (Outsourcing)", "€0", help="No CAPEX — continue status quo")
    with col2:
        st.metric(t("capex_year0") + " (EU)", fmt_eur(kpis["capex_eu"]),
                  help="Equipment + install + commission + training + tooling + spares + ancillary")
    with col3:
        st.metric(t("capex_year0") + " (China)", fmt_eur(kpis["capex_china"]),
                  help="Equipment + duty + freight + install + commission + training + tooling + spares + ancillary")


def render_roi_npv_row(kpis: dict):
    """Render ROI and NPV row."""
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        roi_eu = kpis.get("roi_eu")
        st.metric(
            label=f"{t('roi')} (EU)",
            value=fmt_pct(roi_eu) if roi_eu else "n/a",
            help="5-year cumulative savings / EU CAPEX",
        )
    with col2:
        roi_cn = kpis.get("roi_china")
        st.metric(
            label=f"{t('roi')} (China)",
            value=fmt_pct(roi_cn) if roi_cn else "n/a",
            help="5-year cumulative savings / China CAPEX",
        )
    with col3:
        npv_eu = kpis.get("npv_eu")
        st.metric(
            label=f"{t('npv')} (EU)",
            value=fmt_eur(npv_eu) if npv_eu else "n/a",
            help=f"NPV of incremental cash flows at {kpis.get('discount_rate', 8):.0f}% WACC",
        )
    with col4:
        npv_cn = kpis.get("npv_china")
        st.metric(
            label=f"{t('npv')} (China)",
            value=fmt_eur(npv_cn) if npv_cn else "n/a",
            help=f"NPV of incremental cash flows at {kpis.get('discount_rate', 8):.0f}% WACC",
        )
