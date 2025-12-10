import streamlit as st
from PIL import Image
import os

# ----------------------------------------------------------
# CONFIG APP EN PREMIER (sinon le sidebar se réinitialise)
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
    st.markdown("### ")  # petit espace haut

    candidate_paths = [
        "assets/logo.png",
        "./assets/logo.png",
        "/mount/src/berenbaum-law-app/assets/logo.png",
        "/mount/src/assets/logo.png"
    ]

    loaded = False
    for p in candidate_paths:
        if os.path.exists(p):
            st.image(p, width=140)
            loaded = True
            break

    if not loaded:
        st.error("⚠️ Logo introuvable")
        st.write("Chemin courant :", os.getcwd())

    st.markdown("---")  # séparation esthétique



# ---------------------------------------------------------
# 🔧 CONFIGURATION DE LA PAGE
# ---------------------------------------------------------
st.set_page_config(
    page_title="Berenbaum Law App",
    page_icon="📁",
    layout="wide"
)

st.title("📊 Tableau de bord – Berenbaum Law App")
st.write("Bienvenue dans l'application professionnelle de gestion des dossiers.")


# ---------------------------------------------------------
# 🔄 CHARGEMENT BASE DE DONNÉES DROPBOX
# ---------------------------------------------------------
try:
    db = load_database()
    st.success("Base de données chargée depuis Dropbox ✔")
except Exception as e:
    st.error(f"Erreur lors du chargement Dropbox : {e}")
    db = {"clients": [], "visa": [], "escrow": [], "compta": []}


# ---------------------------------------------------------
# 🔍 DEBUG OPTIONNEL : chemins & contenus DB
# ---------------------------------------------------------
with st.expander("📁 JSON utilisé & Contenu brut (Debug)"):
    try:
        st.write("📁 JSON utilisé :", st.secrets["paths"]["DROPBOX_JSON"])
    except:
        st.error("Impossible de lire le chemin JSON dans secrets.toml")

    st.json(db)


# ---------------------------------------------------------
# 🧾 APERÇU DU TABLEAU DE BORD
# ---------------------------------------------------------
st.subheader("📁 Aperçu des dossiers")

if "clients" in db and len(db["clients"]) > 0:
    st.dataframe(db["clients"], height=500, use_container_width=True)
else:
    st.info("Aucun dossier trouvé.")


# ---------------------------------------------------------
# FIN DU FICHIER
# ---------------------------------------------------------
