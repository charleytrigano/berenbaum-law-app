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

# Garder uniquement ceux cochés
escrow_en_cours = df[df.get("Escrow", False) == True]

st.dataframe(escrow_en_cours)


# ---------------------------------------------------------
# SECURISATION DES COLONNES
# ---------------------------------------------------------

# Dossier envoye → 0/1
df["Dossier envoye"] = pd.to_numeric(df.get("Dossier envoye", 0), errors="coerce").fillna(0).astype(int)

# Escrow (True/False)
df["Escrow"] = df.get("Escrow", False)
df["Escrow"] = df["Escrow"].replace({"": False, "0": False, "1": True, 0: False, 1: True})
df["Escrow"] = df["Escrow"].fillna(False).astype(bool)

# Escrow réclamé
df["Escrow_reclame"] = df.get("Escrow_reclame", False)
df["Escrow_reclame"] = df["Escrow_reclame"].replace({"": False, "0": False, "1": True})
df["Escrow_reclame"] = df["Escrow_reclame"].fillna(False).astype(bool)

# Montants
df["Acompte 1"] = pd.to_numeric(df.get("Acompte 1", 0), errors="coerce").fillna(0)

# ---------------------------------------------------------
# LOGIQUE AUTOMATIQUE ESCROW
# ---------------------------------------------------------

# 1 → Si dossier envoyé, l’escrow passe en "à réclamer"
df.loc[df["Dossier envoye"] == 1, "Escrow"] = False
df.loc[df["Dossier envoye"] == 1, "Escrow_a_reclamer"] = True

# Créer colonne si absente
if "Escrow_a_reclamer" not in df.columns:
    df["Escrow_a_reclamer"] = False

df["Escrow_a_reclamer"] = df.get("Escrow_a_reclamer", False)
df["Escrow_a_reclamer"] = df["Escrow_a_reclamer"].replace({"": False, "0": False, "1": True})
df["Escrow_a_reclamer"] = df["Escrow_a_reclamer"].fillna(False).astype(bool)

# ---------------------------------------------------------
# TABLEAUX
# ---------------------------------------------------------
st.subheader("📌 Escrow en cours")
escrow_cours = df[(df["Escrow"] == True) & (df["Escrow_reclame"] == False)]
st.dataframe(escrow_cours, use_container_width=True)

st.subheader("📌 Escrow à réclamer")
escrow_reclamer = df[(df["Escrow_a_reclamer"] == True) & (df["Escrow_reclame"] == False)]
st.dataframe(escrow_reclamer, use_container_width=True)

st.subheader("📌 Escrow réclamé")
escrow_reclame = df[df["Escrow_reclame"] == True]
st.dataframe(escrow_reclame, use_container_width=True)

# ---------------------------------------------------------
# ACTION : RECLAMER L’ESCROW
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

        # Mise à jour JSON
        db["clients"] = df.to_dict(orient="records")
        save_database(db)

        st.success(f"✔ Escrow du dossier {choix} marqué comme réclamé.")
        st.rerun()


