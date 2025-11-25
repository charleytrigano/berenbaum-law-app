import streamlit as st
from backend.google_sheets import append_row
from backend.google_sheets import load_sheet
from utils.config import SHEET_CLIENTS

st.title("➕ Nouveau dossier")

df = load_sheet(SHEET_CLIENTS)

with st.form("new_dossier_form"):
    col1, col2 = st.columns(2)

    dossier_n = col1.text_input("Dossier N")
    nom = col1.text_input("Nom")
    date = col2.date_input("Date")
    categorie = col2.text_input("Catégorie")

    submitted = st.form_submit_button("Créer")

if submitted:
    if dossier_n.strip() == "" or nom.strip() == "":
        st.error("Les champs obligatoires doivent être remplis.")
    else:
        append_row(SHEET_CLIENTS, [dossier_n, nom, str(date), categorie])
        st.success("Dossier créé avec succès !")
