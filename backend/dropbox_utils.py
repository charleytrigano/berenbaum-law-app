import dropbox
import requests
import streamlit as st
import json

APP_KEY = st.secrets["dropbox"]["APP_KEY"]
APP_SECRET = st.secrets["dropbox"]["APP_SECRET"]
REFRESH_TOKEN = st.secrets["dropbox"]["REFRESH_TOKEN"]

def get_access_token():
    """Échange le refresh token contre un access token valide."""
    url = "https://api.dropbox.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": APP_KEY,
        "client_secret": APP_SECRET
    }
    r = requests.post(url, data=data)
    return r.json()["access_token"]

def get_dbx():
    return dropbox.Dropbox(get_access_token())

def load_database():
    dbx = get_dbx()
    path = st.secrets["paths"]["DROPBOX_JSON"]

    try:
        metadata, res = dbx.files_download(path)
        return json.loads(res.content.decode())
    except:
        return {"clients": [], "visa": [], "escrow": [], "compta": []}

def save_database(data):
    dbx = get_dbx()
    path = st.secrets["paths"]["DROPBOX_JSON"]

    dbx.files_upload(
        json.dumps(data, indent=2).encode(),
        path,
        mode=dropbox.files.WriteMode("overwrite")
    )
