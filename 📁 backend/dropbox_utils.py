import json
import dropbox
import streamlit as st
from utils.config import DROPBOX_TOKEN, DROPBOX_FILE_PATH

# ---------------------------------------------------------
# Charger la base
# ---------------------------------------------------------
def load_database():
    dbx = dropbox.Dropbox(DROPBOX_TOKEN)
    try:
        _, res = dbx.files_download(DROPBOX_FILE_PATH)
        data = json.loads(res.content.decode("utf-8"))
        return data
    except dropbox.exceptions.ApiError:
        # Fichier absent → on crée une base par défaut
        data = {"clients": []}
        save_database(data)
        return data

# ---------------------------------------------------------
# Sauvegarder la base
# ---------------------------------------------------------
def save_database(data):
    dbx = dropbox.Dropbox(DROPBOX_TOKEN)
    dbx.files_upload(
        json.dumps(data, indent=2).encode("utf-8"),
        DROPBOX_FILE_PATH,
        mode=dropbox.files.WriteMode("overwrite")
    )
