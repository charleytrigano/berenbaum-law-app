import streamlit as st
import pandas as pd
from backend.google_sheets import (
    load_sheet,
    load_visa,
    load_escrow,
    load_compta
)
from utils.config import (
    SHEET_CLIENTS,
    SHEET_VISA,
    SHEET_ESCROW,
    SHEET_COMPTA
)
from components.cards import kpi_card
from components.charts import chart_categories, chart_compta

st.set_page_config(page_title="Dashboard", layout="wide")

st.title("🏠 Dashboard Général – Berenbaum Law")

# Chargement des données
clients = load_sheet(SHEET_CLIENTS)
visa = load_visa()
escrow = load_escrow()
compta = load_compta()

# -----------------------
# KPIs 
# -----------------------
st.subheader("📌 Indicateurs Clés")

col1, col2, col3, col4 = st.columns(4)
kpi_card("Total Dossiers", len(clients), "#1976D2")
kpi_card("Visas en cours", len(visa), "#FF9800")
kpi_card("Mouvements Escrow", len(escrow), "#9C27B0")

if "Montant" in compta.columns:
    kpi_card("Solde Global", f"{compta['Montant'].sum():,.2f} USD", "#4CAF50")
else:
    kpi_card("Solde Global", "N/A", "#4CAF50")

st.markdown("---")

# -----------------------
# GRAPHIQUES 
# -----------------------

st.subheader("📊 Analyses Graphiques")

colA, colB = st.columns(2)

# Graphique des catégories (clients)
fig_cat = chart_categories(clients)
if fig_cat:
    colA.plotly_chart(fig_cat, use_container_width=True)
else:
    colA.info("Aucune analyse catégorie disponible.")

# Graphique comptabilité
fig_compta = chart_compta(compta)
if fig_compta:
    colB.plotly_chart(fig_compta, use_container_width=True)
else:
    colB.info("Aucune donnée comptable suffisante pour un graphe.")
