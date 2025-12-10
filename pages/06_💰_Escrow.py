import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

from utils.sidebar import render_sidebar
render_sidebar()


st.set_page_config(page_title="Gestion des Escrows", page_icon="💰", layout="wide")
st.title("💰 Gestion des Escrows")

# ---------------------------------------------------------
# 🔹 Chargement base JSON
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

df = pd.DataFrame(clients)

def normalize_bool(x):
    if isinstance(x, bool):
        return x
    if str(x).lower() in ["true", "1", "yes", "oui"]:
        return True
    return False

for col in ["Escrow", "Escrow_a_reclamer", "Escrow_reclame", "Dossier_envoye"]:
    if col not in df.columns:
        df[col] = False
    df[col] = df[col].apply(normalize_bool)


# ---------------------------------------------------------
# 🔍 DEBUG – Affichage brut des colonnes Escrow
# ---------------------------------------------------------
with st.expander("🔍 DEBUG — État réel des colonnes Escrow"):
    st.dataframe(df[[
        "Dossier N", "Escrow", "Escrow_a_reclamer", "Escrow_reclame", "Dossier_envoye"
    ]])


# ---------------------------------------------------------
# 🟦 1 — ESCROW EN COURS
# ---------------------------------------------------------
st.markdown("## 🟦 Escrow en cours")

escrow_en_cours = df[df["Escrow"] == True]

if escrow_en_cours.empty:
    st.info("Aucun dossier en Escrow en cours.")
else:
    st.dataframe(escrow_en_cours)


# ---------------------------------------------------------
# 🟧 2 — ESCROW À RÉCLAMER (Dossier envoyé)
# ---------------------------------------------------------
st.markdown("## 🟧 Escrow à réclamer (dossier envoyé)")

a_reclamer = df[(df["Escrow_a_reclamer"] == True) & (df["Escrow_reclame"] == False)]

if a_reclamer.empty:
    st.info("Aucun dossier à réclamer.")
else:
    st.dataframe(a_reclamer)


# ---------------------------------------------------------
# 🟩 3 — ESCROW RÉCLAMÉ
# ---------------------------------------------------------
st.markdown("## 🟩 Escrow réclamé")

reclames = df[df["Escrow_reclame"] == True]

if reclames.empty:
    st.info("Aucun dossier marqué comme réclamé.")
else:
    st.dataframe(reclames)


# ---------------------------------------------------------
# 🕒 TIMELINE ESCROW
# ---------------------------------------------------------
st.markdown("---")
st.markdown("## 🕒 Historique / Timeline Escrow")

timeline_data = []

for _, row in df.iterrows():
    etat = "Aucun"
    color = "gray"

    if row["Escrow"] == True:
        etat = "En cours"
        color = "blue"
    elif row["Escrow_a_reclamer"] == True and row["Escrow_reclame"] == False:
        etat = "À réclamer"
        color = "orange"
    elif row["Escrow_reclame"] == True:
        etat = "Réclamé"
        color = "green"

    timeline_data.append({
        "Dossier N": row["Dossier N"],
        "Nom": row.get("Nom", ""),
        "État Escrow": etat,
        "Couleur": color
    })

timeline_df = pd.DataFrame(timeline_data)

st.dataframe(timeline_df)


# ---------------------------------------------------------
# 🛠️ ACTIONS SUR UN DOSSIER
# ---------------------------------------------------------
st.markdown("---")
st.markdown("## 🛠️ Modifier l'état d'un Escrow")

selection = st.selectbox(
    "Choisir un dossier",
    df["Dossier N"].dropna().astype(int).tolist()
)

row = df[df["Dossier N"] == selection].iloc[0]

st.write(f"### Dossier **{selection} — {row.get('Nom', '')}**")

etat_actuel = (
    "En cours" if row["Escrow"] else
    "À réclamer" if row["Escrow_a_reclamer"] else
    "Réclamé" if row["Escrow_reclame"] else "Aucun"
)

st.info(f"**État actuel : {etat_actuel}**")

colA, colB, colC = st.columns(3)

# Passer en Escrow en cours
if colA.button("🟦 Mettre en Escrow en cours"):
    df.loc[df["Dossier N"] == selection, ["Escrow", "Escrow_a_reclamer", "Escrow_reclame"]] = [True, False, False]
    st.success("Le dossier est maintenant en Escrow *en cours*.")
    db["clients"] = df.to_dict(orient="records")
    save_database(db)
    st.rerun()

# Marquer comme à réclamer
if colB.button("🟧 Marquer comme 'À réclamer'"):
    df.loc[df["Dossier N"] == selection, ["Escrow", "Escrow_a_reclamer", "Escrow_reclame"]] = [False, True, False]
    st.success("Le dossier est maintenant dans *Escrow à réclamer*.")
    db["clients"] = df.to_dict(orient="records")
    save_database(db)
    st.rerun()

# Marquer comme réclamé
if colC.button("🟩 Marquer comme 'Réclamé'"):
    df.loc[df["Dossier N"] == selection, ["Escrow", "Escrow_a_reclamer", "Escrow_reclame"]] = [False, False, True]
    st.success("Le dossier est maintenant en *Escrow réclamé*.")
    db["clients"] = df.to_dict(orient="records")
    save_database(db)
    st.rerun()
