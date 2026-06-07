"""
sidebar.py — Shared sidebar controls for the ARPOL dashboard.

Call `render_sidebar(defaults)` from any page to get:
    - Language toggle
    - Scenario assumption overrides (sliders)
    - Returns an `overrides` dict ready for merge_overrides()
"""

import streamlit as st
from src.i18n import t, set_lang, get_lang
from src.config import COLORS


def render_sidebar(defaults: dict) -> dict:
    """
    Render the shared sidebar and return a dict of user overrides.
    """
    with st.sidebar:
        _render_logo()
        st.markdown("---")
        _render_language_toggle()
        st.markdown("---")
        _render_project_info()
        st.markdown("---")
        overrides = _render_assumption_controls(defaults)

    return overrides


# ── Logo / branding ───────────────────────────────────────────────────────

def _render_logo():
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #1B2A4A 0%, #2c4a7c 100%);
            border-radius: 10px;
            padding: 14px 16px 10px 16px;
            margin-bottom: 4px;
        ">
            <div style="display:flex; align-items:center; gap:10px;">
                <span style="font-size:1.6rem; line-height:1;">⚙️</span>
                <div>
                    <div style="color:#ffffff; font-size:1.05rem; font-weight:700;
                                letter-spacing:0.5px; line-height:1.2;">
                        ARPOL
                    </div>
                    <div style="color:#a8c4e8; font-size:0.7rem; line-height:1.3;
                                font-weight:400; letter-spacing:0.3px;">
                        Investment Decision Dashboard
                    </div>
                </div>
            </div>
            <div style="color:#6b9bd2; font-size:0.62rem; margin-top:6px;
                        border-top:1px solid #2c4a7c; padding-top:6px;">
                ESADE MSc Consulting · Challenge 4
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Language toggle ────────────────────────────────────────────────────────

def _render_language_toggle():
    lang = get_lang()
    choice = st.radio(
        t("language"),
        options=["en", "es"],
        index=0 if lang == "en" else 1,
        format_func=lambda x: "🇬🇧 English" if x == "en" else "🇪🇸 Español",
        horizontal=True,
        key="lang_selector",
    )
    if choice != lang:
        set_lang(choice)
        st.rerun()


# ── Project info ───────────────────────────────────────────────────────────

