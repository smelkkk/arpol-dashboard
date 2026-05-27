"""
i18n.py — Bilingual (EN / ES) translation layer for the ARPOL dashboard.

Usage:
    from src.i18n import t, set_lang
    set_lang("es")          # or "en"
    t("payback_period")     # → "Período de recuperación"
"""

import streamlit as st

# ── Language store ─────────────────────────────────────────────────────────
_SUPPORTED = ("en", "es")
_DEFAULT   = "en"


def get_lang() -> str:
    return st.session_state.get("lang", _DEFAULT)


def set_lang(lang: str):
    if lang in _SUPPORTED:
        st.session_state["lang"] = lang


def t(key: str) -> str:
    """Return the translation for `key` in the current language."""
    lang = get_lang()
    trans = _TRANSLATIONS.get(key, {})
    return trans.get(lang, trans.get("en", key))


# ── Translation dictionary ─────────────────────────────────────────────────
_TRANSLATIONS = {

    # ── Navigation ──────────────────────────────────────────────────────────
    "nav_exec_summary"      : {"en": "Executive Summary",           "es": "Resumen Ejecutivo"},
    "nav_scenario"          : {"en": "Scenario Comparison",         "es": "Comparación de Escenarios"},
    "nav_sensitivity"       : {"en": "Sensitivity Analysis",        "es": "Análisis de Sensibilidad"},
    "nav_working_capital"   : {"en": "Working Capital",             "es": "Capital de Trabajo"},
    "nav_assumptions"       : {"en": "Assumptions Register",        "es": "Registro de Supuestos"},

    # ── Page titles ──────────────────────────────────────────────────────────
    "title_exec"            : {"en": "Investment Decision — Executive Summary",
                               "es": "Decisión de Inversión — Resumen Ejecutivo"},
    "title_scenario"        : {"en": "5-Year TCO Scenario Comparison",
                               "es": "Comparación de Escenarios TCO — 5 Años"},
    "title_sensitivity"     : {"en": "Sensitivity & Risk Analysis",
                               "es": "Análisis de Sensibilidad y Riesgo"},
    "title_wc"              : {"en": "Working Capital Release — SKU Rationalisation",
                               "es": "Liberación de Capital de Trabajo — Racionalización de SKU"},
    "title_assumptions"     : {"en": "Assumptions Register",        "es": "Registro de Supuestos"},

    # ── Scenario names ───────────────────────────────────────────────────────
    "scenario_outsource"    : {"en": "Continue Outsourcing",        "es": "Continuar Subcontratación"},
    "scenario_eu"           : {"en": "EU Insource",                 "es": "Insourcing Europa"},
    "scenario_china"        : {"en": "China Insource",              "es": "Insourcing China"},

    # ── KPI labels ──────────────────────────────────────────────────────────
    "payback_period"        : {"en": "Payback Period",              "es": "Período de Recuperación"},
    "payback_eu"            : {"en": "EU Payback",                  "es": "Recuperación UE"},
    "payback_china"         : {"en": "China Payback",               "es": "Recuperación China"},
    "5yr_tco"               : {"en": "5-Year Total Cost",           "es": "Costo Total 5 Años"},
    "5yr_savings_eu"        : {"en": "5-yr Savings vs Outsource (EU)",   "es": "Ahorro 5a vs Subcontrato (UE)"},
    "5yr_savings_china"     : {"en": "5-yr Savings vs Outsource (China)","es": "Ahorro 5a vs Subcontrato (China)"},
    "wc_release"            : {"en": "Working Capital Release",     "es": "Liberación Capital de Trabajo"},
    "roi"                   : {"en": "5-Year ROI",                  "es": "ROI 5 Años"},
    "npv"                   : {"en": "Net Present Value",           "es": "Valor Presente Neto"},
    "breakeven_year"        : {"en": "Break-even Year",             "es": "Año de Equilibrio"},
    "capex_year0"           : {"en": "Year 0 CAPEX",                "es": "CAPEX Año 0"},
    "years"                 : {"en": "years",                       "es": "años"},
    "year"                  : {"en": "Year",                        "es": "Año"},
    "na"                    : {"en": "n/a",                         "es": "n/d"},
    "not_within_5yr"        : {"en": "Beyond Year 5",              "es": "Más de 5 años"},

    # ── Chart axis / labels ─────────────────────────────────────────────────
    "cumulative_cash_flow"  : {"en": "Cumulative Cash Flow (€)",    "es": "Flujo de Caja Acumulado (€)"},
    "annual_cash_flow"      : {"en": "Annual Cash Flow (€)",        "es": "Flujo de Caja Anual (€)"},
    "cumulative_savings"    : {"en": "Cumulative Savings vs Outsourcing (€)",
                               "es": "Ahorro Acumulado vs Subcontrato (€)"},
    "payback_impact"        : {"en": "Impact on EU Payback (years)",  "es": "Impacto en Recuperación UE (años)"},
    "variable"              : {"en": "Variable",                    "es": "Variable"},

    # ── Section headers ──────────────────────────────────────────────────────
    "assumptions_controls"  : {"en": "Model Controls",              "es": "Controles del Modelo"},
    "key_messages"          : {"en": "Key Messages for the Board",  "es": "Mensajes Clave para el Consejo"},
    "capex_breakdown"       : {"en": "CAPEX Breakdown",             "es": "Desglose de CAPEX"},
    "annual_opex"           : {"en": "Annual Operating Costs",      "es": "Costos Operativos Anuales"},
    "sku_impact"            : {"en": "SKU Rationalisation Impact",  "es": "Impacto de la Racionalización de SKU"},
    "risk_flags"            : {"en": "Risk Flags",                  "es": "Alertas de Riesgo"},
    "data_gaps"             : {"en": "Data Gaps — Pending Validation","es": "Brechas de Datos — Pendiente"},
    "tornado_title"         : {"en": "Tornado Chart — Payback Sensitivity",
                               "es": "Gráfico Tornado — Sensibilidad de Recuperación"},
    "heatmap_eu_title"      : {"en": "EU Payback Heatmap (years)",  "es": "Mapa de Calor Recuperación UE (años)"},
    "heatmap_china_title"   : {"en": "China Payback Heatmap (years)","es": "Mapa de Calor Recuperación China (años)"},

    # ── Assumption categories ────────────────────────────────────────────────
    "current_state_label"   : {"en": "Current State (Outsourcing Baseline)",
                               "es": "Estado Actual (Base Subcontrato)"},
    "volume_label"          : {"en": "Volume & Growth",             "es": "Volumen y Crecimiento"},
    "eu_capex_label"        : {"en": "EU CAPEX Inputs",             "es": "Inputs CAPEX Europa"},
    "china_capex_label"     : {"en": "China CAPEX Inputs",          "es": "Inputs CAPEX China"},
    "operations_label"      : {"en": "Operating Parameters",        "es": "Parámetros Operativos"},
    "wc_label"              : {"en": "Working Capital Parameters",  "es": "Parámetros Capital de Trabajo"},
    "financial_label"       : {"en": "Financial Parameters",        "es": "Parámetros Financieros"},

    # ── Status badges ────────────────────────────────────────────────────────
    "status_confirmed"      : {"en": "✅ Confirmed",                 "es": "✅ Confirmado"},
    "status_placeholder"    : {"en": "⚠️ Placeholder",              "es": "⚠️ Estimado"},
    "status_assumed"        : {"en": "📐 Assumed",                   "es": "📐 Supuesto"},
    "status_benchmark"      : {"en": "📊 Benchmark",                 "es": "📊 Benchmark"},

    # ── Key messages ─────────────────────────────────────────────────────────
    "msg1" : {
        "en": "1. Insourcing is structurally favoured over continuing the subcontract in both EU and China scenarios.",
        "es": "1. El insourcing es estructuralmente superior a continuar con el subcontrato en ambos escenarios."
    },
    "msg2" : {
        "en": "2. The coil-to-sheet shift releases ~€112K working capital independently of supplier choice.",
        "es": "2. El cambio de bobina a chapa libera ~€112K de capital de trabajo, independientemente del proveedor."
    },
    "msg3" : {
        "en": "3. EU insource: lower operational risk, longer payback (~Year 3). China insource: faster payback (~Year 2), higher supply-chain risk.",
        "es": "3. Insourcing UE: menor riesgo operativo, mayor período de recuperación (~Año 3). China: recuperación más rápida (~Año 2), mayor riesgo cadena de suministro."
    },
    "msg4" : {
        "en": "4. Payback lies within ARPOL's stated hurdle (validate with Finance).",
        "es": "4. La recuperación está dentro del umbral declarado de ARPOL (validar con Finanzas)."
    },
    "msg5" : {
        "en": "5. ⚠️ Critical: subcontract spend & production volume are still placeholders — validate before Board presentation.",
        "es": "5. ⚠️ Crítico: el gasto en subcontrato y el volumen de producción siguen siendo estimados — validar antes de la presentación al Consejo."
    },

    # ── Language selector ────────────────────────────────────────────────────
    "language"              : {"en": "Language",                    "es": "Idioma"},
    "lang_en"               : {"en": "English",                     "es": "Inglés"},
    "lang_es"               : {"en": "Spanish",                     "es": "Español"},

    # ── Misc UI ──────────────────────────────────────────────────────────────
    "placeholder_warning"   : {
        "en": "Some inputs are placeholders awaiting client data. Results should be treated as directional until confirmed.",
        "es": "Algunos datos son estimados pendientes de información del cliente. Los resultados deben considerarse indicativos hasta su confirmación."
    },
    "subcontract_spend"     : {"en": "Annual Subcontract Spend",    "es": "Gasto Anual en Subcontrato"},
    "volume_growth"         : {"en": "Volume Growth Rate",          "es": "Tasa de Crecimiento de Volumen"},
    "eu_equipment_cost"     : {"en": "EU Equipment Cost",           "es": "Costo Equipo UE"},
    "china_equipment_cost"  : {"en": "China Equipment Cost",        "es": "Costo Equipo China"},
    "china_duty"            : {"en": "China Import Duty",           "es": "Aranceles de Importación China"},
    "operators"             : {"en": "Operators Required",          "es": "Operadores Requeridos"},
    "annual_hours"          : {"en": "Annual Operating Hours",      "es": "Horas Operativas Anuales"},
    "eu_maintenance"        : {"en": "EU Maintenance (% CAPEX/yr)", "es": "Mantenimiento UE (% CAPEX/año)"},
    "china_maintenance"     : {"en": "China Maintenance (% CAPEX/yr)","es": "Mantenimiento China (% CAPEX/año)"},
    "sku_reduction"         : {"en": "SKU Reduction Rate",          "es": "Tasa de Reducción de SKU"},
    "inventory_per_sku"     : {"en": "Avg Inventory per SKU",       "es": "Inventario Promedio por SKU"},
}
