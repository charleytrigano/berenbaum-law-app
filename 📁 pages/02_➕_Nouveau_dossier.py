import streamlit as st
from backend.dropbox_utils import load_database, save_database

st.title("➕ Nouveau dossier")

db = load_database()
clients = db.get("clients", [])

# Champs de saisie
dossier_n = st.text_input("Dossier N")
nom = st.text_input("Nom")
prenom = st.text_input("Prénom")
type_dossier = st.selectbox("Type", ["Visa", "Escrow", "Client"])
statut = st.selectbox("Statut", ["En cours", "Complété", "En attente"])

if st.button("Créer le dossier"):
    new_entry = {
        "Dossier N": dossier_n,
        "Nom": nom,
        "Prenom": prenom,
        "Type": type_dossier,
        "Statut": statut
    }

    clients.append(new_entry)
    db["clients"] = clients
    save_database(db)

    st.success("Dossier créé avec succès ! 🎉")
