import streamlit as st
from backend.dropbox_utils import load_database, save_database

from utils.config import FILE_ID, SHEET_CLIENTS, SHEET_ESCROW, SHEET_VISA, SHEET_COMPTA

st.title("⚙️ Paramètres de l'application")

st.subheader("📌 Informations système")
st.write(f"**ID du fichier Google Sheets :** `{FILE_ID}`")

st.markdown("---")

# -----------------------------------------------------
# TEST DE CONNEXION À GOOGLE SHEETS
# -----------------------------------------------------
st.subheader("🔗 Test de connexion Google Sheets")

try:
    test_df = load_sheet(SHEET_CLIENTS)
    st.success("Connexion Google Sheets opérationnelle ✔")
except Exception as e:
    st.error(f"Échec de la connexion : {e}")

st.markdown("---")


# -----------------------------------------------------
# LISTE DES ONGLET DISPONIBLES
# -----------------------------------------------------
st.subheader("📄 Onglets nécessaires")
st.write("- Clients ↦ ✔" if test_df is not None else "❌")
st.write("- Escrow")
st.write("- Visa")
st.write("- Comptabilité")

st.markdown("---")


# -----------------------------------------------------
# RÉGLAGES APP (FUTUR)
# -----------------------------------------------------
st.subheader("🔧 Réglages (prochaines versions)")

st.info("""
📌 Fonctionnalités prévues :
- Gestion de

