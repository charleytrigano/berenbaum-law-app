import json
import dropbox
import streamlit as st

# ---------------------------
# CHARGEMENT DES SECRETS
# ---------------------------

APP_KEY = st.secrets["dropbox"]["APP_KEY"]
APP_SECRET = st.secrets["dropbox"]["APP_SECRET"]
REFRESH_TOKEN = st.secrets["dropbox"]["DROPBOX_TOKEN"]  # Refresh token permanent
JSON_PATH = st.secrets["paths"]["DROPBOX_JSON"]


# ---------------------------
# CLIENT DROPBOX AVEC REFRESH TOKEN
# ---------------------------

def get_client():
    """Retourne le client Dropbox en utilisant le refresh token (automatique)."""
    return dropbox.Dropbox(
        oauth2_refresh_token=REFRESH_TOKEN,
        app_key=APP_KEY,
        app_secret=APP_SECRET
    )


# ---------------------------
# LECTURE JSON
# ---------------------------

def load_database():
    try:
        dbx = get_client()
        metadata, res = dbx.files_download(JSON_PATH)
        data = json.loads(res.content.decode("utf-8"))
        return data

    except Exception as e:
        st.error(f"❌ Erreur load_database : {e}")
        return {"clients": [], "visa": [], "escrow": [], "compta": []}


# ---------------------------
# ÉCRITURE JSON
# ---------------------------

def save_database(data):
    try:
        dbx = get_client()
        dbx.files_upload(
            json.dumps(data, indent=2).encode("utf-8"),
            JSON_PATH,
            mode=dropbox.files.WriteMode("overwrite")
        )
        return True

    except Exception as e:
        st.error(f"❌ Erreur save_database : {e}")
        return False
