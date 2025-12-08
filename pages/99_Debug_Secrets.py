{
  "dropbox": {
    "APP_KEY": "dec5zj63pkh1clf",
    "APP_SECRET": "..."
    "DROPBOX_TOKEN": "..."
  },
  "paths": {
      "CLIENTS_FILE": "/Apps/Clients.xlsx",
      ...
  }
}
import streamlit as st
from backend.dropbox_utils import load_database

st.title("🔍 DEBUG — Chemins utilisés")

st.write("➡️ DROPBOX_JSON dans secrets.toml :")
st.code(st.secrets["paths"]["DROPBOX_JSON"])

st.write("➡️ Dossier chargé par load_database() :")
db = load_database()
st.json(db)

