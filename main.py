import streamlit as st
from PIL import Image
from backend.dropbox_utils import load_database

# ---------------------------------------------------------
# 🔧 CONFIGURATION INITIALE
# ---------------------------------------------------------
st.set_page_config(
    page_title="Berenbaum Law App",
    page_icon="📁",
    layout="wide"
)

# ---------------------------------------------------------
# 🎨 LOGO DANS LE SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### ")

    try:
        logo = Image.open("assets/logo.png")
        st.image(logo, width=140)
    except Exception as e:
        st.error(f"⚠️ Logo non trouvé : {e}")

    st.markdown("---")
    st.markdown("### 🧭 Navigation")
    st.write("Utilisez le menu à gauche pour naviguer dans l’application.")
    st.markdown("---")


# ---------------------------------------------------------
# 📦 CHARGEMENT BASE DROPBOX
# ---------------------------------------------------------
try:
    db = load_database()
    st.success("Base de données chargée depuis Dropbox ✔")
except Exception as e:
    st.error(f"❌ Erreur chargement Dropbox : {e}")
    db = {"clients": [], "visa": [], "escrow": [], "compta": []}

# Debug affichage JSON utilisé
st.caption(f"JSON utilisé : `{st.secrets['paths']['DROPBOX_JSON']}`")

# ---------------------------------------------------------
# 🏠 PAGE D'ACCUEIL
# ---------------------------------------------------------
st.title("📊 Tableau de bord — Berenbaum Law App")
st.write("Bienvenue dans l’application professionnelle de gestion des dossiers.")

# Aperçu rapide des dossiers
clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier trouvé.")
else:
    st.subheader("📁 Aperçu des dossiers")
    st.dataframe(clients, width="stretch")


# ---------------------------------------------------------
# 🛈 Notes / Footer
# ---------------------------------------------------------
st.markdown("---")
st.caption("© 2025 — Berenbaum, P.A. Law Firm — Application interne de gestion des dossiers.")
