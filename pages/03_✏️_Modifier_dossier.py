import streamlit as st
import pandas as pd
from datetime import datetime, date
from backend.dropbox_utils import load_database, save_database

st.set_page_config(page_title="Modifier dossier", page_icon="✏️", layout="wide")
st.title("✏️ Modifier un dossier")

# ---------------------------------------------------------
# Helpers
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
        if value in ["", None, " ", "-"]:
            return 0.0
        return float(value)
    except:
        return 0.0

# ---------------------------------------------------------
# Load database
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.error("Aucun dossier trouvé dans la base.")
    st.stop()

df = pd.DataFrame(clients)

DOSSIER_COL = "Dossier N"
if DOSSIER_COL not in df.columns:
    st.error("❌ La colonne 'Dossier N' est introuvable dans la base.")
    st.stop()

# Liste dossiers
liste_dossiers = sorted(df[DOSSIER_COL].dropna().unique().tolist())

selected = st.selectbox("Sélectionner un dossier", liste_dossiers)

dossier = df[df[DOSSIER_COL] == selected].iloc[0].copy()

# ---------------------------------------------------------
# FORMULAIRE
# ---------------------------------------------------------
st.subheader("📄 Informations du dossier")

col1, col2, col3 = st.columns(3)

with col1:
    numero = st.number_input("Dossier N", value=int(dossier.get("Dossier N", 0)), step=1)

with col2:
    nom = st.text_input("Nom", value=dossier.get("Nom", ""))

with col3:
    d_creation = st.date_input(
        "Date de création",
        value=parse_date_safe(dossier.get("Date"))
    )

# Ligne finances
st.subheader("💵 Finances")

colA, colB, colC = st.columns(3)

with colA:
    honoraires = st.number_input(
        "Montant honoraires (US $)",
        value=normalize_float(dossier.get("Montant honoraires (US $)", 0.0))
    )

with colB:
    autres = st.number_input(
        "Autres frais (US $)",
        value=normalize_float(dossier.get("Autres frais (US $)", 0.0))
    )

with colC:
    total = honoraires + autres
    st.metric("Total facturé", f"${total:,.2f}")

# Ligne acomptes
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
# STATUTS DOSSIER
# ---------------------------------------------------------
st.subheader("📌 Statuts du dossier")

colS1, colS2, colS3, colS4, colS5 = st.columns(5)

envoye = colS1.checkbox("Dossier envoyé", value=bool(dossier.get("Dossier envoye")))
accepte = colS2.checkbox("Dossier accepté", value=bool(dossier.get("Dossier accepte")))
refuse = colS3.checkbox("Dossier refusé", value=bool(dossier.get("Dossier refuse")))
annule = colS4.checkbox("Dossier annulé", value=bool(dossier.get("Dossier Annule")))
rfe = colS5.checkbox("RFE", value=bool(dossier.get("RFE")))

colD1, colD2, colD3, colD4, colD5 = st.columns(5)

d_env = colD1.date_input("Date envoi", value=parse_date_safe(dossier.get("Date envoi")))
d_acc = colD2.date_input("Date acceptation", value=parse_date_safe(dossier.get("Date acceptation")))
d_ref = colD3.date_input("Date refus", value=parse_date_safe(dossier.get("Date refus")))
d_ann = colD4.date_input("Date annulation", value=parse_date_safe(dossier.get("Date annulation")))
d_rfe = colD5.date_input("Date RFE", value=parse_date_safe(dossier.get("Date reclamation")))

# Escrow
escrow = st.checkbox("Escrow", value=bool(dossier.get("Escrow", False)))

# ---------------------------------------------------------
# BOUTONS ACTION
# ---------------------------------------------------------
st.markdown("---")
colB1, colB2 = st.columns(2)

# -------- SAVE --------
if colB1.button("💾 Enregistrer les modifications", type="primary"):
    for idx, row in df.iterrows():
        if row[DOSSIER_COL] == selected:
            df.at[idx, "Dossier N"] = numero
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

            df.at[idx, "Dossier envoye"] = float(envoye)
            df.at[idx, "Dossier accepte"] = float(accepte)
            df.at[idx, "Dossier refuse"] = float(refuse)
            df.at[idx, "Dossier Annule"] = float(annule)
            df.at[idx, "RFE"] = float(rfe)

            df.at[idx, "Date envoi"] = d_env
            df.at[idx, "Date acceptation"] = d_acc
            df.at[idx, "Date refus"] = d_ref
            df.at[idx, "Date annulation"] = d_ann
            df.at[idx, "Date reclamation"] = d_rfe

            df.at[idx, "Escrow"] = escrow

    db["clients"] = df.to_dict(orient="records")
    save_database(db)

    st.success("✔ Dossier mis à jour avec succès !")
    st.rerun()

# -------- DELETE --------
if colB2.button("🗑️ Supprimer ce dossier", type="secondary"):
    if "deleted_clients" not in db:
        db["deleted_clients"] = []

    db["deleted_clients"].append(dossier)

    df = df[df[DOSSIER_COL] != selected]
    db["clients"] = df.to_dict(orient="records")

    save_database(db)

    st.success("🗑️ Dossier supprimé et archivé dans deleted_clients.")
    st.rerun()
