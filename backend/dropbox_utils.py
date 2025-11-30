import json
import dropbox
import streamlit as st

APP_KEY = st.secrets["dropbox"]["APP_KEY"]
APP_SECRET = st.secrets["dropbox"]["APP_SECRET"]
REFRESH_TOKEN = st.secrets["dropbox"]["DROPBOX_TOKEN"]
JSON_PATH = st.secrets["paths"]["DROPBOX_JSON"]


def dropbox_client():
    """Client Dropbox avec refresh automatique du token."""
    return dropbox.Dropbox(
        oauth2_refresh_token=REFRESH_TOKEN,
        app_key=APP_KEY,
        app_secret=APP_SECRET
    )


def load_database():
    """Lit le JSON sur Dropbox."""
    dbx = dropbox_client()

    try:
        md, res = dbx.files_download(JSON_PATH)
        return json.loads(res.content.decode("utf-8"))
    except Exception as e:
        st.error(f"❌ Erreur load_database : {e}")
        return {"clients": [], "visa": [], "escrow": [], "compta": []}


def save_database(data: dict):
    """Écrit le JSON sur Dropbox."""
    dbx = dropbox_client()

    dbx.files_upload(
        json.dumps(data, indent=2).encode("utf-8"),
        JSON_PATH,
        mode=dropbox.files.WriteMode("overwrite")
    )
