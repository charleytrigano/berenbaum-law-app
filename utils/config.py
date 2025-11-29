import streamlit as st

# ---- Dropbox config ----
DROPBOX_TOKEN = st.secrets["dropbox"]["DROPBOX_TOKEN"]

# 🔥 Chemin correct du fichier JSON dans Dropbox :
DROPBOX_FILE_PATH = "/Apps/berenbaum-law/database.json"

# ---- Sheet names (non utilisés mais conservés) ----
SHEET_CLIENTS = "Clients"
SHEET_ESCROW = "Escrow"
SHEET_VISA = "Visa"
SHEET_COMPTA = "ComptaCli"
