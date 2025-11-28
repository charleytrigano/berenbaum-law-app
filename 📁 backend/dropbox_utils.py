import json
import dropbox
import streamlit as st

DROPBOX_TOKEN = st.secrets["dropbox"]["DROPBOX_TOKEN"]
DROPBOX_FILE_PATH = "/database.json"


def get_dbx():
    return dropbox.Dropbox(DROPBOX_TOKEN)


def load_database():
    dbx = get_dbx()
    try:
        _, res = dbx.files_download(DROPBOX_FILE_PATH)
        data = json.loads(res.content.decode("utf-8"))
        return data
    except Exception:
        empty = {
            "clients": [],
            "visa": [],
            "escrow": [],
            "comptacli": []
        }
        save_database(empty)
        return empty


def save_database(data: dict):
    dbx = get_dbx()
    dbx.files_upload(
        json.dumps(data, indent=4).encode(),
        DROPBOX_FILE_PATH,
        mode=dropbox.files.WriteMode("overwrite")
    )
