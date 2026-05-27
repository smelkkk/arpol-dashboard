"""
charts.py — Reusable Plotly chart functions for the ARPOL dashboard.

All functions return a plotly Figure object.
Call `st.plotly_chart(fig, use_container_width=True)` in the page.
"""

from __future__ import annotations
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from src.config import COLORS, PLOTLY_TEMPLATE, YEAR_LABELS, ANALYSIS_YEARS
from src.i18n import t, get_lang


# ── Colour helpers ─────────────────────────────────────────────────────────

def _hex_to_rgba(hex_color: str, alpha: float = 0.15) -> str:
    """
    Convert #RRGGBB to rgba(r,g,b,alpha).
    Plotly does NOT accept 8-digit hex (#RRGGBBAA) — use this instead.
    """
    h = hex_color.lstrip("#")
    if len(h) == 6:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"rgba({r},{g},{b},{alpha})"
    return hex_color  # already in valid format (e.g. rgb/rgba string)


# ── Shared styling ─────────────────────────────────────────────────────────

def _base_layout(**kwargs) -> dict:
    return dict(
        template=PLOTLY_TEMPLATE,
        font=dict(family="Inter, Arial, sans-serif", size=13, color=COLORS["primary"]),
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=60, r=30, t=50, b=50),
        **kwargs,
    )


def _scenario_name(key: str) -> str:
    return t(f"scenario_{key.replace('_insource', '').replace('outsource', 'outsource')}")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 1 — Cumulative Cash Flow Lines (signature chart)
# ══════════════════════════════════════════════════════════════════════════════

