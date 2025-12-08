import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.set_page_config(page_title="Escrow", page_icon="💰", layout="wide")
st.title("💰 Gestion des Escrows")

# ---------------------------------------------
# LOAD DB
# ---------------------------------------------
db = load_database()
clients = db.get("clients", [])
df = pd.DataFrame(clients)

if df.empty:
    st.warning("Aucun dossier trouvé.")
    st.stop()

# ---------------------------------------------
# NORMALISATION DES BOOLÉENS
# ---------------------------------------------
def norm_bool(x):
    if isinstance(x, bool):
        return x
    if str(x).lower() in ["1", "true", "yes", "oui"]:
        return True
    return False

for col in ["Escrow", "Escrow_a_reclamer", "Escrow_reclame", "Dossier envoye", "Dossier envoyé"]:
    if col not in df.columns:
        df[col] = False
    df[col] = df[col].apply(norm_bool)

# ➤ Fusionner les deux colonnes “envoyé”
df["Dossier_envoye_final"] = df["Dossier envoye"] | df["Dossier envoyé"]

# ---------------------------------------------
# DEBUG VISUEL
# ---------------------------------------------
st.markdown("### 🔍 DEBUG — État réel des colonnes Escrow")
st.dataframe(df[["Dossier N", "Escrow", "Escrow_a_reclamer", "Escrow_reclame", "Dossier_envoye_final"]])

# ---------------------------------------------
# TABLEAUX ESCROW
# ---------------------------------------------
escrow_en_cours = df[(df["Escrow"] == True) & (df["Escrow_a_reclamer"] == False)]
escrow_a_reclamer = df[(df["Escrow_a_reclamer"] == True)]
escrow_reclame = df[(df["Escrow_reclame"] == True)]

st.markdown("## 🔵 Escrow en cours")
st.dataframe(escrow_en_cours)

st.markdown("## 🟠 Escrow à réclamer (dossier envoyé)")
st.dataframe(escrow_a_reclamer)

st.markdown("## 🟢 Escrow réclamé")
st.dataframe(escrow_reclame)


# ---------------------------------------------
# ACTION : MARQUER COMME RÉCLAMÉ
# ---------------------------------------------
st.markdown("---")
st.subheader("📝 Marquer un Escrow comme réclamé")

if not escrow_a_reclamer.empty:
    choix = st.selectbox("Choisir un dossier :", escrow_a_reclamer["Dossier N"].tolist())
    if st.button("Valider la réclamation ✓"):
        idx = df[df["Dossier N"] == choix].index[0]

        df.loc[idx, "Escrow"] = False
        df.loc[idx, "Escrow_a_reclamer"] = False
        df.loc[idx, "Escrow_reclame"] = True

        db["clients"] = df.to_dict(orient="records")
        save_database(db)

        st.success(f"Escrow du dossier {choix} marqué comme réclamé.")
        st.rerun()
else:
    st.info("Aucun escrow à réclamer.")
