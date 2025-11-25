import streamlit as st
from backend.google_sheets import append_row, load_sheet
from utils.config import SHEET_CLIENTS

st.title("➕ Nouveau dossier")

df = load_sheet(SHEET_CLIENTS)
columns = df.columns.tolist()

st.subheader("Créer un dossier")

with st.form("form_new_dossier"):
    inputs = {}

    for col in columns:
        # Champs basiques
        if "Date" in col:
            inputs[col] = st.date_input(col)
        elif "Montant" in col or "Acompte" in col:
            inputs[col] = st.number_input(col, value=0.0)
        else:
            inputs[col] = st.text_input(col)

    submitted = st.form_submit_button("Créer le dossier")

if submitted:
    row = [inputs[col] for col in columns]
    append_row(SHEET_CLIENTS, row)
    st.success("Dossier ajouté avec succès ! 🔥")
    st.info("Actualisez la page Liste des dossiers pour voir la mise à jour.")
