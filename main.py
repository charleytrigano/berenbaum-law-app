import streamlit as st
from PIL import Image

from backend.dropbox_utils import load_database
from backend.json_validator import validate_and_fix_json
from utils.sidebar import render_sidebar


# ---------------------------------------------------------
# CONFIG PAGE
# ---------------------------------------------------------
st.set_page_config(page_title="Berenbaum Law App", page_icon="📁", layout="wide")

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
render_sidebar()

# ---------------------------------------------------------
# VALIDATION AUTOMATIQUE DU JSON AU DEMARRAGE
# ---------------------------------------------------------
fixed = validate_and_fix_json()
if fixed:
    st.warning("⚠️ La base de données contenait des incohérences et a été automatiquement réparée.")


# ---------------------------------------------------------
# CHARGEMENT BASE DE DONNÉES
# ---------------------------------------------------------
try:
    db = load_database()
    st.success("Base de données chargée depuis Dropbox ✔")
except Exception as e:
    st.error(f"Erreur lors du chargement de Dropbox : {e}")
    db = {"clients": [], "visa": [], "escrow": [], "compta": []}

st.title("📊 Tableau de bord – Berenbaum Law App")
st.write("Bienvenue dans l'application professionnelle de gestion des dossiers.")


# ---------------------------------------------------------
# APERÇU DES DOSSIERS
# ---------------------------------------------------------
clients = db.get("clients", [])

if clients:
    st.subheader("📁 Aperçu des dossiers")
    st.dataframe(clients, use_container_width=True)
else:
    st.info("Aucun dossier trouvé.")
