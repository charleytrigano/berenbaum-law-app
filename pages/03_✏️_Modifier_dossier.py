import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.set_page_config(page_title="Modifier un dossier", page_icon="✏️", layout="wide")
st.title("✏️ Modifier un dossier")

# ------------------------------------------------------------
# DÉPENDANCES CATÉGORIE → SOUS-CATÉGORIE → VISA
# ------------------------------------------------------------
dependencies = {
    "Affaires / Tourisme": {
        "B-1": ["1-COS", "2-EOS"],
        "B-2": ["1-COS", "2-EOS"]
    },
    "Professionnel": {
        "P-1": ["1-Inv.", "2-CP", "3-USCIS"],
        "P-2": ["1-CP", "2-USCIS"]
    },
    "Travailleur temporaire": {
        "H-1B": ["1-Initial", "2-Extension", "3-Transfer", "4-CP"],
        "H-2B": ["2-CP.1"],
        "E-3": ["1-Employement"]
    },
    "Immigration permanente - EB": {
        "EB1": ["1-I-140", "2-AOS", "3-I-140 & AOS", "4-CP.1"],
        "EB2": ["4-Perm", "5-CP"],
        "EB5": ["1-I-526", "2-AOS.1", "3-I527 & AOS", "4-CP.2", "I-829"]
    },
    "Immigration familiale": {
        "I-130": ["2-I-130", "3-AOS", "4-I-130 & AOS", "5-CP.1"],
        "K-1": ["1-CP.1", "2-AOS.2"]
    },
    "Autres": {
        "Traditional": ["Traditional"],
        "Marriage": ["Marriage"],
        "Derivatives": ["Derivatives"],
        "Travel Permit": ["Travel Permit"],
        "Work Permit": ["Work Permit"],
        "I-751": ["I-751"],
        "Re-entry Permit": ["Re-entry Permit"],
        "I-90": ["I-90"],
        "Consultation": ["Consultation"],
        "Analysis": ["Analysis"],
        "Referral": ["Referral"],
        "I-407": ["I-407"]
    }
}

# ------------------------------------------------------------
# Chargement BDD
# ------------------------------------------------------------
try:
    db = load_database()
except:
    st.error("Erreur chargement base Dropbox.")
    st.stop()

clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier dans la base.")
    st.stop()

st.subheader("Sélection du dossier")

liste = [f"{c.get('Dossier N','?')} - {c.get('Nom','')}" for c in clients]
selection = st.selectbox("Choisir un dossier", liste)

index = liste.index(selection)
dossier = clients[index]

# Fonction safe pour montants
def safe_float(x):
    try:
        return float(str(x).replace(",", "."))
    except:
        return 0.0

# ------------------------------------------------------------
# FORMULAIRE DE MODIFICATION
# ------------------------------------------------------------
st.subheader("Modifier les informations du dossier")

col1, col2 = st.columns(2)

with col1:
    num = st.text_input("Dossier N", value=str(dossier.get("Dossier N", "")))
    nom = st.text_input("Nom", value=dossier.get("Nom", ""))

    # ----- Catégorie -----
    categorie_actuelle = dossier.get("Catégories", "")
    categorie = st.selectbox(
        "Catégorie",
        list(dependencies.keys()),
        index=list(dependencies.keys()).index(categorie_actuelle) if categorie_actuelle in dependencies else 0
    )

    # ----- Sous-catégorie dépendante -----
    souscats = list(dependencies[categorie].keys())
    souscat_actuelle = dossier.get("Sous-catégories", "")
    sous_categorie = st.selectbox(
        "Sous-catégorie",
        souscats,
        index=souscats.index(souscat_actuelle) if souscat_actuelle in souscats else 0
    )

with col2:
    # ----- Visa dépendant -----
    visas = dependencies[categorie][sous_categorie]
    visa_actuel = dossier.get("Visa", "")
    visa = st.selectbox(
        "Visa",
        visas,
        index=visas.index(visa_actuel) if visa_actuel in visas else 0
    )

    montant_hono = st.number_input(
        "Montant honoraires (US $)",
        value=safe_float(dossier.get("Montant honoraires (US $)", 0)),
        format="%.2f"
    )
    autres_frais = st.number_input(
        "Autres frais (US $)",
        value=safe_float(dossier.get("Autres frais (US $)", 0)),
        format="%.2f"
    )

commentaire = st.text_area("Commentaires", value=dossier.get("Commentaires", ""))

# ------------------------------------------------------------
# BOUTON ENREGISTRER
# ------------------------------------------------------------
if st.button("💾 Enregistrer les modifications", type="primary"):
    clients[index] = {
        "Dossier N": num,
        "Nom": nom,
        "Catégories": categorie,
        "Sous-catégories": sous_categorie,
        "Visa": visa,
        "Montant honoraires (US $)": montant_hono,
        "Autres frais (US $)": autres_frais,
        "Commentaires": commentaire
    }

    db["clients"] = clients
    save_database(db)

    st.success("Modifications enregistrées ✔")

# ------------------------------------------------------------
# SUPPRESSION
# ------------------------------------------------------------
st.markdown("---")
st.subheader("❌ Supprimer ce dossier")

if st.button("🗑️ Supprimer définitivement le dossier"):
    del clients[index]
    db["clients"] = clients
    save_database(db)
    st.success("Dossier supprimé ✔")
    st.stop()
