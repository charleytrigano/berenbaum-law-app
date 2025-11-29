import streamlit as st

DROPBOX_TOKEN = st.secrets["dropbox"]["DROPBOX_TOKEN"]
DROPBOX_FILE_PATH = "/Apps/berenbaum-law/database.json"


SHEET_CLIENTS = "Clients"
SHEET_ESCROW = "Escrow"
SHEET_VISA = "Visa"
SHEET_COMPTA = "ComptaCli"
