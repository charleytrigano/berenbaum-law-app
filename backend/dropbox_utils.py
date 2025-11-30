import dropbox
import json
import streamlit as st

# ---------------------------------------------------------
# Authentification Dropbox (refresh_token)
# ---------------------------------------------------------
APP_KEY = st.secrets["dropbox"]["APP_KEY"]
APP_SECRET = st.secrets["dropbox"]["APP_SECRET"]
REFRESH_TOKEN = st.secrets["dropbox"]["DROPBOX_TOKEN"]

def get_dbx():
    """Retourne un client Dropbox authentifié via refresh token"""
    return dropbox.Dropbox(
        oauth2_refresh_token=REFRESH_TOKEN,
        app_key=APP_KEY,
        app_secret=APP_SECRET
    )

# ---------------------------------------------------------
# Télécharger un fichier depuis Dropbox
# ---------------------------------------------------------
def dropbox_download(path):
    dbx = get_dbx()
    metadata, res = dbx.files_download(path)
    return res.content  # bytes

# ---------------------------------------------------------
# Écrire un JSON dans Dropbox
# ---------------------------------------------------------
def dropbox_upload_json(path, data):
    dbx = get_dbx()

    dbx.files_upload(
        json.dumps(data, indent=2).encode("utf-8"),
        path,
        mode=dropbox.files.WriteMode("overwrite")
    )
