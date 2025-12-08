import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.set_page_config(page_title="Escrow", page_icon="💰", layout="wide")
st.title("💰 Gestion des Escrows")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)

# ---------------------------------------------------------
# NORMALISATION DES COLONNES
# ---------------------------------------------------------
df["Escrow"] = df.get("Escrow", False)
df["Escrow_a_reclamer"] = df.get("Escrow_a_reclamer", False)
df["Escrow_reclame"] = df.get("Escrow_reclame", False)

# Conversion bool cohérente
df["Escrow"] = df["Escrow"].replace({"": False, "0": False, "1": True}).astype(bool)
df["Escrow_a_reclamer"] = df["Escrow_a_reclamer"].replace({"": False, "0": False, "1": True}).astype(bool)
df["Escrow_reclame"] = df["Escrow_reclame"].replace({"": False, "0": False, "1": True}).astype(bool)

# ---------------------------------------------------------
# AUCUNE LOGIQUE AUTOMATIQUE SUPPLÉMENTAIRE
# ---------------------------------------------------------
# ➤ Option B : L’utilisateur décide entièrement depuis Modifier_dossier
# ➤ On n'impose plus :
#     - Escrow → False si dossier envoyé
#     - Escrow → A réclamer automatiquement
# ➤ Escrow.py devient un module d'affichage uniquement.

# ---------------------------------------------------------
# TABLEAU ESCROW EN COURS
# ---------------------------------------------------------
st.subheader("📌 Escrow en cours")
escrow_cours = df[(df["Escrow"] == True) & (df["Escrow_reclame"] == False)]
st.dataframe(escrow_cours, use_container_width=True)

# ---------------------------------------------------------
# TABLEAU ESCROW À RÉCLAMER
# ---------------------------------------------------------
st.subheader("📌 Escrow à réclamer")
escrow_reclamer = df[(df["Escrow_a_reclamer"] == True) & (df["Escrow_reclame"] == False)]
st.dataframe(escrow_reclamer, use_container_width=True)

# ---------------------------------------------------------
# TABLEAU ESCROW RÉCLAMÉ
# ---------------------------------------------------------
st.subheader("📌 Escrow réclamé")
escrow_reclame = df[df["Escrow_reclame"] == True]
st.dataframe(escrow_reclame, use_container_width=True)

# ---------------------------------------------------------
# ACTION : RÉCLAMER L’ESCROW
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📝 Réclamer un Escrow")

liste_dossiers = escrow_reclamer["Dossier N"].tolist()

if len(liste_dossiers) == 0:
    st.info("Aucun Escrow à réclamer.")
else:
    choix = st.selectbox("Sélectionner un dossier à réclamer :", liste_dossiers)

    if st.button("Réclamer maintenant ✅", type="primary"):
        df.loc[df["Dossier N"] == choix, "Escrow_a_reclamer"] = False
        df.loc[df["Dossier N"] == choix, "Escrow_reclame"] = True

        db["clients"] = df.to_dict(orient="records")
        save_database(db)

        st.success(f"✔ Escrow du dossier {choix} marqué comme réclamé.")
        st.rerun()
