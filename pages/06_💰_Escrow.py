import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

st.set_page_config(page_title="Escrow", page_icon="💰", layout="wide")
st.title("💰 Gestion des Escrows")

# ---------------------------------------------------------
# LOAD DB
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

df = pd.DataFrame(clients)

def norm(x):
    if isinstance(x, bool):
        return x
    if str(x).lower() in ["true", "1", "yes", "oui"]:
        return True
    return False

df["Escrow"] = df.get("Escrow", False).apply(norm)
df["Escrow_a_reclamer"] = df.get("Escrow_a_reclamer", False).apply(norm)
df["Escrow_reclame"] = df.get("Escrow_reclame", False).apply(norm)
df["Dossier envoye"] = df.get("Dossier envoye", False).apply(norm)

# ---------------------------------------------------------
# TABLE ESCROW EN COURS
# ---------------------------------------------------------
st.subheader("📌 Escrow en cours")
escrow_cours = df[df["Escrow"] == True]

if escrow_cours.empty:
    st.info("Aucun dossier en Escrow en cours.")
else:
    st.dataframe(escrow_cours[[
        "Dossier N", "Nom", "Visa", "Dossier envoye"
    ]], use_container_width=True)

# ---------------------------------------------------------
# TABLE ESCROW A RECLAMER
# ---------------------------------------------------------
st.subheader("📌 Escrow à réclamer")
escrow_reclamer = df[df["Escrow_a_reclamer"] == True]

if escrow_reclamer.empty:
    st.info("Aucun dossier à réclamer.")
else:
    st.dataframe(escrow_reclamer[[
        "Dossier N", "Nom", "Visa", "Dossier envoye"
    ]], use_container_width=True)

# ---------------------------------------------------------
# TABLE ESCROW RECLAME
# ---------------------------------------------------------
st.subheader("📌 Escrow réclamé")
escrow_reclame = df[df["Escrow_reclame"] == True]

if escrow_reclame.empty:
    st.info("Aucun dossier réclamé.")
else:
    st.dataframe(escrow_reclame[[
        "Dossier N", "Nom", "Visa", "Dossier envoye"
    ]], use_container_width=True)

# ---------------------------------------------------------
# 🔍 HISTORIQUE ESCROW
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📜 Historique Escrow")

if st.button("Voir l’historique complet de l’Escrow"):
    st.write("### Historique brut (base clients)")
    st.dataframe(df, use_container_width=True)
