import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.title("💰 Escrow – Suivi des mouvements")

# ---------------------------------------------------------
# Safe conversion (évite float("") et autres erreurs)
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
# Chargement base Dropbox
# ---------------------------------------------------------
try:
    db = load_database()
except:
    db = {"clients": [], "visa": [], "escrow": [], "compta": []}

escrow = db.get("escrow", [])

# ---------------------------------------------------------
# Tableau Escrow
# ---------------------------------------------------------
st.subheader("📊 Mouvements Escrow")

if escrow:
    df = pd.DataFrame(escrow)
else:
    df = pd.DataFrame(columns=["Dossier N", "Nom", "Montant", "Date envoi", "État", "Date réclamation"])

st.dataframe(df, use_container_width=True, height=350)

st.markdown("---")


# ---------------------------------------------------------
# AJOUTER UN NOUVEAU MOUVEMENT
# ---------------------------------------------------------

st.subheader("➕ Ajouter un mouvement Escrow")

col1, col2 = st.columns(2)

with col1:
    dossier_num = st.text_input("Dossier N")
    nom = st.text_input("Nom")
    montant = st.number_input("Montant (USD)", min_value=0.0, format="%.2f")

with col2:
    date_envoi = st.date_input("Date envoi", format="YYYY-MM-DD")
    etat = st.selectbox("État", ["Envoyé", "Reçu", "En attente", "Accepté", "Refusé"])
    date_reclamation = st.date_input("Date réclamation", format="YYYY-MM-DD")

if st.button("Ajouter à Escrow", type="primary"):
    nouveau = {
        "Dossier N": dossier_num,
        "Nom": nom,
        "Montant": montant,
        "Date envoi": str(date_envoi),
        "État": etat,
        "Date réclamation": str(date_reclamation)
    }
    escrow.append(nouveau)
    db["escrow"] = escrow
    save_database(db)
    st.success("Mouvement ajouté ✔")
    st.balloons()

st.markdown("---")


# ---------------------------------------------------------
# MODIFIER / SUPPRIMER UN MOUVEMENT EXISTANT
# ---------------------------------------------------------

st.subheader("✏️ Modifier un mouvement existant")

if not escrow:
    st.info("Aucun mouvement à modifier.")
    st.stop()

liste = [f"{e.get('Dossier N', '')} - {e.get('Nom', '')} - {safe_float(e.get('Montant', 0))}$" for e in escrow]
selection = st.selectbox("Choisir un mouvement", liste)

index = liste.index(selection)
entry = escrow[index]

colA, colB = st.columns(2)

with colA:
    mod_dossier = st.text_input("Dossier N", value=str(entry.get("Dossier N", "")))
    mod_nom = st.text_input("Nom", value=str(entry.get("Nom", "")))
    mod_montant = st.number_input(
        "Montant (USD)", 
        min_value=0.0,
        value=safe_float(entry.get("Montant")),
        format="%.2f"
    )

with colB:
    mod_date_envoi = st.text_input("Date envoi", value=str(entry.get("Date envoi", "")))
    mod_etat = st.selectbox("État", ["Envoyé", "Reçu", "En attente", "Accepté", "Refusé"], index=0)
    mod_date_reclam = st.text_input("Date réclamation", value=str(entry.get("Date réclamation", "")))


if st.button("💾 Enregistrer les modifications"):
    escrow[index] = {
        "Dossier N": mod_dossier,
        "Nom": mod_nom,
        "Montant": mod_montant,
        "Date envoi": mod_date_envoi,
        "État": mod_etat,
        "Date réclamation": mod_date_reclam
    }
    db["escrow"] = escrow
    save_database(db)
    st.success("Modification enregistrée ✔")


# ---------------------------------------------------------
# SUPPRESSION
# ---------------------------------------------------------

if st.button("🗑️ Supprimer ce mouvement"):
    del escrow[index]
    db["escrow"] = escrow
    save_database(db)
    st.success("Mouvement supprimé ✔")
