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
# 🔹 NORMALISATION ESCROW (version robuste)
# ---------------------------------------------------------
def normalize_bool(x):
    """Transforme toutes les valeurs possibles en bool propre."""
    if isinstance(x, bool):
        return x
    if x in [1, "1", "True", "true", "YES", "yes"]:
        return True
    return False

df["Escrow"] = df.get("Escrow", False).apply(normalize_bool)

# Colonnes éventuelles manquantes
for col in ["Escrow_a_reclamer", "Escrow_reclame"]:
    if col not in df.columns:
        df[col] = False

df["Escrow_a_reclamer"] = df["Escrow_a_reclamer"].apply(normalize_bool)
df["Escrow_reclame"] = df["Escrow_reclame"].apply(normalize_bool)

# ---------------------------------------------------------
# 🔹 LOGIQUE AUTOMATIQUE :
#     Si un dossier est envoyé → Escrow passe en "à réclamer"
# ---------------------------------------------------------
df["Dossier envoye"] = pd.to_numeric(df.get("Dossier envoye", 0), errors="coerce").fillna(0).astype(int)

df.loc[df["Dossier envoye"] == 1, "Escrow"] = False
df.loc[df["Dossier envoye"] == 1, "Escrow_a_reclamer"] = True


# ---------------------------------------------------------
# 🔹 TABLEAUX
# ---------------------------------------------------------
st.markdown("## 📌 Escrow en cours")

escrow_cours = df[(df["Escrow"] == True) & (df["Escrow_reclame"] == False)]
st.dataframe(escrow_cours, use_container_width=True)

# Total
st.write(f"**Total dossiers Escrow en cours : {len(escrow_cours)}**")


st.markdown("## 📌 Escrow à réclamer")

escrow_reclamer = df[(df["Escrow_a_reclamer"] == True) & (df["Escrow_reclame"] == False)]
st.dataframe(escrow_reclamer, use_container_width=True)

st.write(f"**Total Escrow à réclamer : {len(escrow_reclamer)}**")


st.markdown("## 📌 Escrow réclamé")

escrow_ok = df[df["Escrow_reclame"] == True]
st.dataframe(escrow_ok, use_container_width=True)

st.write(f"**Total Escrow réclamés : {len(escrow_ok)}**")


# ---------------------------------------------------------
# 🔹 ACTION : RÉCLAMER UN ESCROW
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📝 Réclamer un Escrow")

liste_dossiers = escrow_reclamer["Dossier N"].tolist()

if len(liste_dossiers) == 0:
    st.info("Aucun Escrow à réclamer.")
else:
    choix = st.selectbox("Sélectionner un dossier :", liste_dossiers)

    if st.button("Réclamer maintenant ✅", type="primary"):
        df.loc[df["Dossier N"] == choix, "Escrow_a_reclamer"] = False
        df.loc[df["Dossier N"] == choix, "Escrow_reclame"] = True

        # Sauvegarde
        db["clients"] = df.to_dict(orient="records")
        save_database(db)

        st.success(f"✔ Escrow du dossier {choix} marqué comme réclamé.")
        st.rerun()


# ---------------------------------------------------------
# 🔹 TOTAL GÉNÉRAL (optionnel)
# ---------------------------------------------------------
st.markdown("---")
total_cours = len(escrow_cours)
total_reclamer = len(escrow_reclamer)
total_reclame = len(escrow_ok)

st.subheader("📊 Récapitulatif global")
st.write(f"- Escrow en cours : **{total_cours}**")
st.write(f"- Escrow à réclamer : **{total_reclamer}**")
st.write(f"- Escrow réclamés : **{total_reclame}**")
