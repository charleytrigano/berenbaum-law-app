import streamlit as st
from backend.google_sheets import load_sheet
from utils.config import SHEET_CLIENTS

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
# CHARGEMENT DES DONNÉES (Clients)
# ---------------------------------------------------
try:
    df_clients = load_sheet(SHEET_CLIENTS)
    st.success("Données chargées depuis Google Sheets ✔")
except Exception as e:
    st.error(f"Erreur lors du chargement des données Google Sheets : {e}")
    df_clients = None

# ---------------------------------------------------
# APERÇU DES DONNÉES
# ---------------------------------------------------
if df_clients is not None:
    st.subheader("Aperçu des dossiers")
    st.dataframe(df_clients, use_container_width=True)
else:
    st.warning("Données non disponibles.")
