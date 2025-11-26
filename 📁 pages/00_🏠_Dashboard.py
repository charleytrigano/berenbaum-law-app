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

from components.database import load_database, save_database

db = load_database()

nouveau_client = {"id": 1, "nom": "TRIGANO", "prenom": "Charley"}
db["clients"].append(nouveau_client)
save_database(db)

from components.dropbox_utils import upload_file_to_dropbox

uploaded = st.file_uploader("Ajouter un document")

if uploaded:
    upload_file_to_dropbox(uploaded, f"/berenbaum/documents/{uploaded.name}")
    st.success("Document enregistré !")

import streamlit as st
from components.database import load_database

# ---------------------------------------------------
# CONFIGURATION GÉNÉRALE
# ---------------------------------------------------
st.set_page_config(
    page_title="Berenbaum Law App",
    page_icon="📁",
    layout="wide"
)

# ---------------------------------------------------
# TITRE & HEADER
# ---------------------------------------------------
st.title("📊 Tableau de bord – Berenbaum Law App")
st.write("Bienvenue dans l'application professionnelle de gestion des dossiers.")

# ---------------------------------------------------
# CHARGEMENT DES DONNÉES (Dropbox)
# ---------------------------------------------------
try:
    db = load_database()
    st.success("Base de données chargée depuis Dropbox ✔")
except Exception as e:
    st.error(f"Erreur lors du chargement de la base Dropbox : {e}")
    db = None

# ---------------------------------------------------
# APERÇU DES CLIENTS
# ---------------------------------------------------
if db and "Clients" in db:
    st.subheader("📁 Aperçu des dossiers")
    df_clients = st.dataframe(db["Clients"], use_container_width=True)
else:
    st.warning("Aucun client trouvé dans la base de données.")


