import streamlit as st
from backend.dropbox_utils import load_database

st.set_page_config(page_title="Debug Secrets", page_icon="🛠️")

st.title("🔍 DEBUG — Secrets & Chemins Dropbox")

# Montrer les secrets
st.subheader("📦 Contenu de st.secrets")
st.json({
    "dropbox": {
        "APP_KEY": st.secrets["dropbox"]["APP_KEY"],
        "APP_SECRET": st.secrets["dropbox"]["APP_SECRET"],
        "DROPBOX_TOKEN": st.secrets["dropbox"]["DROPBOX_TOKEN"]
    },
    "paths": st.secrets["paths"]
})

# Chemin JSON réellement utilisé
st.subheader("📁 Chemin JSON utilisé :")
st.code(st.secrets["paths"]["DROPBOX_JSON"])

# Contenu JSON chargé
st.subheader("📄 Base JSON chargée :")
db = load_database()
st.json(db)
