import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.title("➕ Nouveau dossier")

# ---------------------------------------------------------
# TABLE DES DÉPENDANCES (depuis Visa.xlsx)
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# CHARGEMENT BASE
# ---------------------------------------------------------
try:
    db = load_database()
except:
    db = {"clients": []}

clients = db.get("clients", [])

# ---------------------------------------------------------
# GÉNÉRER AUTOMATIQUEMENT LE PROCHAIN NUMÉRO
# ---------------------------------------------------------
def nouveau_numero():
    nums = []

    for c in clients:
        n = c.get("Dossier N")

        # Cas 1 : numérique (int/float)
        if isinstance(n, (int, float)) and not pd.isna(n):
            nums.append(int(n))

        # Cas 2 : chaîne numérique ("123")
        elif isinstance(n, str) and n.isdigit():
            nums.append(int(n))

    return str(max(nums) + 1) if nums else "1"

# ---------------------------------------------------------
# FORMULAIRE
# ---------------------------------------------------------
st.subheader("Création d'un nouveau dossier")

col1, col2 = st.columns(2)

with col1:
    dossier_num = st.text_input("Dossier N", nouveau_numero())
    nom = st.text_input("Nom du client")

    categorie = st.selectbox("Catégorie", [""] + list(dependencies.keys()))

    # Sous-catégories dynamiques
    if categorie:
        souscats = [""] + list(dependencies[categorie].keys())
    else:
        souscats = [""]

    sous_categorie = st.selectbox("Sous-catégorie", souscats)

with col2:
    # Visa dépendant de catégorie + sous-catégorie
    if categorie and sous_categorie:
        visas = [""] + dependencies[categorie][sous_categorie]
    else:
        visas = [""]

    visa = st.selectbox("Visa", visas)

    commentaires = st.text_area("Commentaires")

# ---------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------
if st.button("Créer le dossier", type="primary"):

    if not nom.strip():
        st.error("Le nom du client est obligatoire.")
        st.stop()

    new_client = {
        "Dossier N": dossier_num,
        "Nom": nom,
        "Catégories": categorie,
        "Sous-catégories": sous_categorie,
        "Visa": visa,
        "Commentaires": commentaires
    }

    db["clients"].append(new_client)
    save_database(db)

    st.success(f"Dossier #{dossier_num} créé avec succès ✔")
    st.balloons()
