import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.title("✏️ Modifier un dossier")

# --------------------------------------------------
# Chargement base Dropbox
# --------------------------------------------------
try:
    db = load_database()
except:
    db = {"clients": []}

clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier enregistré.")
    st.stop()

df = pd.DataFrame(clients)

# --------------------------------------------------
# Mapping Catégorie → Sous-catégories → Visa
# --------------------------------------------------
dependencies = {
    "Affaires / Tourisme": {
        "B-1": ["1-COS", "2-EOS"],
        "B-2": ["1-COS", "2-EOS"]
    },
    "Étudiant": {
        "F-1": ["1-COS", "2-EOS"],
        "M-1": ["1-COS", "2-EOS"]
    },
    "Travail": {
        "H-1B": ["Initial", "Transfer", "Extension"],
        "O-1": ["Initial", "Extension"]
    }
}

# --------------------------------------------------
# Sélection dossier
# --------------------------------------------------
liste = [f"{c['Dossier N']} - {c['Nom']}" for c in clients]
selection = st.selectbox("Choisir un dossier", liste)

index = liste.index(selection)
dossier = clients[index]

# --------------------------------------------------
# FORMULAIRE
# --------------------------------------------------
st.subheader("Modifier les informations du dossier")

col1, col2 = st.columns(2)

with col1:
    numero = st.text_input("Dossier N", value=str(dossier.get("Dossier N", "")))
    nom = st.text_input("Nom", value=dossier.get("Nom", ""))

    # Catégorie
    categories = list(dependencies.keys())
    cat_actuelle = dossier.get("Catégories", categories[0])

    categorie = st.selectbox(
        "Catégorie",
        categories,
        index=categories.index(cat_actuelle) if cat_actuelle in categories else 0
    )

    # Sous-catégorie dépendante
    souscats = list(dependencies[categorie].keys())
    souscat_actuelle = dossier.get("Sous-catégories", souscats[0])

    sous_categorie = st.selectbox(
        "Sous-catégorie",
        souscats,
        index=souscats.index(souscat_actuelle) if souscat_actuelle in souscats else 0
    )

with col2:
    # VISA dépend de (catégorie + sous-catégorie)
    visas = dependencies[categorie][sous_categorie]
    visa_actuelle = dossier.get("Visa", visas[0])

    visa = st.selectbox(
        "Visa",
        visas,
        index=visas.index(visa_actuelle) if visa_actuelle in visas else 0
    )

    montant_hono = st.number_input(
        "Montant honoraires (US $)",
        value=float(dossier.get("Montant honoraires (US $)", 0)),
        format="%.2f"
    )

    autres_frais = st.number_input(
        "Autres frais (US $)",
        value=float(dossier.get("Autres frais (US $)", 0)),
        format="%.2f"
    )

commentaires = st.text_area("Commentaires", value=dossier.get("Commentaires", ""))

# --------------------------------------------------
# BOUTON ENREGISTRER
# --------------------------------------------------
if st.button("💾 Enregistrer les modifications", type="primary"):
    clients[index] = {
        "Dossier N": numero,
        "Nom": nom,
        "Catégories": categorie,
        "Sous-catégories": sous_categorie,
        "Visa": visa,
        "Montant honoraires (US $)": montant_hono,
        "Autres frais (US $)": autres_frais,
        "Commentaires": commentaires
    }

    db["clients"] = clients
    save_database(db)
    st.success("Modifications enregistrées ✔")

# --------------------------------------------------
# SUPPRESSION
# --------------------------------------------------
st.markdown("---")
if st.button("🗑️ Supprimer le dossier"):
    del clients[index]
    db["clients"] = clients
    save_database(db)
    st.success("Dossier supprimé ✔")
    st.stop()
