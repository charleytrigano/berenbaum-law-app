import streamlit as st
import pandas as pd
import json
import dropbox
import requests
from backend.dropbox_utils import load_database, save_database
from utils.visa_filters import clean_visa_df


st.set_page_config(page_title="Import Excel", page_icon="🔄", layout="wide")

st.title("🔄 Import Excel → Mise à jour JSON (Dropbox)")
st.write("Recharge tous les fichiers Excel et reconstruit le fichier JSON.")

# --------------------------------------------------------
# CHARGER LES SECRETS
# --------------------------------------------------------
TOKEN = st.secrets["dropbox"]["DROPBOX_TOKEN"]
APP_KEY = st.secrets["dropbox"]["APP_KEY"]
APP_SECRET = st.secrets["dropbox"]["APP_SECRET"]

PATH_CLIENTS = st.secrets["paths"]["CLIENTS_FILE"]
PATH_ESCROW = st.secrets["paths"]["ESCROW_FILE"]
PATH_VISA = st.secrets["paths"]["VISA_FILE"]
PATH_COMPTA = st.secrets["paths"]["COMPTA_FILE"]
PATH_JSON = st.secrets["paths"]["DROPBOX_JSON"]

# --------------------------------------------------------
# OBTENIR ACCESS TOKEN à partir du REFRESH TOKEN
# --------------------------------------------------------
def get_access_token():
    resp = requests.post(
        "https://api.dropbox.com/oauth2/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": TOKEN,
            "client_id": APP_KEY,
            "client_secret": APP_SECRET,
        },
    )
    return resp.json().get("access_token")


# --------------------------------------------------------
# TÉLÉCHARGER UN EXCEL DE DROPBOX
# --------------------------------------------------------
def download_excel(path):
    try:
        access_token = get_access_token()
        dbx = dropbox.Dropbox(access_token)

        meta, res = dbx.files_download(path)

        df = pd.read_excel(res.content)
        return df

    except Exception as e:
        st.error(f"❌ Erreur lecture fichier : {path}\n{e}")
        return None


# --------------------------------------------------------
# NORMALISATION JSON
# --------------------------------------------------------
def normalize_record(record):
    out = {}
    for k, v in record.items():
        if isinstance(v, pd.Timestamp):
            out[k] = v.strftime("%Y-%m-%d")
        elif pd.isna(v):
            out[k] = ""
        else:
            out[k] = v
    return out


# --------------------------------------------------------
# UI
# --------------------------------------------------------
st.subheader("📦 Contenu actuel du JSON")
st.json(load_database())


# --------------------------------------------------------
# BOUTON IMPORT
# --------------------------------------------------------
if st.button("🚀 Lancer l'import complet", type="primary"):
    
    st.info("📥 Lecture fichiers Excel…")

    df_clients = download_excel(PATH_CLIENTS)
    df_visa = download_excel(PATH_VISA)
    df_escrow = download_excel(PATH_ESCROW)
    df_compta = download_excel(PATH_COMPTA)

    st.success("✔ Fichiers Excel téléchargés")

    st.write("Clients :", df_clients)
    st.write("Visa :", df_visa)
    st.write("Escrow :", df_escrow)
    st.write("Compta :", df_compta)

    # Nettoyage Visa
    df_visa = clean_visa_df(df_visa)

    # Reconstruction JSON
    db = {
        "clients": [] if df_clients is None else [normalize_record(r) for _, r in df_clients.iterrows()],
        "visa":    [] if df_visa is None else    [normalize_record(r) for _, r in df_visa.iterrows()],
        "escrow":  [] if df_escrow is None else  [normalize_record(r) for _, r in df_escrow.iterrows()],
        "compta":  [] if df_compta is None else  [normalize_record(r) for _, r in df_compta.iterrows()],
    }

    st.subheader("🧩 JSON généré")
    st.json(db)

    save_database(db)

    st.success("🎉 JSON Dropbox mis à jour avec succès !")
    st.balloons()
