import streamlit as st
from backend.dropbox_utils import load_database, save_database

from datetime import datetime

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Gestion Escrow",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Gestion Escrow")
st.write("Suivez les mouvements financiers liés aux dossiers.")

# ---------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------
db = load_database()

if "escrow" not in db:
    db["escrow"] = []

escrows = db["escrow"]

# ---------------------------------------------------
# AFFICHAGE TABLEAU
# ---------------------------------------------------
st.subheader("📋 Mouvements Escrow")

if len(escrows) > 0:
    st.dataframe(escrows, use_container_width=True)
else:
    st.info("Aucun mouvement Escrow enregistré.")

st.markdown("---")

# ---------------------------------------------------
# FORMULAIRE AJOUT / MODIFICATION
# ---------------------------------------------------
st.subheader("➕ Ajouter / Modifier un mouvement")

# Liste des dossiers existants pour sélection
clients_list = [c["Dossier N"] for c in db.get("clients", [])]

col1, col2 = st.columns(2)

with col1:
    selected_mode = st.radio("Mode", ["Ajouter", "Modifier"])

with col2:
    selected_index = None
    if selected_mode == "Modifier" and len(escrows) > 0:
        selected_index = st.selectbox(
            "Sélectionnez un mouvement à modifier",
            list(range(len(escrows)))
        )

# Pré-remplissage si modification
if selected_mode == "Modifier" and selected_index is not None:
    entry = escrows[selected_index]
else:
    entry = {
        "Dossier N": "",
        "Nom": "",
        "Montant": "",
        "Date envoi": "",
        "État": "",
        "Date réclamation": ""
    }

# FORM
colA, colB = st.columns(2)

with colA:
    dossier = st.selectbox("📁 Dossier N", clients_list, index=clients_list.index(entry["Dossier N"]) if entry["Dossier N"] in clients_list else 0)
    nom = st.text_input("Nom", entry.get("Nom", ""))

with colB:
    montant = st.number_input("Montant (USD)", min_value=0.0, value=float(entry.get("Montant", 0)), format="%.2f")

date_envoi = st.date_input(
    "Date envoi",
    datetime.fromisoformat(entry["Date envoi"]) if entry.get("Date envoi") else datetime.now()
)

etat = st.selectbox("État", ["En attente", "Envoyé", "Accepté", "Refusé"], index=["En attente", "Envoyé", "Accepté", "Refusé"].index(entry.get("État", "En attente")))

date_reclamation = st.date_input(
    "Date réclamation",
    datetime.fromisoformat(entry["Date réclamation"]) if entry.get("Date réclamation") else datetime.now()
)

st.markdown("---")

# ---------------------------------------------------
# BOUTONS D’ACTION
# ---------------------------------------------------
colSave, colDelete = st.columns([1, 1])

with colSave:
    if st.button("💾 Enregistrer", type="primary"):
        new_entry = {
            "Dossier N": dossier,
            "Nom": nom,
            "Montant": montant,
            "Date envoi": str(date_envoi),
            "État": etat,
            "Date réclamation": str(date_reclamation)
        }

        if selected_mode == "Ajouter":
            db["escrow"].append(new_entry)
            st.success("✔️ Mouvement ajouté avec succès.")

        else:
            db["escrow"][selected_index] = new_entry
            st.success("✔️ Mouvement modifié avec succès.")

        save_database(db)
        st.balloons()

with colDelete:
    if selected_mode == "Modifier":
        if st.button("🗑️ Supprimer ce mouvement"):
            del db["escrow"][selected_index]
            save_database(db)
            st.warning("❌ Mouvement supprimé.")
            st.balloons()
