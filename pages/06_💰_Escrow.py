import streamlit as st
import pandas as pd
from datetime import datetime

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database
from utils.status_utils import normalize_bool

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="💰 Escrow", page_icon="💰", layout="wide")
render_sidebar()
st.title("💰 Gestion des Escrows")

# ---------------------------------------------------------
# CHARGEMENT BASE
# ---------------------------------------------------------
db = load_database()
clients = pd.DataFrame(db.get("clients", []))

if clients.empty:
    st.info("Aucun dossier trouvé.")
    st.stop()

# Sécurisation booléens
for col in ["Escrow", "Escrow_a_reclamer", "Escrow_reclame"]:
    if col not in clients.columns:
        clients[col] = False
    clients[col] = clients[col].apply(normalize_bool)

clients["Acompte 1"] = pd.to_numeric(clients.get("Acompte 1", 0), errors="coerce").fillna(0)

# ---------------------------------------------------------
# FILTRES
# ---------------------------------------------------------
st.subheader("🎯 Filtres Escrow")

colF1, colF2 = st.columns(2)

etat = colF1.selectbox(
    "État de l'Escrow",
    ["Escrow actif", "Escrow à réclamer", "Escrow réclamé"]
)

# ---------------------------------------------------------
# FILTRAGE LOGIQUE
# ---------------------------------------------------------
if etat == "Escrow actif":
    df = clients[(clients["Escrow"] == True)]

elif etat == "Escrow à réclamer":
    df = clients[(clients["Escrow_a_reclamer"] == True)]

else:
    df = clients[(clients["Escrow_reclame"] == True)]

# ---------------------------------------------------------
# KPI
# ---------------------------------------------------------
total_montant = df["Acompte 1"].sum()
nb_dossiers = len(df)

k1, k2 = st.columns(2)
k1.metric("📁 Dossiers", nb_dossiers)
k2.metric("💰 Montant Escrow", f"${total_montant:,.2f}")

# ---------------------------------------------------------
# TABLEAU
# ---------------------------------------------------------
st.subheader("📋 Dossiers en Escrow")

if df.empty:
    st.info("Aucun dossier pour cet état.")
    st.stop()

cols = [
    "Dossier N",
    "Nom",
    "Visa",
    "Acompte 1",
]

st.dataframe(df[cols], use_container_width=True)

# ---------------------------------------------------------
# ACTIONS
# ---------------------------------------------------------
st.subheader("⚙️ Actions")

for idx, row in df.iterrows():

    st.markdown(f"### 📄 Dossier {row['Dossier N']} — {row['Nom']}")

    colA, colB = st.columns(2)

    # --- Escrow actif → à réclamer
    if etat == "Escrow actif":
        if colA.button(
            "➡️ Passer à Escrow à réclamer",
            key=f"to_reclamer_{idx}"
        ):
            clients.loc[idx, "Escrow"] = False
            clients.loc[idx, "Escrow_a_reclamer"] = True
            clients.loc[idx, "Escrow_reclame"] = False

            save_database({"clients": clients.to_dict(orient="records")})
            st.success("Escrow déplacé vers *À réclamer*")
            st.rerun()

    # --- Escrow à réclamer → réclamé
    if etat == "Escrow à réclamer":
        if colB.button(
            "✅ Marquer comme réclamé",
            key=f"to_reclame_{idx}"
        ):
            clients.loc[idx, "Escrow"] = False
            clients.loc[idx, "Escrow_a_reclamer"] = False
            clients.loc[idx, "Escrow_reclame"] = True
            clients.loc[idx, "Date reclamation"] = str(datetime.today().date())

            save_database({"clients": clients.to_dict(orient="records")})
            st.success("Escrow marqué comme *Réclamé*")
            st.rerun()

# ---------------------------------------------------------
# FIN
# ---------------------------------------------------------
st.markdown("---")
st.markdown("✔ Gestion Escrow fiable — Acompte 1 uniquement")