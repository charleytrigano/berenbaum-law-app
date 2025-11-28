import streamlit as st
from components.database import load_database, save_database
from datetime import datetime

# ---------------------------------------------------
# PAGE SETUP
# ---------------------------------------------------
st.set_page_config(page_title="Gestion Visa", page_icon="🛂", layout="wide")

st.title("🛂 Gestion des dossiers Visa")
st.write("Ajouter, modifier ou supprimer les dossiers liés aux visas.")

# ---------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------
db = load_database()

if "visa" not in db:
    db["visa"] = []

visa_list = db["visa"]

# ---------------------------------------------------
# AFFICHAGE DES DONNÉES
# ---------------------------------------------------
st.subheader("📋 Liste des dossiers Visa")

if len(visa_list) > 0:
    st.dataframe(visa_list, use_container_width=True)
else:
    st.info("Aucun dossier Visa enregistré.")

st.markdown("---")

# ---------------------------------------------------
# FORMULAIRE AJOUT / MODIFICATION
# ---------------------------------------------------
st.subheader("➕ Ajouter / Modifier un dossier Visa")

# Liste des clients existants
clients = db.get("clients", [])
dossiers = [c["Dossier N"] for c in clients] if clients else []

col1, col2 = st.columns(2)

with col1:
    mode = st.radio("Mode", ["Ajouter", "Modifier"])

with col2:
    selected_index = None
    if mode == "Modifier" and len(visa_list) > 0:
        selected_index = st.selectbox(
            "Sélectionner un dossier à modifier",
            list(range(len(visa_list)))
        )

# Pré-remplissage
if mode == "Modifier" and selected_index is not None:
    entry = visa_list[selected_index]
else:
    entry = {
        "Dossier N": "",
        "Nom": "",
        "Type Visa": "",
        "Date": "",
        "Statut": "",
        "Commentaires": ""
    }

# Champs
colA, colB = st.columns(2)

with colA:
    dossier = st.selectbox(
        "📁 Dossier N",
        dossiers,
        index=dossiers.index(entry["Dossier N"]) if entry["Dossier N"] in dossiers else 0
    )
    nom = st.text_input("Nom", entry.get("Nom", ""))

with colB:
    type_visa = st.text_input("Type de Visa", entry.get("Type Visa", ""))
    statut = st.selectbox(
        "Statut",
        ["En cours", "Soumis", "Accepté", "Refusé"],
        index=["En cours", "Soumis", "Accepté", "Refusé"].index(entry.get("Statut", "En cours"))
    )

date = st.date_input(
    "Date",
    datetime.fromisoformat(entry["Date"]) if entry.get("Date") else datetime.now()
)

commentaires = st.text_area("Commentaires", entry.get("Commentaires", ""))

st.markdown("---")

# ---------------------------------------------------
# BOUTONS ACTION
# ---------------------------------------------------
colSave, colDelete = st.columns([1, 1])

with colSave:
    if st.button("💾 Enregistrer", type="primary"):
        new_entry = {
            "Dossier N": dossier,
            "Nom": nom,
            "Type Visa": type_visa,
            "Date": str(date),
            "Statut": statut,
            "Commentaires": commentaires
        }

        if mode == "Ajouter":
            db["visa"].append(new_entry)
            st.success("✔️ Dossier Visa ajouté.")
        else:
            db["visa"][selected_index] = new_entry
            st.success("✔️ Dossier Visa modifié.")

        save_database(db)
        st.balloons()

with colDelete:
    if mode == "Modifier" and st.button("🗑️ Supprimer ce dossier"):
        del db["visa"][selected_index]
        save_database(db)
        st.warning("❌ Dossier Visa supprimé.")
        st.balloons()
