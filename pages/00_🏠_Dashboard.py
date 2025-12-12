import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="🏠 Dashboard", page_icon="🏠", layout="wide")
render_sidebar()
st.title("🏠 Dashboard — Berenbaum Law App")

# ---------------------------------------------------------
# CHARGEMENT BASE
# ---------------------------------------------------------
db = load_database()
clients = pd.DataFrame(db.get("clients", []))

if clients.empty:
    st.warning("Aucun dossier trouvé.")
    st.stop()

# ---------------------------------------------------------
# GARANTIE STRUCTURE
# ---------------------------------------------------------
clients["Dossier ID"] = clients["Dossier ID"].astype(str)
clients["Dossier N"] = clients["Dossier N"].astype(str)

# Normalisation bool
def to_bool(v):
    if isinstance(v, bool):
        return v
    return str(v).lower() in ["true", "1", "yes", "oui"]

for col in [
    "Dossier envoye",
    "Dossier accepte",
    "Dossier refuse",
    "Dossier Annule",
    "RFE",
    "Escrow",
    "Escrow_a_reclamer",
    "Escrow_reclame",
]:
    if col not in clients.columns:
        clients[col] = False
    clients[col] = clients[col].apply(to_bool)

# ---------------------------------------------------------
# KPI (TOUJOURS via Dossier ID)
# ---------------------------------------------------------
total_dossiers = clients["Dossier ID"].nunique()
dossiers_envoyes = clients[clients["Dossier envoye"]]["Dossier ID"].nunique()
dossiers_acceptes = clients[clients["Dossier accepte"]]["Dossier ID"].nunique()
dossiers_refuses = clients[clients["Dossier refuse"]]["Dossier ID"].nunique()
dossiers_escrow = clients[clients["Escrow"]]["Dossier ID"].nunique()

# ---------------------------------------------------------
# AFFICHAGE KPI
# ---------------------------------------------------------
st.subheader("📊 Indicateurs clés")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("📁 Total dossiers", total_dossiers)
c2.metric("📤 Dossiers envoyés", dossiers_envoyes)
c3.metric("✅ Acceptés", dossiers_acceptes)
c4.metric("❌ Refusés", dossiers_refuses)
c5.metric("💼 En Escrow", dossiers_escrow)

# ---------------------------------------------------------
# TABLEAU SYNTHÈSE
# ---------------------------------------------------------
st.subheader("📋 Aperçu des dossiers")

st.dataframe(
    clients[
        [
            "Dossier N",
            "Nom",
            "Categories",
            "Visa",
            "Dossier envoye",
            "Dossier accepte",
            "Dossier refuse",
            "Escrow",
        ]
    ],
    use_container_width=True,
)
