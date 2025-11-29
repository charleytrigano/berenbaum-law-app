import streamlit as st

# ---- Dropbox config ----
DROPBOX_TOKEN = st.secrets["DROPBOX_TOKEN"]

# 🔥 Chemin correct du fichier JSON dans Dropbox :
DROPBOX_FILE_PATH = "/Apps/berenbaum-law/database.json"

# ---- Sheet (non utilisés maintenant) ----
SHEET_CLIENTS = "Clients"
SHEET_ESCROW = "Escrow"
SHEET_VISA = "Visa"
SHEET_COMPTA = "ComptaCli"
