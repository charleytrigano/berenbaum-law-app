import streamlit as st
from backend.google_sheets import load_sheet
from utils.config import SHEET_CLIENTS

st.title("📁 Liste des dossiers")

df = load_sheet(SHEET_CLIENTS)
st.dataframe(df, use_container_width=True)

import streamlit as st
from components.dropbox_utils import upload_to_dropbox, list_files, download_from_dropbox

st.title("Gestion des fichiers Dropbox")

# --- UPLOAD ---
uploaded = st.file_uploader("Uploader un fichier")

if uploaded:
    upload_to_dropbox(uploaded, f"/dossiers/{uploaded.name}")
    st.success("Fichier envoyé dans Dropbox !")

# --- LIST FILES ---
st.subheader("Fichiers dans Dropbox")

files = list_files("/dossiers")
st.write(files)

# --- DOWNLOAD A FILE ---
file_to_download = st.selectbox("Choisir un fichier à télécharger :", files)

if st.button("Télécharger"):
    content = download_from_dropbox(f"/dossiers/{file_to_download}")
    st.download_button("Télécharger le fichier", content, file_name=file_to_download)