def cumulative_cashflow_chart(df: pd.DataFrame) -> go.Figure:
    """
    Line chart: cumulative cash position for all 3 scenarios over 5 years.
    The breakeven crossing point is annotated.
    """
    years = df["year"].tolist()
    fig = go.Figure()

    scenarios = [
        ("outsource",     t("scenario_outsource"),  COLORS["outsource"],     "dot"),
        ("eu_insource",   t("scenario_eu"),          COLORS["eu_insource"],   "solid"),
        ("china_insource",t("scenario_china"),        COLORS["china_insource"],"solid"),
    ]

    for key, name, color, dash in scenarios:
        col = f"{key}_cumul"
        fig.add_trace(go.Scatter(
            x=years,
            y=df[col].tolist(),
            mode="lines+markers",
            name=name,
            line=dict(color=color, width=3, dash=dash),
            marker=dict(size=8),
            hovertemplate=f"<b>{name}</b><br>{t('year')} %{{x}}<br>€%{{y:,.0f}}<extra></extra>",
        ))

    # Zero line
    fig.add_hline(y=0, line_dash="dash", line_color=COLORS["neutral"], line_width=1)

    fig.update_layout(
        **_base_layout(
            title=dict(text=t("cumulative_cash_flow"), font=dict(size=16)),
            xaxis=dict(title=t("year"), tickvals=years, ticktext=YEAR_LABELS),
            yaxis=dict(title="€", tickformat=",.0f"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# CHART 2 — 5-Year TCO Comparison Bar Chart
# ══════════════════════════════════════════════════════════════════════════════

def tco_comparison_bar(kpis: dict) -> go.Figure:
    """
    Horizontal bar chart comparing 5-year TCO across all 3 scenarios.
    Negative values (costs) shown as absolute.
    """
    scenarios = [t("scenario_outsource"), t("scenario_eu"), t("scenario_china")]
    values    = [
        abs(kpis["tco_5yr_outsource"]),
        abs(kpis["tco_5yr_eu"]),
        abs(kpis["tco_5yr_china"]),
    ]
    colors = [COLORS["outsource"], COLORS["eu_insource"], COLORS["china_insource"]]

    fig = go.Figure(go.Bar(
        x=values,
        y=scenarios,
        orientation="h",
        marker_color=colors,
        text=[f"€{v:,.0f}" for v in values],
        textposition="outside",
        hovertemplate="%{y}: €%{x:,.0f}<extra></extra>",
    ))

    fig.update_layout(
        **_base_layout(
            title=dict(text=t("5yr_tco"), font=dict(size=16)),
            xaxis=dict(title="€", tickformat=",.0f"),
            yaxis=dict(title=""),
            showlegend=False,
        )
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# CHART 3 — Annual Cash Flow Waterfall / Bar
# ══════════════════════════════════════════════════════════════════════════════

def annual_cashflow_grouped_bar(df: pd.DataFrame) -> go.Figure:
    """
    Grouped bar chart: annual cash flow per year for each scenario.
    """
    years = df["year"].tolist()
    fig = go.Figure()

    scenarios = [
        ("outsource",      t("scenario_outsource"),   COLORS["outsource"]),
        ("eu_insource",    t("scenario_eu"),           COLORS["eu_insource"]),
        ("china_insource", t("scenario_china"),         COLORS["china_insource"]),
    ]

    for key, name, color in scenarios:
        fig.add_trace(go.Bar(
            x=years,
            y=df[key].tolist(),
            name=name,
            marker_color=color,
            opacity=0.85,
            hovertemplate=f"<b>{name}</b><br>{t('year')} %{{x}}<br>€%{{y:,.0f}}<extra></extra>",
        ))

    fig.add_hline(y=0, line_color=COLORS["neutral"], line_width=1)

    fig.update_layout(
        **_base_layout(
            barmode="group",
            title=dict(text=t("annual_cash_flow"), font=dict(size=16)),
            xaxis=dict(title=t("year"), tickvals=years, ticktext=YEAR_LABELS),
            yaxis=dict(title="€", tickformat=",.0f"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# CHART 4 — Cumulative Savings vs Outsourcing
# ══════════════════════════════════════════════════════════════════════════════

def cumulative_savings_chart(df: pd.DataFrame) -> go.Figure:
    """
    Area chart: cumulative savings of EU and China insource vs outsourcing.
    Positive = insource is ahead of outsourcing on cumulative basis.
    The zero crossing = payback year.
    """
    years = df["year"].tolist()
    fig = go.Figure()

    for key, name, color in [
        ("eu_savings_cumul",    t("scenario_eu"),    COLORS["eu_insource"]),
        ("china_savings_cumul", t("scenario_china"),  COLORS["china_insource"]),
    ]:
        y_vals = df[key].tolist()
        fig.add_trace(go.Scatter(
            x=years,
            y=y_vals,
            mode="lines+markers",
            name=name,
            line=dict(color=color, width=3),
            marker=dict(size=8),
            fill="tozeroy",
            fillcolor=_hex_to_rgba(color, 0.15),
            hovertemplate=f"<b>{name}</b><br>{t('year')} %{{x}}<br>Savings: €%{{y:,.0f}}<extra></extra>",
        ))

    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color=COLORS["negative"],
        line_width=2,
        annotation_text="Payback threshold" if get_lang() == "en" else "Umbral de recuperación",
        annotation_position="top right",
    )

    fig.update_layout(
        **_base_layout(
            title=dict(text=t("cumulative_savings"), font=dict(size=16)),
            xaxis=dict(title=t("year"), tickvals=years, ticktext=YEAR_LABELS),
            yaxis=dict(title="€", tickformat=",.0f"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# CHART 5 — CAPEX Breakdown Stacked Bar
# ══════════════════════════════════════════════════════════════════════════════

def capex_breakdown_chart(eu_breakdown: dict, china_breakdown: dict) -> go.Figure:
    """
    Stacked horizontal bar showing CAPEX line items for EU vs China.
    """
    # Filter out the "Total CAPEX" summary row
    eu_items    = {k: v for k, v in eu_breakdown.items()    if k != "Total CAPEX"}
    china_items = {k: v for k, v in china_breakdown.items() if k != "Total CAPEX"}

    # Merge all possible line-item labels
    all_items = list(dict.fromkeys(list(eu_items.keys()) + list(china_items.keys())))

    scenarios = [t("scenario_eu"), t("scenario_china")]
    fig = go.Figure()

    palette = px.colors.qualitative.Set3
    for i, item in enumerate(all_items):
        eu_val    = eu_items.get(item, 0)
        china_val = china_items.get(item, 0)
        fig.add_trace(go.Bar(
            name=item,
            x=scenarios,
            y=[eu_val, china_val],
            marker_color=palette[i % len(palette)],
            hovertemplate=f"<b>{item}</b><br>€%{{y:,.0f}}<extra></extra>",
        ))

    fig.update_layout(
        **_base_layout(
            barmode="stack",
            title=dict(text=t("capex_breakdown"), font=dict(size=16)),
            yaxis=dict(title="€", tickformat=",.0f"),
            xaxis=dict(title=""),
            legend=dict(orientation="v", x=1.02, y=1),
        )
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# CHART 6 — Tornado Chart
# ══════════════════════════════════════════════════════════════════════════════

def tornado_chart(tornado_df: pd.DataFrame, scenario: str = "eu_insource") -> go.Figure:
    """
    Horizontal bar tornado chart.
    tornado_df: output of run_tornado() from sensitivity.py.

    X-axis: Δ 5-year cumulative savings (€) — continuous metric.
      Positive bars  = variable increase HELPS the insource case (more savings).
      Negative bars  = variable increase HURTS the insource case (fewer savings).

    Two bars per variable (stacked from centre):
      Blue  = effect when variable goes DOWN (−20%)
      Red   = effect when variable goes UP   (+20%)
    """
    lang      = get_lang()
    label_col = "label_en" if lang == "en" else "label_es"

    top_n = min(8, len(tornado_df))
    df    = tornado_df.head(top_n).copy()
    df    = df.sort_values("impact", ascending=True)   # largest impact at top

    labels       = df[label_col].tolist()
    effect_high  = df["effect_high"].tolist()   # Δ savings when var goes UP
    effect_low   = df["effect_low"].tolist()    # Δ savings when var goes DOWN
    savings_high = df["savings_high"].tolist()
    savings_low  = df["savings_low"].tolist()

    fig = go.Figure()

    # ── Bar: variable INCREASED (+20%) ────────────────────────────────
    fig.add_trace(go.Bar(
        name="↑ +20% variable" if lang == "en" else "↑ +20% variable",
        y=labels,
        x=effect_high,
        orientation="h",
        marker=dict(
            color=[COLORS["positive"] if v > 0 else COLORS["outsource"] for v in effect_high],
            opacity=0.85,
        ),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Variable +20%<br>"
            "5yr Savings: €%{customdata:,.0f}<br>"
            "Δ vs base: €%{x:,.0f}"
            "<extra></extra>"
        ),
        customdata=savings_high,
    ))

    # ── Bar: variable DECREASED (−20%) ────────────────────────────────
    fig.add_trace(go.Bar(
        name="↓ −20% variable" if lang == "en" else "↓ −20% variable",
        y=labels,
        x=effect_low,
        orientation="h",
        marker=dict(
            color=[COLORS["positive"] if v > 0 else COLORS["eu_insource"] for v in effect_low],
            opacity=0.55,
        ),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Variable −20%<br>"
            "5yr Savings: €%{customdata:,.0f}<br>"
            "Δ vs base: €%{x:,.0f}"
            "<extra></extra>"
        ),
        customdata=savings_low,
    ))

    # Centre reference line
    fig.add_vline(x=0, line_width=2, line_color=COLORS["primary"])

    x_title = (
        "Δ 5-Year Savings vs Outsourcing (€)" if lang == "en"
        else "Δ Ahorro 5 años vs Subcontrato (€)"
    )

    fig.update_layout(
        **_base_layout(
            barmode="overlay",
            title=dict(text=t("tornado_title"), font=dict(size=16)),
            xaxis=dict(
                title=x_title,
                tickformat=",.0f",
                zeroline=True,
                zerolinecolor=COLORS["primary"],
                tickprefix="€",
            ),
            yaxis=dict(title=""),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# CHART 7 — Payback Heatmap
# ══════════════════════════════════════════════════════════════════════════════

def payback_heatmap(
    vol_grid: np.ndarray,
    capex_grid: np.ndarray,
    matrix: np.ndarray,
    scenario: str,
) -> go.Figure:
    """
    2D heatmap: payback period across volume growth (x) and CAPEX multiplier (y).
    """
    title = t("heatmap_eu_title") if scenario == "eu_insource" else t("heatmap_china_title")

    # Clip display at 5.5 (= "beyond 5 years")
    z = np.clip(matrix, 1, 5.5)

    fig = go.Figure(go.Heatmap(
        x=[f"{v*100:.0f}%" for v in vol_grid],
        y=[f"{c*100:.0f}%" for c in capex_grid],
        z=z,
        colorscale=[
            [0.0,  "#1E8449"],   # year 1 — excellent (green)
            [0.25, "#27AE60"],   # year 2 — good
            [0.50, "#F39C12"],   # year 3 — acceptable (amber)
            [0.75, "#E67E22"],   # year 4 — borderline
            [1.0,  "#C0392B"],   # year 5+ — poor (red)
        ],
        zmin=1, zmax=5.5,
        colorbar=dict(
            title="Payback (yrs)",
            tickvals=[1, 2, 3, 4, 5],
            ticktext=["Yr 1", "Yr 2", "Yr 3", "Yr 4", "Yr 5+"],
        ),
        hovertemplate=(
            "Volume Growth: %{x}<br>"
            "CAPEX Multiplier: %{y}<br>"
            "Payback: %{z:.1f} yrs<extra></extra>"
        ),
    ))

    fig.update_layout(
        **_base_layout(
            title=dict(text=title, font=dict(size=16)),
            xaxis=dict(title="Volume Growth Rate (% p.a.)"),
            yaxis=dict(title="CAPEX vs Base Case"),
        )
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# CHART 8 — Working Capital Waterfall
# ══════════════════════════════════════════════════════════════════════════════

def wc_release_waterfall(wc: dict) -> go.Figure:
    """
    Waterfall chart showing the working capital release mechanics.
    """
    lang = get_lang()

    labels = [
        "Current Coil Inventory" if lang == "en" else "Inventario Bobinas Actual",
        "SKUs Eliminated" if lang == "en" else "SKU Eliminados",
        "One-time Release" if lang == "en" else "Liberación Única",
        f"Annual Saving × 5 yrs" if lang == "en" else f"Ahorro Anual × 5 años",
        "5-yr Total WC Benefit" if lang == "en" else "Beneficio Total 5 años",
    ]

    values = [
        wc["total_coil_inv_value_eur"],
        -wc["inv_released_onetime_eur"],         # reduction step
        wc["inv_released_onetime_eur"],
        wc["annual_holding_saved_eur"] * 5,
        wc["total_5yr_wc_benefit_eur"],
    ]

    measure = ["absolute", "relative", "absolute", "relative", "total"]

    fig = go.Figure(go.Waterfall(
        name="",
        orientation="v",
        measure=measure,
        x=labels,
        y=values,
        text=[f"€{abs(v):,.0f}" for v in values],
        textposition="outside",
        connector=dict(line=dict(color=COLORS["neutral"])),
        increasing=dict(marker_color=COLORS["positive"]),
        decreasing=dict(marker_color=COLORS["negative"]),
        totals=dict(marker_color=COLORS["eu_insource"]),
        hovertemplate="%{x}<br>€%{y:,.0f}<extra></extra>",
    ))

    fig.update_layout(
        **_base_layout(
            title=dict(text=t("sku_impact"), font=dict(size=16)),
            yaxis=dict(title="€", tickformat=",.0f"),
            xaxis=dict(title=""),
            showlegend=False,
        )
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# CHART 9 — Subcontract Sensitivity Line Chart
# ══════════════════════════════════════════════════════════════════════════════

def subcontract_sensitivity_chart(sens_df: pd.DataFrame) -> go.Figure:
    """
    Line chart: EU and China payback as subcontract spend varies.
    """
    lang = get_lang()
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=sens_df["Subcontract Spend (€/yr)"],
        y=sens_df["EU Payback (yrs)"],
        mode="lines+markers",
        name=t("scenario_eu"),
        line=dict(color=COLORS["eu_insource"], width=3),
        marker=dict(size=8),
    ))

    fig.add_trace(go.Scatter(
        x=sens_df["Subcontract Spend (€/yr)"],
        y=sens_df["China Payback (yrs)"],
        mode="lines+markers",
        name=t("scenario_china"),
        line=dict(color=COLORS["china_insource"], width=3),
        marker=dict(size=8),
    ))

    # Payback hurdle line
    fig.add_hline(
        y=4,
        line_dash="dash",
        line_color=COLORS["accent"],
        annotation_text="4-yr hurdle" if lang == "en" else "Umbral 4 años",
        annotation_position="top right",
    )

    fig.update_layout(
        **_base_layout(
            title=dict(
                text="Payback Sensitivity to Subcontract Spend" if lang == "en"
                     else "Sensibilidad de Recuperación al Gasto en Subcontrato",
                font=dict(size=16),
            ),
            xaxis=dict(title="Annual Subcontract Spend (€)" if lang == "en" else "Gasto Anual Subcontrato (€)",
                       tickformat=",.0f"),
            yaxis=dict(title="Payback (years)" if lang == "en" else "Recuperación (años)",
                       range=[0, 7]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
    )
    return fig
