import json
import dropbox
import streamlit as st

# ----------------------------------------------------
# CONFIG (Streamlit Secrets)
# ----------------------------------------------------
APP_KEY = st.secrets["dropbox"]["APP_KEY"]
APP_SECRET = st.secrets["dropbox"]["APP_SECRET"]
REFRESH_TOKEN = st.secrets["dropbox"]["DROPBOX_TOKEN"]
JSON_PATH = st.secrets["paths"]["DROPBOX_JSON"]


# ----------------------------------------------------
# OAUTH2 — Obtention d'un access token valide
# ----------------------------------------------------
def get_access_token():
    """Génère un access_token en utilisant le refresh_token Dropbox OAuth2."""
    url = "https://api.dropbox.com/oauth2/token"

    data = {
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token",
        "client_id": APP_KEY,
        "client_secret": APP_SECRET
    }

    import requests
    r = requests.post(url, data=data)

    if r.status_code != 200:
        raise Exception(f"Erreur OAuth Dropbox : {r.text}")

    return r.json()["access_token"]


def get_dbx():
    """Retourne un client Dropbox authentifié."""
    token = get_access_token()
    return dropbox.Dropbox(token)


# ----------------------------------------------------
# JSON SAFE — Convertit toute structure Python → JSON valide
# ----------------------------------------------------
def json_safe(obj):
    import pandas as pd
    import numpy as np

    if isinstance(obj, dict):
        return {k: json_safe(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [json_safe(x) for x in obj]

    # Dates Pandas
    if isinstance(obj, (pd.Timestamp,)):
        return obj.strftime("%Y-%m-%d")

    # NumPy types
    if isinstance(obj, (np.integer, np.floating)):
        return obj.item()

    if obj is None:
        return ""

    # Autres types non JSON
    if not isinstance(obj, (int, float, str, bool)):
        return str(obj)

    return obj


# ----------------------------------------------------
# LOAD JSON
# ----------------------------------------------------
def load_database():
    """Télécharge et charge le JSON depuis Dropbox."""
    dbx = get_dbx()

    try:
        metadata, res = dbx.files_download(JSON_PATH)
        data = json.loads(res.content.decode("utf-8"))
        return data
    except Exception as e:
        print("Erreur load_database:", e)
        return {"clients": [], "visa": [], "escrow": [], "compta": [], "__test__": "OK"}


# ----------------------------------------------------
# SAVE JSON
# ----------------------------------------------------
def save_database(data):
    """Convertit en JSON et sauvegarde dans Dropbox."""
    dbx = get_dbx()

    safe_data = json_safe(data)

    dbx.files_upload(
        json.dumps(safe_data, indent=2).encode("utf-8"),
        JSON_PATH,
        mode=dropbox.files.WriteMode("overwrite")
    )
