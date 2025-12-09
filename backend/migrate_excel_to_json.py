import pandas as pd
import json
from backend.dropbox_utils import get_dbx
import streamlit as st

def read_excel_from_dropbox(path):
    """Télécharge un fichier Excel depuis Dropbox et retourne un DataFrame."""
    dbx = get_dbx()
    try:
        metadata, res = dbx.files_download(path)
        content = res.content
        return pd.read_excel(content)
    except Exception as e:
        st.error(f"❌ Erreur lecture fichier : {path} — {e}")
        return None


def convert_all_excels_to_json():
    """
    Récupère tous les fichiers Excel mentionnés dans st.secrets["paths"]
    et génère un JSON complet.
    """

    p = st.secrets["paths"]

    clients_df = read_excel_from_dropbox(p["CLIENTS_FILE"])
    visa_df = read_excel_from_dropbox(p["VISA_FILE"])
    escrow_df = read_excel_from_dropbox(p["ESCROW_FILE"])
    compta_df = read_excel_from_dropbox(p["COMPTA_FILE"])

    db_json = {
        "clients": [],
        "visa": [],
        "escrow": [],
        "compta": []
    }

    if clients_df is not None:
        db_json["clients"] = clients_df.fillna("").to_dict(orient="records")

    if visa_df is not None:
        db_json["visa"] = visa_df.fillna("").to_dict(orient="records")

    if escrow_df is not None:
        db_json["escrow"] = escrow_df.fillna("").to_dict(orient="records")

    if compta_df is not None:
        db_json["compta"] = compta_df.fillna("").to_dict(orient="records")

    return db_json
