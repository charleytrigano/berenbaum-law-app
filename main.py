import streamlit as st
from utils.sidebar import render_sidebar
render_sidebar()

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
