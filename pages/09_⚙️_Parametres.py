import streamlit as st
from backend.dropbox_utils import load_database, save_database

st.set_page_config(page_title="Paramètres", page_icon="⚙️", layout="wide")

st.title("⚙️ Paramètres de l'application")

st.markdown("""
Bienvenue dans la page **Paramètres**.

Ici vous pouvez :
- 🔧 Vérifier l’état des données
- 💾 Sauvegarder / réinitialiser
- 🧪 Voir les informations système
""")

st.markdown("---")

# ---------------------------------------------------------
# CHARGER BASE
# ---------------------------------------------------------
try:
    db = load_database()
    st.success("Base chargée depuis Dropbox ✔")
except:
    st.error("Impossible de charger la base Dropbox.")
    db = {"clients": [], "visa": [], "escrow": [], "compta": []}

# ---------------------------------------------------------
# INFOS SUR LA BASE
# ---------------------------------------------------------
st.subheader("📁 Informations sur la base")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Clients", len(db.get("clients", [])))
col2.metric("Visa", len(db.get("visa", [])))
col3.metric("Escrow", len(db.get("escrow", [])))
col4.metric("Comptabilité", len(db.get("compta", [])))

st.markdown("---")

# ---------------------------------------------------------
# RÉINITIALISATION
# ---------------------------------------------------------
st.subheader("🧨 Réinitialiser la base (danger)")

st.info(
    "Cette option remet la base à zéro. "
    "Toutes les données clients, Visa, Escrow, Comptabilité seront supprimées."
)

if st.button("❌ Réinitialiser totalement la base"):
    save_database({"clients": [], "visa": [], "escrow": [], "compta": []})
    st.success("Base réinitialisée ✔")

st.markdown("---")

# ---------------------------------------------------------
# DEBUG SECRETS (Optionnel)
# ---------------------------------------------------------
st.subheader("🔒 Débogage des secrets")

if st.checkbox("Afficher les secrets (DEBUG)"):
    st.json(st.secrets)

st.markdown("---")

st.success("Page Paramètres chargée correctement ✔")
