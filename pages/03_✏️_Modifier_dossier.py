import streamlit as st
import pandas as pd
from datetime import datetime, date
from backend.dropbox_utils import load_database, save_database

st.set_page_config(page_title="Modifier dossier", page_icon="✏️", layout="wide")
st.title("✏️ Modifier un dossier")

# ---------------------------------------------------------
# SAFE HELPERS
# ---------------------------------------------------------
def parse_date_safe(value):
    """Convertit une date JSON → date Python ou None."""
    if not value or pd.isna(value) or value == "":
        return None
    try:
        return pd.to_datetime(value).date()
    except:
        return None

def normalize_float(value):
    """Convertit proprement un champ numérique JSON en float."""
    try:
        if value in ["", None, " ", "-", "nan"]:
            return 0.0
        return float(value)
    except:
        return 0.0

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.error("Aucun dossier trouvé dans la base.")
    st.stop()

df = pd.DataFrame(clients)

# ---------------------------------------------------------
# 🔍 AUTO-DETECTION DE LA COLONNE DU NUMÉRO DE DOSSIER
# ---------------------------------------------------------
possible_cols = [
    "Dossier N", "Dossier", "Dossier Numéro", "Numero", "Numéro",
    "No", "N dossier", "DossierN", "dossier n", "dossier"
]

DOSSIER_COL = None
for col in df.columns:
    if col.strip().lower() in [c.lower() for c in possible_cols]:
        DOSSIER_COL = col
        break

if DOSSIER_COL is None:
    st.error("❌ Impossible de trouver la colonne du numéro de dossier dans la base.")
    st.write("Colonnes trouvées :", df.columns.tolist())
    st.stop()

# ---------------------------------------------------------
# LISTE DES DOSSIERS
# ---------------------------------------------------------
try:
    liste_dossiers = sorted(df[DOSSIER_COL].dropna().unique().tolist())
except Exception as e:
    st.error(f"Erreur lors de la lecture des numéros de dossiers : {e}")
    st.write("Colonnes disponibles :", df.columns.tolist())
    st.stop()

selected = st.selectbox("Sélectionner un dossier", liste_dossiers)

# Sélection du dossier
dossier = df[df[DOSSIER_COL] == selected].iloc[0].copy()

# ---------------------------------------------------------
# FORMULAIRE
# ---------------------------------------------------------

st.subheader("📄 Informations du dossier")

col1, col2, col3 = st.columns(3)

with col1:
    numero = st.number_input("Dossier N", value=int(dossier.get(DOSSIER_COL)), step=1)

with col2:
    nom = st.text_input("Nom", value=dossier.get("Nom", ""))

with col3:
    d_creation = st.date_input(
        "Date de création",
        value=parse_date_safe(dossier.get("Date"))
    )

# ---------------------------------------------------------
# FINANCES
# ---------------------------------------------------------

st.subheader("💵 Finances")

colA, colB, colC = st.columns(3)

with colA:
    honoraires = st.number_input(
        "Montant honoraires (US $)", value=normalize_float(dossier.get("Montant honoraires (US $)", 0))
    )

with colB:
    autres = st.number_input(
        "Autres frais (US $)", value=normalize_float(dossier.get("Autres frais (US $)", 0))
    )

with colC:
    total = honoraires + autres
    st.metric("Total facturé", f"${total:,.2f}")

# ---------------------------------------------------------
# ACOMPTE
# ---------------------------------------------------------
st.subheader("💰 Acomptes")

colA1, colA2, colA3, colA4 = st.columns(4)

a1 = colA1.number_input("Acompte 1", value=normalize_float(dossier.get("Acompte 1")))
a2 = colA2.number_input("Acompte 2", value=normalize_float(dossier.get("Acompte 2")))
a3 = colA3.number_input("Acompte 3", value=normalize_float(dossier.get("Acompte 3")))
a4 = colA4.number_input("Acompte 4", value=normalize_float(dossier.get("Acompte 4")))

encaissé = a1 + a2 + a3 + a4
solde = total - encaissé
st.metric("Solde", f"${solde:,.2f}")

# Dates acomptes
colD1, colD2, colD3, colD4 = st.columns(4)

d_a1 = colD1.date_input("Date Acompte 1", value=parse_date_safe(dossier.get("Date Acompte 1")))
d_a2 = colD2.date_input("Date Acompte 2", value=parse_date_safe(dossier.get("Date Acompte 2")))
d_a3 = colD3.date_input("Date Acompte 3", value=parse_date_safe(dossier.get("Date Acompte 3")))
d_a4 = colD4.date_input("Date Acompte 4", value=parse_date_safe(dossier.get("Date Acompte 4")))

# ---------------------------------------------------------
# SAUVEGARDE
# ---------------------------------------------------------

st.markdown("---")
colSave, colDelete = st.columns(2)

if colSave.button("💾 Enregistrer les modifications", type="primary"):
    for idx, row in df.iterrows():
        if row[DOSSIER_COL] == selected:
            df.at[idx, DOSSIER_COL] = numero
            df.at[idx, "Nom"] = nom
            df.at[idx, "Date"] = d_creation

            df.at[idx, "Montant honoraires (US $)"] = honoraires
            df.at[idx, "Autres frais (US $)"] = autres

            df.at[idx, "Acompte 1"] = a1
            df.at[idx, "Acompte 2"] = a2
            df.at[idx, "Acompte 3"] = a3
            df.at[idx, "Acompte 4"] = a4

            df.at[idx, "Date Acompte 1"] = d_a1
            df.at[idx, "Date Acompte 2"] = d_a2
            df.at[idx, "Date Acompte 3"] = d_a3
            df.at[idx, "Date Acompte 4"] = d_a4

    db["clients"] = df.to_dict(orient="records")
    save_database(db)

    st.success("✔ Dossier mis à jour avec succès !")
    st.rerun()

# ---------------------------------------------------------
# SUPPRESSION AVEC HISTORIQUE
# ---------------------------------------------------------

if colDelete.button("🗑️ Supprimer ce dossier", type="secondary"):
    if "deleted_clients" not in db:
        db["deleted_clients"] = []

    db["deleted_clients"].append(dossier)
    df = df[df[DOSSIER_COL] != selected]
    db["clients"] = df.to_dict(orient="records")

    save_database(db)

    st.success("🗑️ Dossier supprimé et ajouté à l'historique.")
    st.rerun()
