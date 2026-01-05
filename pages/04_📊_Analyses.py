# pages/04_📊_Analyses.py

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database
from utils.status_utils import normalize_bool

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(
    page_title="📊 Analyses",
    page_icon="📊",
    layout="wide"
)
render_sidebar()
st.title("📊 Analyses & indicateurs avancés")

# =====================================================
# LOAD DATA
# =====================================================
db = load_database()
clients = pd.DataFrame(db.get("clients", []))

if clients.empty:
    st.warning("Aucune donnée disponible.")
    st.stop()

# =====================================================
# NORMALISATION
# =====================================================
clients["Dossier N"] = clients["Dossier N"].astype(str)
clients["Date"] = pd.to_datetime(clients["Date"], errors="coerce")

clients["Total facturé"] = (
    clients.get("Montant honoraires (US $)", 0).fillna(0)
    + clients.get("Autres frais (US $)", 0).fillna(0)
)

clients["Total encaissé"] = 0.0
for i in range(1, 5):
    col = f"Acompte {i}"
    if col in clients.columns:
        clients["Total encaissé"] += clients[col].fillna(0)

clients["Solde"] = clients["Total facturé"] - clients["Total encaissé"]

# =====================================================
# FILTRES
# =====================================================
st.subheader("🎛️ Filtres")

c1, c2, c3, c4, c5 = st.columns(5)

# Année
years = sorted(clients["Date"].dropna().dt.year.unique())
selected_years = c1.multiselect("Année", years, default=years)

# Catégorie
categories = sorted(clients["Categories"].dropna().unique())
cat = c2.multiselect("Catégorie", categories, default=categories)

# Sous-catégorie
souscats = sorted(clients["Sous-categories"].dropna().unique())
souscat = c3.multiselect("Sous-catégorie", souscats, default=souscats)

# Visa
visas = sorted(clients["Visa"].dropna().unique())
visa = c4.multiselect("Visa", visas, default=visas)

# Statuts
statut = c5.multiselect(
    "Statut",
    [
        "Dossier envoye",
        "Dossier accepte",
        "Dossier refuse",
        "Dossier Annule",
        "RFE"
    ],
    default=[]
)

df = clients.copy()

if selected_years:
    df = df[df["Date"].dt.year.isin(selected_years)]

df = df[
    df["Categories"].isin(cat)
    & df["Sous-categories"].isin(souscat)
    & df["Visa"].isin(visa)
]

# Filtre statuts
for s in statut:
    df = df[df[s].apply(normalize_bool)]

# =====================================================
# FILTRES FINANCIERS
# =====================================================
st.markdown("### 💰 Filtres financiers")

f1, f2, f3 = st.columns(3)

show_soldes = f1.checkbox("Dossiers soldés (solde = 0)", False)
show_non_soldes = f2.checkbox("Dossiers non soldés (solde ≠ 0)", False)
show_negative = f3.checkbox("Solde négatif", False)

if show_soldes:
    df = df[df["Solde"] == 0]

if show_non_soldes:
    df = df[df["Solde"] != 0]

if show_negative:
    df = df[df["Solde"] < 0]

# =====================================================
# KPI
# =====================================================
st.markdown("---")
st.subheader("📌 Indicateurs clés")

k1, k2, k3, k4, k5, k6, k7 = st.columns(7)

k1.metric("Dossiers", len(df))
k2.metric("Acceptés", df["Dossier accepte"].apply(normalize_bool).sum())
k3.metric("Refusés", df["Dossier refuse"].apply(normalize_bool).sum())
k4.metric("Annulés", df["Dossier Annule"].apply(normalize_bool).sum())
k5.metric("Total facturé", f"${df['Total facturé'].sum():,.2f}")
k6.metric("Total encaissé", f"${df['Total encaissé'].sum():,.2f}")
k7.metric("Solde total", f"${df['Solde'].sum():,.2f}")

# =====================================================
# GRAPHIQUE 1 — ÉVOLUTION MENSUELLE
# =====================================================
st.markdown("---")
st.subheader("📈 Évolution mensuelle (facturé / encaissé)")

monthly = (
    df.dropna(subset=["Date"])
    .assign(Mois=lambda x: x["Date"].dt.to_period("M").astype(str))
    .groupby("Mois")[["Total facturé", "Total encaissé"]]
    .sum()
    .reset_index()
)

if not monthly.empty:
    fig = px.line(
        monthly,
        x="Mois",
        y=["Total facturé", "Total encaissé"],
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Aucune donnée mensuelle disponible.")

# =====================================================
# GRAPHIQUE 2 — MULTI-ANNÉES (RÉTABLI)
# =====================================================
st.markdown("---")
st.subheader("📊 Comparaison multi-années")

yearly = (
    df.dropna(subset=["Date"])
    .assign(Année=lambda x: x["Date"].dt.year)
    .groupby("Année")[["Total facturé", "Total encaissé"]]
    .sum()
    .reset_index()
)

if not yearly.empty:
    fig2 = px.bar(
        yearly,
        x="Année",
        y=["Total facturé", "Total encaissé"],
        barmode="group"
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Pas assez de données pour la comparaison annuelle.")

# =====================================================
# GRAPHIQUE 3 — RÉPARTITION PAR VISA
# =====================================================
st.markdown("---")
st.subheader("🛂 Répartition des honoraires par Visa")

visa_stats = (
    df.groupby("Visa")["Total facturé"]
    .sum()
    .reset_index()
    .sort_values("Total facturé", ascending=False)
)

if not visa_stats.empty:
    fig3 = px.pie(
        visa_stats,
        names="Visa",
        values="Total facturé",
        hole=0.4
    )
    st.plotly_chart(fig3, use_container_width=True)

# =====================================================
# TABLEAU DÉTAILLÉ
# =====================================================
st.markdown("---")
st.subheader("📋 Détails des dossiers analysés")

cols = [
    "Dossier N", "Nom", "Date", "Categories", "Sous-categories", "Visa",
    "Total facturé", "Total encaissé", "Solde",
    "Dossier envoye", "Dossier accepte", "Dossier refuse", "Dossier Annule", "RFE"
]

st.dataframe(
    df[cols].sort_values("Date", ascending=False),
    use_container_width=True
)