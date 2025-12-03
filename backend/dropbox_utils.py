import json
import dropbox
import streamlit as st
from backend.clean_json import clean_database

data = clean_database(data)

from backend.clean_json import clean_database

# ----------------------------------------------------
# 🔐 Chargement des secrets
# ----------------------------------------------------
APP_KEY = st.secrets["dropbox"]["APP_KEY"]
APP_SECRET = st.secrets["dropbox"]["APP_SECRET"]
REFRESH_TOKEN = st.secrets["dropbox"]["DROPBOX_TOKEN"]
JSON_PATH = st.secrets["paths"]["DROPBOX_JSON"]


# ----------------------------------------------------
# 🔄 Authentification via Refresh Token
# ----------------------------------------------------
def get_dbx():
    """Client Dropbox authentifié automatiquement."""
    return dropbox.Dropbox(
        oauth2_refresh_token=REFRESH_TOKEN,
        app_key=APP_KEY,
        app_secret=APP_SECRET
    )


# ----------------------------------------------------
# 📥 Charger JSON depuis Dropbox
# ----------------------------------------------------
def load_database():
    try:
        dbx = get_dbx()
        metadata, res = dbx.files_download(JSON_PATH)

        data = json.loads(res.content.decode("utf-8"))

        # Nettoyage automatique
        return clean_database(data)

    except Exception as e:
        print("❌ Erreur load_database :", e)
        return {"clients": [], "visa": [], "escrow": [], "compta": []}


# ----------------------------------------------------
# 📤 Sauvegarder JSON dans Dropbox
# ----------------------------------------------------
def save_database(data):
    try:
        dbx = get_dbx()
        dbx.files_upload(
            json.dumps(data, indent=2).encode("utf-8"),
            JSON_PATH,
            mode=dropbox.files.WriteMode("overwrite")
        )
    except Exception as e:
        print("❌ Erreur save_database :", e)
