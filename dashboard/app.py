from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date

import pandas as pd
import streamlit as st

from energy_management.cli import run_scenarios
from energy_management.data_sources import load_inputs_from_csv

# ── Configuration de la page ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Énergétique",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS personnalisé ──────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    [data-testid="stMetricValue"] { font-size: 1.4rem; }
    .metric-card { background: #1e1e2e; border-radius: 12px; padding: 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar : paramètres ──────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚡ Énergie Intelligente")
    st.divider()

    st.subheader("🎛️ Paramètres de simulation")
    sim_date = st.date_input("Date de simulation", value=date(2026, 3, 24))
    seed = st.number_input("Graine aléatoire (seed)", min_value=0, max_value=9999, value=42, step=1)
    max_shift = st.slider("Déplacement flexible max", 0.0, 1.0, 0.45, 0.05,
                          help="Part max de la charge flexible déplaçable vers les créneaux solaires")

    st.divider()
    st.subheader("📁 Données personnalisées (optionnel)")
    uploaded = st.file_uploader(
        "Importer un CSV (timestamp, base_load_kwh, flexible_load_kwh, solar_kwh)",
        type="csv",
    )

    st.divider()
    run_btn = st.button("▶ Lancer la simulation", type="primary", use_container_width=True)

    st.caption("Les données synthétiques sont générées automatiquement si aucun CSV n'est importé.")

# ── Navigation ────────────────────────────────────────────────────────────────
st.sidebar.divider()
menu = st.sidebar.radio(
    "Navigation",
    ["🏠 Vue d'ensemble", "📡 Capteurs (Virtuels)", "📊 Indicateurs KPI", "⚙️ Optimisation"],
)

# ── Calcul des données ────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Simulation en cours…")
def compute(sim_date: date, seed: int, max_shift: float, csv_bytes: bytes | None):
    custom_inputs = None
    if csv_bytes:
        import io
        import tempfile, os
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            tmp.write(csv_bytes)
            tmp_path = tmp.name
        custom_inputs = load_inputs_from_csv(tmp_path)
        os.unlink(tmp_path)

    result = run_scenarios(
        simulation_date=sim_date,
        seed=seed,
        max_relative_shift=max_shift,
        inputs=custom_inputs,
        include_inputs=True,
    )
    return result


csv_bytes = uploaded.read() if uploaded else None

# Lancer automatiquement au chargement, ou sur clic bouton
if "result" not in st.session_state or run_btn:
    st.session_state["result"] = compute(sim_date, seed, max_shift, csv_bytes)

result = st.session_state["result"]

# ── Préparer les DataFrames ───────────────────────────────────────────────────
baseline_inputs = result["baseline_inputs"]
optimized_inputs = result["optimized_inputs"]
kpis_b = result["kpis"]["baseline"]
kpis_o = result["kpis"]["optimized"]

def inputs_to_df(inputs) -> pd.DataFrame:
    return pd.DataFrame([
        {
            "Heure": inp.timestamp.strftime("%H:%M"),
            "Charge base (kWh)": inp.base_load_kwh,
            "Charge flexible (kWh)": inp.flexible_load_kwh,
            "Solaire (kWh)": inp.solar_kwh,
            "Charge totale (kWh)": round(inp.base_load_kwh + inp.flexible_load_kwh, 4),
        }
        for inp in inputs
    ]).set_index("Heure")

df_base = inputs_to_df(baseline_inputs)
df_opt  = inputs_to_df(optimized_inputs)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE : Vue d'ensemble
# ══════════════════════════════════════════════════════════════════════════════
if menu == "🏠 Vue d'ensemble":
    st.title("🏠 Vue d'ensemble")
    st.markdown(f"**Simulation du {sim_date.strftime('%d/%m/%Y')}** · Seed `{seed}` · Déplacement flexible max `{max_shift:.0%}`")
    st.divider()

    # KPIs principaux — 4 colonnes
    col1, col2, col3, col4 = st.columns(4)

    def delta_str(val_b, val_o, unit="", invert=False):
        diff = val_o - val_b
        arrow = "▼" if diff < 0 else "▲"
        color = "green" if (diff < 0) != invert else "red"
        return f"<span style='color:{color}'>{arrow} {abs(diff):.3f} {unit}</span>"

    with col1:
        st.metric("Import réseau", f"{kpis_o['grid_import_kwh']:.3f} kWh",
                  delta=f"{kpis_o['grid_import_kwh'] - kpis_b['grid_import_kwh']:.3f} kWh vs baseline",
                  delta_color="inverse")
    with col2:
        st.metric("Autonomie", f"{kpis_o['autonomy_rate']*100:.2f}%",
                  delta=f"{(kpis_o['autonomy_rate'] - kpis_b['autonomy_rate'])*100:.2f} pts")
    with col3:
        st.metric("Autoconsommation solaire", f"{kpis_o['self_consumption_rate']*100:.2f}%",
                  delta=f"{(kpis_o['self_consumption_rate'] - kpis_b['self_consumption_rate'])*100:.2f} pts")
    with col4:
        st.metric("Coût net", f"{kpis_o['net_energy_cost_eur']:.3f} €",
                  delta=f"{kpis_o['net_energy_cost_eur'] - kpis_b['net_energy_cost_eur']:.3f} € vs baseline",
                  delta_color="inverse")

    st.divider()

    # Graphique principal : profil journalier
    st.subheader("📈 Profil énergétique journalier (baseline)")
    chart_cols = ["Charge totale (kWh)", "Solaire (kWh)", "Charge flexible (kWh)"]
    st.line_chart(df_base[chart_cols], height=350)

    st.divider()

    # Résumé textuel
    st.subheader("📋 Résumé")
    c1, c2 = st.columns(2)
    with c1:
        st.info(
            f"**Consommation totale :** {kpis_b['total_consumption_kwh']:.2f} kWh\n\n"
            f"**Production solaire :** {kpis_b['total_solar_kwh']:.2f} kWh\n\n"
            f"**Émissions CO₂ :** {kpis_o['grid_co2_kg']:.3f} kg"
        )
    with c2:
        st.success(
            f"L'optimisation réduit l'import réseau de "
            f"**{(kpis_b['grid_import_kwh'] - kpis_o['grid_import_kwh']):.3f} kWh** "
            f"et améliore l'autoconsommation solaire de "
            f"**{(kpis_o['self_consumption_rate'] - kpis_b['self_consumption_rate'])*100:.2f} points**."
        )

# ══════════════════════════════════════════════════════════════════════════════
# PAGE : Capteurs virtuels
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "📡 Capteurs (Virtuels)":
    st.title("📡 Supervision des Capteurs Virtuels")
    st.markdown("Données horaires générées synthétiquement pour la journée simulée.")
    st.divider()

    tab1, tab2, tab3 = st.tabs(["⚡ Consommation", "☀️ Production Solaire", "🔋 Charge Flexible"])

    with tab1:
        st.subheader("Charge de base (non déplaçable)")
        st.line_chart(df_base[["Charge base (kWh)"]], height=300, color=["#f97316"])
        st.caption("Consommation incompressible : éclairage, froid, appareils toujours actifs.")

    with tab2:
        st.subheader("Production solaire photovoltaïque")
        st.line_chart(df_base[["Solaire (kWh)"]], height=300, color=["#facc15"])
        st.caption("Courbe en cloche centrée sur 13h — simulée avec bruit ±8%.")

    with tab3:
        st.subheader("Charge flexible — Baseline vs Optimisé")
        df_flex = pd.DataFrame({
            "Baseline": df_base["Charge flexible (kWh)"],
            "Optimisé": df_opt["Charge flexible (kWh)"],
        })
        st.line_chart(df_flex, height=300)
        st.caption("La charge flexible est décalée vers les créneaux de forte production solaire.")

    st.divider()
    st.subheader("📄 Données brutes (baseline)")
    st.dataframe(df_base, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE : Indicateurs KPI
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "📊 Indicateurs KPI":
    st.title("📊 Indicateurs de Performance Énergétique")
    st.divider()

    kpi_labels = {
        "total_consumption_kwh":  ("Consommation totale", "kWh"),
        "total_solar_kwh":        ("Production solaire",  "kWh"),
        "grid_import_kwh":        ("Import réseau",       "kWh"),
        "grid_export_kwh":        ("Export réseau",       "kWh"),
        "self_consumption_rate":  ("Autoconsommation solaire", "%"),
        "autonomy_rate":          ("Taux d'autonomie",    "%"),
        "peak_grid_import_kwh":   ("Pic import réseau",   "kWh"),
        "load_factor":            ("Facteur de charge",   ""),
        "battery_cycles":         ("Cycles batterie éq.", ""),
        "net_energy_cost_eur":    ("Coût net énergétique","€"),
        "grid_co2_kg":            ("Émissions CO₂ réseau","kg"),
    }

    rows = []
    for key, (label, unit) in kpi_labels.items():
        b = kpis_b[key]
        o = kpis_o[key]
        if unit == "%":
            b_fmt, o_fmt = f"{b*100:.2f}%", f"{o*100:.2f}%"
            diff_fmt = f"{(o-b)*100:+.2f} pts"
        else:
            b_fmt = f"{b:.3f} {unit}".strip()
            o_fmt = f"{o:.3f} {unit}".strip()
            diff_fmt = f"{o-b:+.3f} {unit}".strip()
        rows.append({"Indicateur": label, "Baseline": b_fmt, "Optimisé": o_fmt, "Évolution": diff_fmt})

    df_kpis = pd.DataFrame(rows)
    st.dataframe(df_kpis.set_index("Indicateur"), use_container_width=True)

    st.divider()

    # Graphique barres : import / export / autonomie
    st.subheader("📉 Import / Export réseau — Baseline vs Optimisé")
    df_bar = pd.DataFrame({
        "Import réseau (kWh)": [kpis_b["grid_import_kwh"], kpis_o["grid_import_kwh"]],
        "Export réseau (kWh)": [kpis_b["grid_export_kwh"], kpis_o["grid_export_kwh"]],
    }, index=["Baseline", "Optimisé"])
    st.bar_chart(df_bar, height=300)

    st.divider()
    st.subheader("🌱 Émissions CO₂ & Coût net")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("CO₂ baseline", f"{kpis_b['grid_co2_kg']:.3f} kg",
                  delta=f"{kpis_o['grid_co2_kg'] - kpis_b['grid_co2_kg']:.3f} kg (optimisé)",
                  delta_color="inverse")
    with c2:
        st.metric("Coût net baseline", f"{kpis_b['net_energy_cost_eur']:.3f} €",
                  delta=f"{kpis_o['net_energy_cost_eur'] - kpis_b['net_energy_cost_eur']:.3f} € (optimisé)",
                  delta_color="inverse")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE : Optimisation
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "⚙️ Optimisation":
    st.title("⚙️ Stratégie d'Optimisation")
    st.markdown(
        "L'optimisation **décale la charge flexible** vers les créneaux de forte production solaire "
        "afin de maximiser l'autoconsommation et réduire la dépendance au réseau."
    )
    st.divider()

    # Comparaison profils
    st.subheader("🔄 Charge totale — Baseline vs Optimisé")
    df_compare = pd.DataFrame({
        "Baseline (kWh)":  df_base["Charge totale (kWh)"],
        "Optimisé (kWh)":  df_opt["Charge totale (kWh)"],
        "Solaire (kWh)":   df_base["Solaire (kWh)"],
    })
    st.line_chart(df_compare, height=350)
    st.caption("La courbe optimisée se rapproche de la courbe solaire pour maximiser l'autoconsommation.")

    st.divider()
    st.subheader("📊 Gains de l'optimisation")

    gain_import  = kpis_b["grid_import_kwh"]  - kpis_o["grid_import_kwh"]
    gain_autocon = (kpis_o["self_consumption_rate"] - kpis_b["self_consumption_rate"]) * 100
    gain_co2     = kpis_b["grid_co2_kg"]      - kpis_o["grid_co2_kg"]
    gain_cost    = kpis_b["net_energy_cost_eur"] - kpis_o["net_energy_cost_eur"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("↓ Import réseau",          f"{gain_import:.3f} kWh",  delta="économisé", delta_color="normal")
    c2.metric("↑ Autoconsommation",       f"+{gain_autocon:.2f} pts", delta="amélioré",  delta_color="normal")
    c3.metric("↓ Émissions CO₂",          f"{gain_co2:.3f} kg",      delta="évité",     delta_color="normal")
    c4.metric("Δ Coût net",               f"{gain_cost:.3f} €",      delta="vs baseline", delta_color="normal")

    st.divider()
    st.subheader("📄 Déplacement de charge flexible (détail horaire)")
    df_shift = pd.DataFrame({
        "Heure":    [inp.timestamp.strftime("%H:%M") for inp in baseline_inputs],
        "Baseline": [inp.flexible_load_kwh for inp in baseline_inputs],
        "Optimisé": [inp.flexible_load_kwh for inp in optimized_inputs],
        "Δ":        [round(o.flexible_load_kwh - b.flexible_load_kwh, 4)
                     for b, o in zip(baseline_inputs, optimized_inputs)],
    }).set_index("Heure")
    st.dataframe(df_shift, use_container_width=True)

    st.divider()
    # Export JSON
    st.subheader("⬇️ Exporter les résultats")
    export_data = {"baseline": kpis_b, "optimized": kpis_o}
    st.download_button(
        label="📥 Télécharger les KPIs (JSON)",
        data=json.dumps(export_data, indent=2, ensure_ascii=False),
        file_name=f"kpis_{sim_date.isoformat()}.json",
        mime="application/json",
    )
