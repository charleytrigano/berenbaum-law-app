import streamlit as st

# ---------------------------------
# Google Sheets (désactivé maintenant)
# ---------------------------------
# FILE_ID = "ton_id_si_un_jour_tu_reviens_sur_GSheets"

# ---------------------------------
# Dropbox configuration
# ---------------------------------
DROPBOX_TOKEN = st.secrets["dropbox"]["DROPBOX_TOKEN"]
DROPBOX_FILE_PATH = st.secrets["paths"]["DROPBOX_FILE_PATH"]

# ---------------------------------
# Sheets names (pour cohérence)
# ---------------------------------
SHEET_CLIENTS = "Clients"
SHEET_ESCROW = "Escrow"
SHEET_VISA = "Visa"
SHEET_COMPTA = "ComptaCli"
