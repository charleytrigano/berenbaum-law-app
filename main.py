import streamlit as st
from backend.dropbox_utils import load_database, save_database

st.set_page_config(page_title="Berenbaum Law App", page_icon="📁", layout="wide")

st.title("📊 Tableau de bord – Berenbaum Law App")
st.write("Bienvenue dans l'application professionnelle de gestion des dossiers.")

# Charger la base depuis Dropbox
try:
    db = load_database()
    st.success("Base de données chargée depuis Dropbox ✔")
except Exception as e:
    st.error(f"Erreur lors du chargement de Dropbox : {e}")
    db = {"clients": []}

# Aperçu
st.subheader("Aperçu des dossiers")
if "clients" in db and len(db["clients"]) > 0:
    st.dataframe(db["clients"], use_container_width=True)
else:
    st.warning("Aucun client trouvé dans la base de données.")
