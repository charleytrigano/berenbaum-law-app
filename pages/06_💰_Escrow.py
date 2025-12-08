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
# NORMALISATION ROBUSTE (Escrow + Dossier envoyé)
# ---------------------------------------------------------

def normalize_bool(x):
    """Convertit proprement toutes les formes de vrai/faux en bool."""
    if isinstance(x, bool):
        return x
    if str(x).lower() in ["1", "true", "yes", "oui"]:
        return True
    return False

# Normaliser Escrow / Escrow_a_reclamer / Escrow_reclame
for col in ["Escrow", "Escrow_a_reclamer", "Escrow_reclame"]:
    if col not in df.columns:
        df[col] = False
    df[col] = df[col].apply(normalize_bool)

# Normaliser Dossier envoyé
if "Dossier envoye" not in df.columns:
    df["Dossier envoye"] = False

df["Dossier envoye"] = df["Dossier envoye"].apply(normalize_bool)

# ---------------------------------------------------------
# LOGIQUE AUTOMATIQUE (RETIRÉE)
# ---------------------------------------------------------
# Option B : AUCUNE logique automatique ici.
# Tout est contrôlé par Modifier_dossier.py.

# ---------------------------------------------------------
# TABLEAU : ESCROW EN COURS
# ---------------------------------------------------------
st.subheader("📌 Escrow en cours")

escrow_cours = df[
    (df["Escrow"] == True) &
    (df["Escrow_reclame"] == False) &
    (df["Escrow_a_reclamer"] == False) &
    (df["Dossier envoye"] == False)
]

st.dataframe(escrow_cours, use_container_width=True)

# ---------------------------------------------------------
# TABLEAU : ESCROW À RÉCLAMER
# ---------------------------------------------------------
st.subheader("📌 Escrow à réclamer")

escrow_reclamer = df[
    (df["Escrow_a_reclamer"] == True) &
    (df["Escrow_reclame"] == False)
]

st.dataframe(escrow_reclamer, use_container_width=True)

# ---------------------------------------------------------
# TABLEAU : ESCROW RÉCLAMÉ
# ---------------------------------------------------------
st.subheader("📌 Escrow réclamé")

escrow_reclame = df[df["Escrow_reclame"] == True]

st.dataframe(escrow_reclame, use_container_width=True)

# ---------------------------------------------------------
# ACTION : RÉCLAMER UN ESCROW
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📝 Réclamer un Escrow")

liste_dossiers = escrow_reclamer["Dossier N"].tolist()

if not liste_dossiers:
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
