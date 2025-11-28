import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.title("🛂 Gestion des dossiers Visa")

# ---------------------------------------------------------
# Conversion sécurisée pour les montants
# ---------------------------------------------------------
def safe_float(x, default=0.0):
    try:
        if x is None:
            return default
        if isinstance(x, (int, float)):
            return float(x)
        x = str(x).replace(",", ".").strip()
        return float(x) if x != "" else default
    except:
        return default


# ---------------------------------------------------------
# Charger la base Dropbox
# ---------------------------------------------------------
try:
    db = load_database()
except:
    db = {"clients": [], "visa": [], "escrow": [], "compta": []}

visa_entries = db.get("visa", [])


# ---------------------------------------------------------
# Tableau de bord
# ---------------------------------------------------------
st.subheader("📋 Liste des dossiers Visa")

if visa_entries:
    df = pd.DataFrame(visa_entries)
else:
    df = pd.DataFrame(columns=[
        "Dossier N", "Nom", "Type Visa", "Statut", "Frais USCIS",
        "Frais Cabinet", "Date Soumission", "Commentaires"
    ])

st.dataframe(df, use_container_width=True, height=350)

st.markdown("---")


# ---------------------------------------------------------
# AJOUTER UN DOSSIER VISA
# ---------------------------------------------------------
st.subheader("➕ Ajouter un dossier Visa")

VISA_TYPES = [
    "I-130", "I-140", "I-485", "I-765", "I-131",
    "EB1", "EB2", "EB3", "H-1B", "O-1", "E-2", "F-1",
    "I-526", "I-829", "Autre"
]

col1, col2 = st.columns(2)

with col1:
    dnum = st.text_input("Dossier N")
    nom = st.text_input("Nom")
    type_visa = st.selectbox("Type de Visa", VISA_TYPES)

with col2:
    frais_uscis = st.number_input("Frais USCIS ($)", min_value=0.0, format="%.2f")
    frais_cabinet = st.number_input("Frais Cabinet ($)", min_value=0.0, format="%.2f")
    date_soumission = st.date_input("Date de soumission", format="YYYY-MM-DD")

commentaires = st.text_area("Commentaires")

if st.button("Ajouter le dossier Visa", type="primary"):
    new_entry = {
        "Dossier N": dnum,
        "Nom": nom,
        "Type Visa": type_visa,
        "Statut": "En cours",
        "Frais USCIS": frais_uscis,
        "Frais Cabinet": frais_cabinet,
        "Date Soumission": str(date_soumission),
        "Commentaires": commentaires
    }
    visa_entries.append(new_entry)
    db["visa"] = visa_entries
    save_database(db)
    st.success("Dossier Visa ajouté ✔")
    st.balloons()

st.markdown("---")


# ---------------------------------------------------------
# MODIFIER / SUPPRIMER UN DOSSIER VISA
# ---------------------------------------------------------
st.subheader("✏️ Modifier un dossier Visa")

if not visa_entries:
    st.info("Aucun dossier Visa à modifier.")
    st.stop()

# Liste déroulante
liste = [
    f"{v.get('Dossier N', '')} - {v.get('Nom', '')} ({v.get('Type Visa', '')})"
    for v in visa_entries
]
selection = st.selectbox("Choisir un dossier", liste)

index = liste.index(selection)
entry = visa_entries[index]

STATUTS = ["En cours", "Soumis", "Accepté", "Refusé"]

# Sélection sécurisée du statut
statut_actuel = entry.get("Statut", "En cours")
if statut_actuel not in STATUTS:
    statut_actuel = "En cours"
index_statut = STATUTS.index(statut_actuel)

# Sélection sécurisée du type visa
visa_actuel = entry.get("Type Visa", "Autre")
if visa_actuel not in VISA_TYPES:
    visa_actuel = "Autre"
index_visa = VISA_TYPES.index(visa_actuel)

colA, colB = st.columns(2)

with colA:
    mod_dnum = st.text_input("Dossier N", value=str(entry.get("Dossier N", "")))
    mod_nom = st.text_input("Nom", value=str(entry.get("Nom", "")))
    mod_type_visa = st.selectbox("Type Visa", VISA_TYPES, index=index_visa)

with colB:
    mod_statut = st.selectbox("Statut", STATUTS, index=index_statut)
    mod_frais_uscis = st.number_input(
        "Frais USCIS ($)",
        value=safe_float(entry.get("Frais USCIS", 0)),
        format="%.2f"
    )
    mod_frais_cabinet = st.number_input(
        "Frais Cabinet ($)",
        value=safe_float(entry.get("Frais Cabinet", 0)),
        format="%.2f"
    )

mod_date = st.text_input("Date Soumission", value=str(entry.get("Date Soumission", "")))
mod_comment = st.text_area("Commentaires", value=str(entry.get("Commentaires", "")))

if st.button("💾 Enregistrer les modifications"):
    visa_entries[index] = {
        "Dossier N": mod_dnum,
        "Nom": mod_nom,
        "Type Visa": mod_type_visa,
        "Statut": mod_statut,
        "Frais USCIS": mod_frais_uscis,
        "Frais Cabinet": mod_frais_cabinet,
        "Date Soumission": mod_date,
        "Commentaires": mod_comment
    }
    db["visa"] = visa_entries
    save_database(db)
    st.success("Dossier Visa mis à jour ✔")


# ---------------------------------------------------------
# SUPPRESSION
# ---------------------------------------------------------
st.markdown("---")

if st.button("🗑️ Supprimer ce dossier Visa"):
    del visa_entries[index]
    db["visa"] = visa_entries
    save_database(db)
    st.success("Dossier supprimé ✔")
