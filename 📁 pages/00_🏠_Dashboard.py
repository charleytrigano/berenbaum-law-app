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
