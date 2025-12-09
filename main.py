import streamlit as st
from backend.dropbox_utils import load_database, save_database

import streamlit as st
from backend.dropbox_utils import load_database
import json

import streamlit as st
from PIL import Image

# --- LOGO DANS LE SIDEBAR ---
with st.sidebar:
    try:
        logo = Image.open("assets/logo.png")
        st.image(logo, width=120)
    except Exception as e:
        st.write("⚠️ Logo non trouvé :", e)

    st.markdown("## ")


db = load_database()
st.write("📁 JSON utilisé :", st.secrets["paths"]["DROPBOX_JSON"])
st.write("📄 Contenu DB chargé :", db)


st.set_page_config(page_title="Berenbaum Law App", page_icon="📁", layout="wide")

st.title("📊 Tableau de bord – Berenbaum Law App")
st.write("Bienvenue dans l'application professionnelle de gestion des dossiers.")

# Charger la base depuis Dropbox
try:
    db = load_database()
    st.success("Base de données chargée depuis Dropbox ✔")
except Exception as e:
    st.error(f"Erreur lors du chargement de Dropbox : {e}")
    db = {"clients": [], "visa": [], "escrow": [], "compta": []}

# Aperçu tableau de bord
st.subheader("Aperçu des dossiers")

if "clients" in db and len(db["clients"]) > 0:
    st.dataframe(db["clients"], use_container_width=True)
else:
    st.info("Aucun dossier trouvé.")
