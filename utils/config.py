import streamlit as st

# ---- Dropbox config ----
DROPBOX_TOKEN = st.secrets["dropbox"]["DROPBOX_TOKEN"]
DROPBOX_FILE_PATH = st.secrets["paths"]["DROPBOX_FILE_PATH"]

# ---- Sheet Names ----
SHEET_CLIENTS = "Clients"
SHEET_ESCROW = "Escrow"
SHEET_VISA = "Visa"
SHEET_COMPTA = "ComptaCli"
