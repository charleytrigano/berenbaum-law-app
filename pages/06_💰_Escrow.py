import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.set_page_config(page_title="Escrow", page_icon="💰", layout="wide")
st.title("💰 Gestion des Escrows")

# ---------------------------------------------------------
# 🔹 CHARGEMENT BASE DE DONNÉES
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)

# ---------------------------------------------------------
# 🔹 NORMALISATION ROBUSTE DES 3 ÉTATS ESCROW
# ---------------------------------------------------------

def normalize_bool(x):
    if isinstance(x, bool):
        return x
    if x in ["1", 1, "true", "True", "yes", "YES"]:
        return True
    return False

# S'assurer que les colonnes existent
for col in ["Escrow", "Escrow_a_reclamer", "Escrow_reclame"]:
    if col not in df.columns:
        df[col] = False

df["Escrow"] = df["Escrow"].apply(normalize_bool)
df["Escrow_a_reclamer"] = df["Escrow_a_reclamer"].apply(normalize_bool)
df["Escrow_reclame"] = df["Escrow_reclame"].apply(normalize_bool)

# Normalisation du statut
df["Dossier envoye"] = pd.to_numeric(df.get("Dossier envoye", 0), errors="ignore").fillna(0).astype(int)

# ---------------------------------------------------------
# 🔹 LOGIQUE AUTOMATIQUE :
#    dossier envoyé → escrow passe en "à réclamer"
# ---------------------------------------------------------
df.loc[df["Dossier envoye"] == 1, "Escrow"] = False
df.loc[df["Dossier envoye"] == 1, "Escrow_a_reclamer"] = True

# ---------------------------------------------------------
# 🔹 TABLEAU 1 – Escrow en cours
# ---------------------------------------------------------
st.subheader("📌 Escrow en cours")

escrow_cours = df[(df["Escrow"] == True) & (df["Escrow_reclame"] == False)]
st.dataframe(escrow_cours, use_container_width=True)

st.info(f"Nombre total d’Escrows en cours : **{len(escrow_cours)}**")

# ---------------------------------------------------------
# 🔹 TABLEAU 2 – Escrow à réclamer
# ---------------------------------------------------------
st.subheader("📌 Escrow à réclamer")

escrow_a_rec = df[(df["Escrow_a_reclamer"] == True) & (df["Escrow_reclame"] == False)]
st.dataframe(escrow_a_rec, use_container_width=True)

st.info(f"Escrows à réclamer : **{len(escrow_a_rec)}**")

# ---------------------------------------------------------
# 🔹 TABLEAU 3 – Escrow réclamé (terminé)
# ---------------------------------------------------------
st.subheader("📌 Escrow réclamé")

escrow_done = df[df["Escrow_reclame"] == True]
st.dataframe(escrow_done, use_container_width=True)

st.info(f"Escrows déjà réclamés : **{len(escrow_done)}**")

# ---------------------------------------------------------
# 🔹 ACTION : RÉCLAMER UN ESCROW
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📝 Réclamer maintenant un Escrow")

liste_dossiers = escrow_a_rec["Dossier N"].tolist()

if len(liste_dossiers) == 0:
    st.success("Aucun Escrow à réclamer 🎉")
else:
    choix = st.selectbox("Sélectionner un dossier :", liste_dossiers)

    if st.button("✔ Marquer comme réclamé", type="primary"):
        df.loc[df["Dossier N"] == choix, "Escrow_a_reclamer"] = False
        df.loc[df["Dossier N"] == choix, "Escrow_reclame"] = True

        db["clients"] = df.to_dict(orient="records")
        save_database(db)

        st.success(f"Escrow du dossier **{choix}** est maintenant marqué comme réclamé ✔")
        st.rerun()

# ---------------------------------------------------------
# 🔹 RÉCAPITULATIF GLOBAL
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📊 Récapitulatif global")

st.write(f"- 💼 Escrow en cours : **{len(escrow_cours)}**")
st.write(f"- 📬 Escrow à réclamer : **{len(escrow_a_rec)}**")
st.write(f"- ✔ Escrow réclamés : **{len(escrow_done)}**")
