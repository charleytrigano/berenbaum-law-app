import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database
from components.kpi_cards import kpi_card
from components.analysis_charts import (
    monthly_hist,
    multi_year_line,
    category_donut,
    heatmap_month,
    category_bars,
)

# ---------------------------------------------------------
# CONFIG PAGE
# ---------------------------------------------------------
st.set_page_config(page_title="📊 Analyses", page_icon="📊", layout="wide")
render_sidebar()
st.title("📊 Analyses & Statistiques")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = pd.DataFrame(db.get("clients", []))

if clients.empty:
    st.warning("Aucun dossier disponible.")
    st.stop()

# ---------------------------------------------------------
# NORMALISATION DE BASE
# ---------------------------------------------------------
clients["Dossier N"] = clients["Dossier N"].astype(str)

clients["Date"] = pd.to_datetime(clients["Date"], errors="coerce")
clients["Année"] = clients["Date"].dt.year
clients["Mois"] = clients["Date"].dt.to_period("M").astype(str)

# Montants
for col in [
    "Montant honoraires (US $)",
    "Autres frais (US $)",
    "Acompte 1",
    "Acompte 2",
    "Acompte 3",
    "Acompte 4",
]:
    if col not in clients.columns:
        clients[col] = 0.0
    clients[col] = pd.to_numeric(clients[col], errors="coerce").fillna(0.0)

# Booléens
for col in [
    "Dossier envoye",
    "Dossier accepte",
    "Dossier refuse",
    "Dossier Annule",
    "RFE",
    "Escrow",
    "Escrow_a_reclamer",
    "Escrow_reclame",
]:
    if col not in clients.columns:
        clients[col] = False
    clients[col] = clients[col].astype(bool)

# ---------------------------------------------------------
# FILTRES
# ---------------------------------------------------------
st.subheader("🎛️ Filtres")

colF1, colF2, colF3, colF4 = st.columns(4)

# Année
years = sorted(clients["Année"].dropna().unique().tolist())
selected_years = colF1.multiselect(
    "Année",
    years,
    default=years,
)

# Catégorie
categories = ["Toutes"] + sorted(
    clients["Categories"].dropna().unique().tolist()
)
cat = colF2.selectbox("Catégorie", categories)

# Sous-catégorie
if cat != "Toutes":
    souscats = ["Toutes"] + sorted(
        clients[clients["Categories"] == cat]["Sous-categories"]
        .dropna()
        .unique()
        .tolist()
    )
else:
    souscats = ["Toutes"] + sorted(
        clients["Sous-categories"].dropna().unique().tolist()
    )

souscat = colF3.selectbox("Sous-catégorie", souscats)

# Visa
if souscat != "Toutes":
    visas = ["Tous"] + sorted(
        clients[clients["Sous-categories"] == souscat]["Visa"]
        .dropna()
        .unique()
        .tolist()
    )
else:
    visas = ["Tous"] + sorted(clients["Visa"].dropna().unique().tolist())

visa = colF4.selectbox("Visa", visas)

# ---------------------------------------------------------
# APPLICATION DES FILTRES
# ---------------------------------------------------------
df = clients.copy()

if selected_years:
    df = df[df["Année"].isin(selected_years)]

if cat != "Toutes":
    df = df[df["Categories"] == cat]

if souscat != "Toutes":
    df = df[df["Sous-categories"] == souscat]

if visa != "Tous":
    df = df[df["Visa"] == visa]

# ---------------------------------------------------------
# KPI
# ---------------------------------------------------------
st.subheader("📈 Indicateurs clés")

k1, k2, k3, k4 = st.columns(4)
k5, k6 = st.columns(2)

total_facture = (
    df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
).sum()

total_encaisse = df[
    ["Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4"]
].sum().sum()

solde_du = total_facture - total_encaisse

escrow_total = df[df["Escrow"] == True]["Acompte 1"].sum()

with k1:
    kpi_card(
        "Nombre de dossiers",
        len(df),
        "📁",
        "Nombre total de dossiers (principaux + sous-dossiers)"
    )

with k2:
    kpi_card(
        "Honoraires",
        f"${df['Montant honoraires (US $)'].sum():,.0f}",
        "💼",
        "Total des honoraires des dossiers filtrés"
    )

with k3:
    kpi_card(
        "Autres frais",
        f"${df['Autres frais (US $)'].sum():,.0f}",
        "🧾",
        "Total des autres frais facturés"
    )

with k4:
    kpi_card(
        "Total facturé",
        f"${total_facture:,.0f}",
        "🧮",
        "Honoraires + autres frais"
    )

with k5:
    kpi_card(
        "Total encaissé",
        f"${total_encaisse:,.0f}",
        "🏦",
        "Somme de tous les acomptes encaissés"
    )

with k6:
    kpi_card(
        "Escrow",
        f"${escrow_total:,.0f}",
        "🔒",
        "Montant actuellement en escrow (Acompte 1 uniquement)"
    )

# ---------------------------------------------------------
# GRAPHIQUES
# ---------------------------------------------------------
st.subheader("📊 Graphiques")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅 Mensuel",
    "📈 Multi-années",
    "🎯 Catégories",
    "🔥 Activité",
    "📊 Revenus",
])

with tab1:
    st.plotly_chart(monthly_hist(df), use_container_width=True)

with tab2:
    st.plotly_chart(multi_year_line(df), use_container_width=True)

with tab3:
    st.plotly_chart(category_donut(df), use_container_width=True)

with tab4:
    st.plotly_chart(heatmap_month(df), use_container_width=True)

with tab5:
    st.plotly_chart(category_bars(df), use_container_width=True)

# ---------------------------------------------------------
# TABLEAU DÉTAIL
# ---------------------------------------------------------
st.subheader("📋 Dossiers filtrés")

cols_display = [
    "Dossier N",
    "Nom",
    "Date",
    "Categories",
    "Sous-categories",
    "Visa",
    "Montant honoraires (US $)",
    "Autres frais (US $)",
    "Acompte 1",
    "Acompte 2",
    "Acompte 3",
    "Acompte 4",
    "Escrow",
]

st.dataframe(
    df[cols_display].sort_values("Dossier N"),
    use_container_width=True,
    height=420,
)