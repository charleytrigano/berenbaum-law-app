import json
import dropbox
import streamlit as st

# ---------------------------
# CHARGEMENT DES SECRETS
# ---------------------------

APP_KEY = st.secrets["dropbox"]["APP_KEY"]
APP_SECRET = st.secrets["dropbox"]["APP_SECRET"]
REFRESH_TOKEN = st.secrets["dropbox"]["DROPBOX_TOKEN"]  # ✔ OK
JSON_PATH = st.secrets["paths"]["DROPBOX_JSON"]          # ✔ OK

# ---------------------------
# RÉCUPÉRER ACCESS TOKEN
# ---------------------------

def get_access_token():
    """Échange le refresh token contre un access token valide."""
    dbx = dropbox.DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)
    oauth_result = dbx.refresh_access_token(REFRESH_TOKEN)
    return oauth_result.access_token


# ---------------------------
# CLIENT DROPBOX
# ---------------------------

def get_client():
    access_token = get_access_token()
    return dropbox.Dropbox(oauth2_access_token=access_token)


# ---------------------------
# LECTURE JSON
# ---------------------------

def load_database():
    """Télécharge et charge le fichier JSON depuis Dropbox."""
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
    """Écrit le JSON sur Dropbox."""
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
