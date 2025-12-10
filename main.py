import streamlit as st
from PIL import Image
import os

# IMPORTS BACKEND
from backend.dropbox_utils import load_database, save_database


# ----------------------------------------------------------
# CONFIG APP EN PREMIER (IMPORTANT)
# ----------------------------------------------------------
st.set_page_config(
    page_title="Berenbaum Law App",
    page_icon="📁",
    layout="wide"
)


# ----------------------------------------------------------
# LOGO EN HAUT DU SIDEBAR
# ----------------------------------------------------------
with st.sidebar:
    st.markdown("### ")  # petit espace haute

    candidate_paths = [
        "assets/logo.png",
        "./assets/logo.png",
        "/mount/src/berenbaum-law-app/assets/logo.png",
        "/mount/src/assets/logo.png"
    ]

    logo_loaded = False
    for p in candidate_paths:
        if os.path.exists(p):
            st.image(p, width=140)
            logo_loaded = True
            break

    if not logo_loaded:
        st.error("⚠️ Logo introuvable")
        st.write("Chemin courant :", os.getcwd())

    st.markdown("---")


# ----------------------------------------------------------
# AFFICHAGE DU CONTENU PRINCIPAL
# ----------------------------------------------------------
st.title("📊 Tableau de bord – Berenbaum Law App")
st.write("Bienvenue dans l'application professionnelle de gestion des dossiers.")

# Charger la base depuis Dropbox
try:
    db = load_database()
    st.success("Base de données chargée depuis Dropbox ✔")
except Exception as e:
    st.error(f"Erreur lors du chargement Dropbox : {e}")
    db = {"clients": [], "visa": [], "escrow": [], "compta": []}

# DEBUG (si tu veux)
# st.json(db)
