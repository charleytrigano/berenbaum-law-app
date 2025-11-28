import streamlit as st
from components.database import load_database, save_database
from datetime import datetime
import pandas as pd

# ---------------------------------------------------
# PAGE SETUP
# ---------------------------------------------------
st.set_page_config(page_title="Comptabilité Clients", page_icon="📒", layout="wide")

st.title("📒 Comptabilité – Berenbaum Law")
st.write("Suivi des paiements, honoraires et mouvements financiers clients.")

# ---------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------
db = load_database()

if "compta" not in db:
    db["compta"] = []

compta_list = db["compta"]

# ---------------------------------------------------
# AFFICHAGE TABLEAU
# ---------------------------------------------------
st.subheader("📋 Liste des mouvements comptables")

if len(compta_list) > 0:
    df_compta = pd.DataFrame(compta_list)
    st.dataframe(df_compta, use_container_width=True)
else:
    st.info("Aucune donnée comptable enregistrée.")

st.markdown("---")

# ---------------------------------------------------
# INDICATEURS
# ---------------------------------------------------
st.subheader("📊 Indicateurs comptables")

if len(compta_list) > 0:
    df_compta["Montant"] = pd.to_numeric(df_compta["Montant"], errors="coerce").fillna(0)

    total_global = df_compta["Montant"].sum()
    mois = datetime.now().strftime("%Y-%m")

    df_compta["Mois"] = df_compta["Date"].str.slice(0, 7)
    total_mensuel = df_compta[df_compta["Mois"] == mois]["Montant"].sum()
else:
    total_global = 0
    total_mensuel = 0

colA, colB = st.columns(2)
colA.metric("Total global", f"${total_global:,.2f}")
colB.metric("Total du mois", f"${total_mensuel:,.2f}")

st.markdown("---")

# ---------------------------------------------------
# FORMULAIRE AJOUT / MODIFICATION
# ---------------------------------------------------
st.subheader("➕ Ajouter / Modifier un mouvement")

# Liste des clients existants
clients = db.get("clients", [])
dossiers = [c["Dossier N"] for c in clients] if clients else []

mode = st.radio("Mode", ["Ajouter", "Modifier"])

selected_index = None
if mode == "Modifier" and len(compta_list) > 0:
    selected_index = st.selectbox("Sélectionner un mouvement", list(range(len(compta_list))))

# Pré-remplissage
if mode == "Modifier" and selected_index is not None:
    entry = compta_list[selected_index]
else:
    entry = {
        "Dossier N": "",
        "Nom": "",
        "Date": "",
        "Montant": "",
        "Type": "",
        "Commentaires": ""
    }

# FORMULAIRE
col1, col2 = st.columns(2)

with col1:
    dossier = st.selectbox(
        "📁 Dossier N",
        dossiers,
        index=dossiers.index(entry["Dossier N"]) if entry["Dossier N"] in dossiers else 0
    )
    nom = st.text_input("Nom", entry.get("Nom", ""))

with col2:
    montant = st.number_input("Montant (USD)", value=float(entry.get("Montant", 0)), format="%.2f")
    type_op = st.selectbox(
        "Type d'opération",
        ["Honoraires", "Acompte", "Frais", "Remboursement", "Autre"],
        index=["Honoraires", "Acompte", "Frais", "Remboursement", "Autre"].index(entry.get("Type", "Honoraires"))
    )

date = st.date_input(
    "Date",
    datetime.fromisoformat(entry["Date"]) if entry.get("Date") else datetime.now()
)

comment = st.text_area("Commentaires", entry.get("Commentaires", ""))

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
            "Date": str(date),
            "Montant": montant,
            "Type": type_op,
            "Commentaires": comment
        }

        if mode == "Ajouter":
            db["compta"].append(new_entry)
            st.success("✔️ Mouvement ajouté.")
        else:
            db["compta"][selected_index] = new_entry
            st.success("✔️ Mouvement modifié.")

        save_database(db)
        st.balloons()

with colDelete:
    if mode == "Modifier" and st.button("🗑️ Supprimer ce mouvement"):
        del db["compta"][selected_index]
        save_database(db)
        st.warning("❌ Mouvement supprimé.")
        st.balloons()
