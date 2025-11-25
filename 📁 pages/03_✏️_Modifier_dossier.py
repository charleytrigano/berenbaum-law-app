import streamlit as st
from backend.google_sheets import (
    load_sheet, find_row_index, update_row, delete_row_safely
)
from utils.config import SHEET_CLIENTS
import pandas as pd

st.title("✏️ Modifier / Supprimer un dossier")

df = load_sheet(SHEET_CLIENTS)
columns = df.columns.tolist()

st.subheader("Sélectionner un dossier")
dossier_id = st.selectbox("Choisissez un Dossier N :", df["Dossier N"])

row_index = find_row_index(SHEET_CLIENTS, dossier_id)
row_data = df.loc[row_index].to_dict()

st.subheader("Modifier les informations")
updated_data = {}

for col in columns:
    val = row_data[col]
    if "Date" in col:
        val = pd.to_datetime(val).date() if val else None
        updated_data[col] = st.date_input(col, value=val)
    elif "Montant" in col or "Acompte" in col:
        updated_data[col] = st.number_input(col, value=float(val) if val else 0.0)
    else:
        updated_data[col] = st.text_input(col, value=val)

if st.button("💾 Enregistrer les modifications"):
    update_row(SHEET_CLIENTS, row_index, [updated_data[c] for c in columns])
    st.success("Modifications enregistrées ✔")

st.markdown("---")
st.subheader("❌ Supprimer le dossier")

if st.button("Supprimer le dossier DEFINITIVEMENT"):
    delete_row_safely(SHEET_CLIENTS, row_index)
    st.error("Dossier supprimé !")

