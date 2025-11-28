import streamlit as st
from backend.google_sheets import load_sheet
from utils.config import SHEET_CLIENTS

st.title("👥 Suivi clients")

df = load_sheet(SHEET_CLIENTS)

st.dataframe(df[["Dossier N", "Nom"]], use_container_width=True)

