import streamlit as st
import os
from PIL import Image
from backend.dropbox_utils import load_database, save_database

import os
st.write("📁 Fichiers trouvés dans le dossier courant :", os.listdir())
st.write("📁 Fichiers trouvés dans /mount/src :", os.listdir("/mount/src"))
st.write("📁 Fichiers trouvés dans /mount/src/berenbaum-law-app/assets :", 
         os.listdir("/mount/src/berenbaum-law-app/assets"))


# ---------------------------------------------------------
# 🖼️ LOGO DANS LE SIDEBAR (chemin ABSOLU — fonctionne toujours)
# ---------------------------------------------------------
with st.sidebar:
    try:
        current_dir = os.path.dirname(__file__)              # dossier courant
        logo_path = os.path.join(current_dir, "assets", "logo.png")

        logo = Image.open(logo_path)
        st.image(logo, width=140)

    except Exception as e:
        st.warning(f"⚠️ Logo non trouvé : {e}")

    st.markdown("## ")


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