def _render_project_info():
    st.markdown(
        """
        <div style='font-size:0.75rem; color:#7f8c8d; line-height:1.6'>
        <b>ARPOL × ESADE</b><br>
        Challenge 4 — Production &amp; Laser-Cutting Investment
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Assumption controls ────────────────────────────────────────────────────

def _render_assumption_controls(defaults: dict) -> dict:
    overrides = {}

    st.markdown(f"### {t('assumptions_controls')}")

    # ── Current State ──────────────────────────────────────────────────
    with st.expander(t("current_state_label"), expanded=True):
        overrides["subcontract_annual_spend"] = st.slider(
            t("subcontract_spend") + " (€/yr) ⚠️",
            min_value=60_000,
            max_value=250_000,
            value=int(defaults["subcontract_annual_spend"]),
            step=5_000,
            help="⚠️ PLACEHOLDER — validate with Manuel. Range: €60K–€250K",
        )
        overrides["press_annual_opex"] = st.slider(
            "Press OpEx (€/yr) ⚠️",
            min_value=30_000,
            max_value=150_000,
            value=int(defaults["press_annual_opex"]),
            step=5_000,
            help="⚠️ PLACEHOLDER — press labour + energy + maintenance",
        )

    # ── Volume ─────────────────────────────────────────────────────────
    with st.expander(t("volume_label"), expanded=False):
        vol_pct = st.slider(
            t("volume_growth") + " (%/yr)",
            min_value=3,
            max_value=30,
            value=int(defaults["volume_growth_rate"] * 100),
            step=1,
            help="Base case 15% → doubling by 2028. Low: 8%. High: 20%.",
        )
        overrides["volume_growth_rate"] = vol_pct / 100.0

    # ── EU CAPEX ────────────────────────────────────────────────────────
    with st.expander(t("eu_capex_label"), expanded=False):
        overrides["eu_equipment_cost"] = st.slider(
            t("eu_equipment_cost") + " (€)",
            min_value=100_000,
            max_value=380_000,
            value=int(defaults["eu_equipment_cost"]),
            step=5_000,
            help="Bystronic 6kW with 15% SME discount: €145K–€221K. Trumpf 6kW: €157K–€230K.",
        )
        eu_maint_pct = st.slider(
            t("eu_maintenance") + " (%)",
            min_value=5,
            max_value=10,
            value=int(defaults["eu_maintenance_pct"] * 100),
            step=1,
            help="EU benchmark: 5–10% of CAPEX/yr (mid 7%)",
        )
        overrides["eu_maintenance_pct"] = eu_maint_pct / 100.0

    # ── China CAPEX ─────────────────────────────────────────────────────
    with st.expander(t("china_capex_label"), expanded=False):
        overrides["china_equipment_cost"] = st.slider(
            t("china_equipment_cost") + " (€ ex-works)",
            min_value=15_000,
            max_value=95_000,
            value=int(defaults["china_equipment_cost"]),
            step=2_500,
            help="Bodor P3015E 6kW: €30K–€55K. +4.5% MFN duty + €3.5K freight applied automatically.",
        )
        duty_pct = st.select_slider(
            t("china_duty") + " (%)",
            options=[4.5, 8, 15, 25],
            value=round(defaults["china_duty_pct"] * 100, 1),
            help="Base: 4.5% MFN (EU Access2Markets HS 8456.11.90, verified May 2026). Sensitivity: 8%, 15%, 25% (worst-case trade scenario).",
        )
        overrides["china_duty_pct"] = duty_pct / 100.0

        cn_maint_pct = st.slider(
            t("china_maintenance") + " (%)",
            min_value=3,
            max_value=8,
            value=int(defaults["china_maintenance_pct"] * 100),
            step=1,
            help="China benchmark: 3–8% of CAPEX/yr (mid 5%). Note: parts lead time 4–12 weeks ex-China.",
        )
        overrides["china_maintenance_pct"] = cn_maint_pct / 100.0

    # ── Machine Scale ────────────────────────────────────────────────────
    with st.expander("⚙️ " + t("num_machines"), expanded=True):
        st.caption("Base case: 1 machine covers current volumes + 2-shift upside." if get_lang() == "en" else
                   "Caso base: 1 máquina cubre volúmenes actuales + capacidad de 2 turnos.")
        overrides["num_machines"] = st.select_slider(
            t("num_machines"),
            options=[1, 2, 3],
            value=int(defaults.get("num_machines", 1)),
            help="Each additional machine multiplies CAPEX and OpEx. Use to test high-volume growth scenarios.",
        )

    # ── Operations ──────────────────────────────────────────────────────
    with st.expander(t("operations_label"), expanded=False):
        overrides["num_operators"] = st.select_slider(
            t("operators"),
            options=[1, 2, 3],
            value=int(defaults["num_operators"]),
            help="1 = standard 1-shift. 2 = 2-shift or second operator. Each adds €35K/yr.",
        )
        overrides["annual_hours"] = st.slider(
            t("annual_hours"),
            min_value=900,
            max_value=3_500,
            value=int(defaults["annual_hours"]),
            step=100,
            help="1-shift: ~1,800 hrs. 2-shift: ~3,500 hrs. Affects energy + consumables linearly.",
        )

    # ── Working Capital ─────────────────────────────────────────────────
    with st.expander(t("wc_label"), expanded=False):
        sku_red = st.slider(
            t("sku_reduction") + " (%) ⚠️",
            min_value=40,
            max_value=90,
            value=int(defaults["sku_reduction_rate"] * 100),
            step=5,
            help="⚠️ Hypothesis: 70% of coil SKUs eliminated by switching to sheet. Validate with Manuel.",
        )
        overrides["sku_reduction_rate"] = sku_red / 100.0

        overrides["avg_inventory_per_sku"] = st.slider(
            t("inventory_per_sku") + " (€)",
            min_value=1_000,
            max_value=10_000,
            value=int(defaults["avg_inventory_per_sku"]),
            step=500,
        )

    return overrides
