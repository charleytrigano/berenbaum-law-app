import json
import dropbox
import streamlit as st

DBX = dropbox.Dropbox(st.secrets["DROPBOX_TOKEN"])
DB_PATH = "/database.json"

# ----------------------------------------
# Charger (ou créer si absent)
# ----------------------------------------
def load_database():
    try:
        metadata, res = DBX.files_download(DB_PATH)
        data = json.loads(res.content)
        return data
    except dropbox.exceptions.ApiError:
        # ➜ Le fichier N’EXISTE PAS → on le crée vide
        empty_data = {"clients": [], "escrow": [], "visa": [], "compta": []}
        save_database(empty_data)
        return empty_data

# ----------------------------------------
# Sauvegarder
# ----------------------------------------
def save_database(data):
    DBX.files_upload(
        json.dumps(data).encode(),
        DB_PATH,
        mode=dropbox.files.WriteMode("overwrite")
    )
