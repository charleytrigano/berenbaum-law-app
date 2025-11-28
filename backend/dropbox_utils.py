import json
import dropbox
import streamlit as st
from utils.config import DROPBOX_TOKEN, DROPBOX_FILE_PATH

def _get_dbx():
    """Retourne un client Dropbox authentifié."""
    return dropbox.Dropbox(DROPBOX_TOKEN)

def load_database():
    """Charge le fichier JSON depuis Dropbox."""
    dbx = _get_dbx()

    try:
        metadata, res = dbx.files_download(DROPBOX_FILE_PATH)
        data = json.loads(res.content.decode("utf-8"))
        return data
    except dropbox.exceptions.ApiError:
        # Si le fichier n'existe pas encore → base vide
        return {"clients": []}

def save_database(data):
    """Sauvegarde le JSON dans Dropbox."""
    dbx = _get_dbx()

    dbx.files_upload(
        json.dumps(data, indent=2).encode("utf-8"),
        DROPBOX_FILE_PATH,
        mode=dropbox.files.WriteMode("overwrite")
    )
