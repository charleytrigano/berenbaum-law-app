import streamlit as st

# --------------------------------------------------
# 🔐 DROBOX AUTH
# --------------------------------------------------
APP_KEY = st.secrets["dropbox"]["APP_KEY"]
APP_SECRET = st.secrets["dropbox"]["APP_SECRET"]
DROPBOX_REFRESH_TOKEN = st.secrets["dropbox"]["DROPBOX_TOKEN"]  # refresh token Dropbox

# --------------------------------------------------
# 📁 PATHS DROPBOX
# --------------------------------------------------
CLIENTS_FILE = st.secrets["paths"]["CLIENTS_FILE"]
ESCROW_FILE = st.secrets["paths"]["ESCROW_FILE"]
VISA_FILE = st.secrets["paths"]["VISA_FILE"]
COMPTA_FILE = st.secrets["paths"]["COMPTA_FILE"]
DROPBOX_JSON = st.secrets["paths"]["DROPBOX_JSON"]
