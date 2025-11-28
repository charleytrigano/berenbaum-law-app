import streamlit as st
from backend.dropbox_utils import load_database, save_database

from utils.config import SHEET_CLIENTS

st.title("👥 Suivi clients")

df = load_sheet(SHEET_CLIENTS)

st.dataframe(df[["Dossier N", "Nom"]], use_container_width=True)

