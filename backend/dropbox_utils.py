# backend/dropbox_utils.py
import json
import dropbox
import streamlit as st
from backend.clean_json import clean_database

APP_KEY = st.secrets["dropbox"]["APP_KEY"]
APP_SECRET = st.secrets["dropbox"]["APP_SECRET"]
REFRESH_TOKEN = st.secrets["dropbox"]["DROPBOX_TOKEN"]
JSON_PATH = st.secrets["paths"]["DROPBOX_JSON"]

def get_dbx():
    import requests
    resp = requests.post(
        "https://api.dropbox.com/oauth2/token",
        data={
            "refresh_token": REFRESH_TOKEN,
            "client_id": APP_KEY,
            "client_secret": APP_SECRET,
            "grant_type": "refresh_token",
        }
    )
    access_token = resp.json()["access_token"]
    return dropbox.Dropbox(access_token)

def load_database():
    """Télécharge le JSON Dropbox + nettoyage cohérent."""
    try:
        dbx = get_dbx()
        metadata, res = dbx.files_download(JSON_PATH)
        data = json.loads(res.content.decode("utf-8"))

        # Nettoyage intelligent et normalisation Escrow
        data = clean_database(data)

        return data
    except Exception as e:
        print("❌ Erreur load_database :", e)
        return {"clients": [], "visa": [], "escrow": [], "compta": []}

def save_database(data):
    """Sauvegarde JSON propre dans Dropbox."""
    try:
        dbx = get_dbx()
        cleaned = clean_database(data)

        dbx.files_upload(
            json.dumps(cleaned, indent=2).encode("utf-8"),
            JSON_PATH,
            mode=dropbox.files.WriteMode("overwrite")
        )
    except Exception as e:
        print("❌ Erreur save_database :", e)
