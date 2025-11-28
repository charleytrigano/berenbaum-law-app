import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

import plotly.express as px
from datetime import datetime

# ---------------------------------------------------
# PAGE SETUP
# ---------------------------------------------------
st.set_page_config(page_title="Analyses", page_icon="📊", layout="wide")
st.title("📊 Analyses & Statistiques")
st.write("Visualisez les performances globales du cabinet.")

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------
db = load_database()

clients = pd.DataFrame(db.get("clients", []))
visa = pd.DataFrame(db.get("visa", []))
escrow = pd.DataFrame(db.get("escrow", []))

if clients.empty:
    st.info("Aucun dossier client trouvé.")
    st.stop()

# ---------------------------------------------------
# KPI GLOBALS
# ---------------------------------------------------
st.subheader("📌 Indicateurs principaux")

total_dossiers = len(clients)

acceptes = clients["Date acceptation"].astype(str).str.len() > 0
refuses = clients["Date refus"].astype(str).str.len() > 0
annules = clients["Date annulation"].astype(str).str.len() > 0

taux_accept = (acceptes.sum() / total_dossiers) * 100
taux_refus = (refuses.sum() / total_dossiers) * 100
taux_annul = (annules.sum() / total_dossiers) * 100

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total dossiers", total_dossiers)
col2.metric("Acceptés", f"{taux_accept:.1f}%")
col3.metric("Refusés", f"{taux_refus:.1f}%")
col4.metric("Annulés", f"{taux_annul:.1f}%")

st.markdown("---")

# ---------------------------------------------------
# 📊 DOSSIERS PAR CATÉGORIE
# ---------------------------------------------------
st.subheader("📁 Répartition par catégorie")

if "Catégories" in clients.columns:
    fig_cat = px.pie(
        clients,
        names="Catégories",
        title="Répartition des dossiers par catégorie",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    st.plotly_chart(fig_cat, use_container_width=True)
else:
    st.info("Aucune catégorie définie.")

st.markdown("---")

# ---------------------------------------------------
# 🗂️ RÉPARTITION VISA
# ---------------------------------------------------
st.subheader("🛂 Répartition des types de Visa")

if "Visa" in clients.columns:
    fig_visa = px.pie(
        clients,
        names="Visa",
        title="Répartition des dossiers Visa",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig_visa, use_container_width=True)
else:
    st.info("Aucun type de visa trouvé.")

st.markdown("---")

# ---------------------------------------------------
# 📅 DOSSIERS PAR MOIS
# ---------------------------------------------------
st.subheader("📆 Volume de dossiers par mois")

if "Date envoi" in clients.columns:

    df_months = clients.copy()
    df_months["Date envoi"] = pd.to_datetime(df_months["Date envoi"], errors="coerce")
    df_months["Mois"] = df_months["Date envoi"].dt.to_period("M")

    df_count = df_months["Mois"].value_counts().sort_index()

    fig_mois = px.bar(
        df_count,
        title="Nombre de dossiers envoyés par mois",
        labels={'value': 'Nombre de dossiers', 'index': 'Mois'},
        color_discrete_sequence=px.colors.qualitative.Vivid
    )
    st.plotly_chart(fig_mois, use_container_width=True)

else:
    st.info("Aucune date d'envoi trouvée.")

st.markdown("---")

# ---------------------------------------------------
# 💰 ANALYSE ESCROW
# ---------------------------------------------------
st.subheader("💰 Mouvements Escrow")

if not escrow.empty:

    escrow["Montant"] = pd.to_numeric(escrow["Montant"], errors="coerce").fillna(0)
    total_escrow = escrow["Montant"].sum()

    colA, colB = st.columns(2)
    colA.metric("Total Escrow enregistré", f"${total_escrow:,.2f}")

    escrow["Date envoi"] = pd.to_datetime(escrow["Date envoi"], errors="coerce")
    escrow["Mois"] = escrow["Date envoi"].dt.to_period("M")

    df_escrow_mois = escrow.groupby("Mois")["Montant"].sum()

    fig_escrow = px.line(
        df_escrow_mois,
        title="Évolution mensuelle des fonds Escrow",
        labels={"value": "Montant", "index": "Mois"},
        markers=True
    )
    st.plotly_chart(fig_escrow, use_container_width=True)

else:
    st.info("Aucun mouvement Escrow enregistré.")
