import json
import dropbox
import streamlit as st

# Le token Dropbox doit être dans secrets.toml
DBX = dropbox.Dropbox(st.secrets["DROPBOX_TOKEN"])

# Chemin du fichier dans Dropbox
DB_PATH = "/database.json"

# ----------------------------------------
# Charger (et créer si absent)
# ----------------------------------------
def load_database():
    try:
        metadata, res = DBX.files_download(DB_PATH)
        return json.loads(res.content)
    except dropbox.exceptions.ApiError:
        # Le fichier N'EXISTE PAS → on le crée
        empty_data = {
            "clients": [],
            "escrow": [],
            "visa": [],
            "compta": []
        }
        save_database(empty_data)
        return empty_data

# ----------------------------------------
# Sauvegarder dans Dropbox
# ----------------------------------------
def save_database(data):
    DBX.files_upload(
        json.dumps(data, indent=2).encode(),
        DB_PATH,
        mode=dropbox.files.WriteMode("overwrite")
    )
