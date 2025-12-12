import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database

# ---------------------------------------------------------
# CONFIG — DOIT ÊTRE EN PREMIER
# ---------------------------------------------------------
st.set_page_config(
    page_title="🏠 Dashboard",
    page_icon="🏠",
    layout="wide"
)

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
render_sidebar()

st.title("🏠 Dashboard — Berenbaum Law App")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = pd.DataFrame(db.get("clients", []))

if clients.empty:
    st.warning("Aucun dossier trouvé.")
    st.stop()

# ---------------------------------------------------------
# SÉCURITÉ : Dossier ID
# ---------------------------------------------------------
if "Dossier ID" not in clients.columns:
    clients["Dossier ID"] = clients["Dossier N"].astype(str)
    db["clients"] = clients.to_dict(orient="records")
    save_database(db)

clients["Dossier ID"] = clients["Dossier ID"].astype(str)

# ---------------------------------------------------------
# NORMALISATION BOOL
# ---------------------------------------------------------
def to_bool(v):
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in ["true", "1", "yes", "oui"]

for col in [
    "Dossier envoye",
    "Dossier accepte",
    "Dossier refuse",
    "Dossier Annule",
    "RFE",
    "Escrow",
]:
    if col not in clients.columns:
        clients[col] = False
    clients[col] = clients[col].apply(to_bool)

# ---------------------------------------------------------
# KPI — CALCUL CORRECT
# ---------------------------------------------------------
total = clients["Dossier ID"].nunique()
envoyes = clients[clients["Dossier envoye"]]["Dossier ID"].nunique()
acceptes = clients[clients["Dossier accepte"]]["Dossier ID"].nunique()
refuses = clients[clients["Dossier refuse"]]["Dossier ID"].nunique()
escrow = clients[clients["Escrow"]]["Dossier ID"].nunique()

# ---------------------------------------------------------
# AFFICHAGE KPI (ILS SONT LÀ)
# ---------------------------------------------------------
st.subheader("📊 Indicateurs clés")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("📁 Total dossiers", total)
c2.metric("📤 Envoyés", envoyes)
c3.metric("✅ Acceptés", acceptes)
c4.metric("❌ Refusés", refuses)
c5.metric("💼 En Escrow", escrow)

# ---------------------------------------------------------
# TABLEAU
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
