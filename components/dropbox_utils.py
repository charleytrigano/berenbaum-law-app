import dropbox
import streamlit as st

# Connexion à Dropbox
def get_dbx():
    return dropbox.Dropbox(st.secrets["DROPBOX_TOKEN"])

# Upload
def upload_to_dropbox(file, dropbox_path):
    dbx = get_dbx()
    dbx.files_upload(file.read(), dropbox_path, mode=dropbox.files.WriteMode("overwrite"))
    return True

# Download
def download_from_dropbox(dropbox_path):
    dbx = get_dbx()
    meta, res = dbx.files_download(dropbox_path)
    return res.content

# List files
def list_files(folder="/"):
    dbx = get_dbx()
    items = dbx.files_list_folder(folder).entries
    return [item.name for item in items]
