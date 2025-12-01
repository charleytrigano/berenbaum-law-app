import json
import dropbox
import streamlit as st

# ---------------------------------------------
# 🔐 Chargement des secrets Dropbox
# ---------------------------------------------
APP_KEY = st.secrets["dropbox"]["APP_KEY"]
APP_SECRET = st.secrets["dropbox"]["APP_SECRET"]
REFRESH_TOKEN = st.secrets["dropbox"]["DROPBOX_TOKEN"]

JSON_PATH = st.secrets["paths"]["DROPBOX_JSON"]

# ---------------------------------------------
# 🔄 Obtenir un access_token PROPRE via refresh token
# ---------------------------------------------
def get_dbx():
    """Retourne un client Dropbox avec un access_token actualisé."""
    oauth_result = dropbox.DropboxOAuth2FlowNoRedirect(
        consumer_key=APP_KEY,
        consumer_secret=APP_SECRET
    )

    # Demande un nouveau access_token à partir du refresh_token
    token_result = dropbox.oauth.RefreshResult(
        access_token=None,
        expires_in=None,
        refresh_token=REFRESH_TOKEN,
        scope=None,
        token_type="bearer",
        account_id=None,
        user_id=None
    )

    dbx = dropbox.Dropbox(
        oauth2_refresh_token=REFRESH_TOKEN,
        app_key=APP_KEY,
        app_secret=APP_SECRET
    )

    return dbx

# ---------------------------------------------
# 📥 Charger la base JSON
# ---------------------------------------------
def load_database():
    try:
        dbx = get_dbx()
        metadata, res = dbx.files_download(JSON_PATH)
        data = json.loads(res.content.decode("utf-8"))
        return data
    except Exception as e:
        print("❌ Erreur load_database :", e)
        return {"clients": [], "visa": [], "escrow": [], "compta": []}

# ---------------------------------------------
# 📤 Sauvegarder la base JSON
# ---------------------------------------------
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

import json
import streamlit as st
import dropbox
from utils.config import (
    APP_KEY,
    APP_SECRET,
    DROPBOX_REFRESH_TOKEN,
    DROPBOX_JSON
)


# ----------------------------------------------------
# 🔄 Authentification Dropbox via REFRESH TOKEN
# ----------------------------------------------------
def get_dbx():
    """Retourne un client Dropbox authentifié avec refresh token."""
    return dropbox.Dropbox(
        oauth2_refresh_token=DROPBOX_REFRESH_TOKEN,
        app_key=APP_KEY,
        app_secret=APP_SECRET
    )


# ----------------------------------------------------
# 📥 Charger le JSON depuis Dropbox
# ----------------------------------------------------
from backend.clean_json import clean_database

def load_database():
    try:
        dbx = get_dbx()
        metadata, res = dbx.files_download(JSON_PATH)

        data = json.loads(res.content.decode("utf-8"))

        # 🧹 Nettoyage automatique du JSON
        clean = clean_database(data)
        return clean

    except Exception as e:
        print("❌ Erreur load_database :", e)
        return {"clients": [], "visa": [], "escrow": [], "compta": []}

from backend.clean_json import clean_database

def load_database():
    try:
        dbx = get_dbx()
        metadata, res = dbx.files_download(JSON_PATH)

        # Décodage JSON
        data = json.loads(res.content.decode("utf-8"))

        # 🧹 Nettoyage automatique
        data = clean_database(data)

        return data

    except Exception as e:
        print("❌ Erreur load_database :", e)
        return {"clients": [], "visa": [], "escrow": [], "compta": []}




# ----------------------------------------------------
# 📤 Sauvegarder le JSON dans Dropbox
# ----------------------------------------------------
def save_database(data):
    try:
        dbx = get_dbx()
        dbx.files_upload(
            json.dumps(data, indent=2).encode("utf-8"),
            DROPBOX_JSON,
            mode=dropbox.files.WriteMode("overwrite")
        )
    except Exception as e:
        print("❌ Erreur save_database :", e)

