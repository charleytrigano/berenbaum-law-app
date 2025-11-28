import streamlit as st
from backend.dropbox_utils import load_database, save_database

st.title("✏️ Modifier dossier")

db = load_database()
clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier disponible.")
    st.stop()

# Choix du dossier
liste_ids = [c.get("Dossier N", "") for c in clients]
selected = st.selectbox("Choisir un dossier", liste_ids)

client = next((c for c in clients if c.get("Dossier N") == selected), None)

if client:
    nom = st.text_input("Nom", client.get("Nom"))
    prenom = st.text_input("Prénom", client.get("Prenom"))
    statut = st.selectbox("Statut", ["En cours", "Complété", "En attente"], index=["En cours", "Complété", "En attente"].index(client.get("Statut", "En cours")))

    if st.button("Mettre à jour"):
        client["Nom"] = nom
        client["Prenom"] = prenom
        client["Statut"] = statut
        save_database(db)
        st.success("Dossier mis à jour ✔")

