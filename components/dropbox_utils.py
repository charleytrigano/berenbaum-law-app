import dropbox
import streamlit as st

def get_dbx():
    return dropbox.Dropbox(st.secrets["DROPBOX_TOKEN"])

def upload_bytes_to_dropbox(content: bytes, dropbox_path: str):
    dbx = get_dbx()
    dbx.files_upload(content, dropbox_path, mode=dropbox.files.WriteMode("overwrite"))

def upload_file_to_dropbox(file, dropbox_path):    
    dbx = get_dbx()
    dbx.files_upload(file.read(), dropbox_path, mode=dropbox.files.WriteMode("overwrite"))

def download_from_dropbox(dropbox_path):
    dbx = get_dbx()
    _, res = dbx.files_download(dropbox_path)
    return res.content

def list_folder(dropbox_path="/"):
    dbx = get_dbx()
    items = dbx.files_list_folder(dropbox_path).entries
    return [item.name for item in items]
