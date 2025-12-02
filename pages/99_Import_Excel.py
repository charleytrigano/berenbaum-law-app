import streamlit as st
import pandas as pd
import dropbox
import requests

from backend.dropbox_utils import load_database, save_database


# --------------------------------------------------------
# CLEAN VISA DF
# --------------------------------------------------------
def clean_visa_df(dfv):
    if dfv is None or dfv.empty:
        return pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

    rename_map = {}
    for col in dfv.columns:
        col_clean = (
            col.lower()
            .replace("é", "e")
            .replace("è", "e")
            .strip()
        )

        if col_clean in ["categories", "categorie"]:
            rename_map[col] = "Categories"
        elif col_clean in ["sous-categories", "sous-categorie"]:
            rename_map[col] = "Sous-categories"
        elif col_clean == "visa":
            rename_map[col] = "Visa"

    dfv = dfv.rename(columns=rename_map)

    # Supprimer anciennes colonnes erronées
    for old in ["Catégories", "Sous-catégories"]:
        if old in dfv.columns:
            dfv = dfv.drop(columns=[old])

    # Colonnes garanties
    for c in ["Categories", "Sous-categories", "Visa"]:
        if c not in dfv.columns:
            dfv[c] = ""

    return dfv


# --------------------------------------------------------
# CONFIG – chemins fichiers Excel dans Dropbox
# --------------------------------------------------------
TOKEN = st.secrets["dropbox"]["DROPBOX_TOKEN"]
APP_KEY = st.secrets["dropbox"]["APP_KEY"]
APP_SECRET = st.secrets["dropbox"]["APP_SECRET"]

PATH_CLIENTS = st.secrets["paths"]["CLIENTS_FILE"]
PATH_ESCROW = st.secrets["paths"]["ESCROW_FILE"]
PATH_VISA = st.secrets["paths"]["VISA_FILE"]
PATH_COMPTA = st.secrets["paths"]["COMPTA_FILE"]


# --------------------------------------------------------
# Téléchargement fichier depuis Dropbox
# --------------------------------------------------------
def read_excel_from_dropbox(path):
    try:
        # 1) Obtenir access_token depuis refresh_token
        resp = requests.post(
            "https://api.dropbox.com/oauth2/token",
            data={
                "refresh_token": TOKEN,
                "client_id": APP_KEY,
                "client_secret": APP_SECRET,
                "grant_type": "refresh_token",
            },
        )
        access_token = resp.json()["access_token"]

        # 2) Connexion Dropbox
        dbx = dropbox.Dropbox(access_token)

        # 3) Téléchargement fichier
        metadata, res = dbx.files_download(path)

        return pd.read_excel(res.content)

    except Exception as e:
        st.error(f"❌ Erreur lecture fichier : {path} — {e}")
        return None


# --------------------------------------------------------
# Normalisation JSON
# --------------------------------------------------------
def normalize_record(record):
    import numpy as np

    out = {}
    for k, v in record.items():

        # Dates
        if isinstance(v, pd.Timestamp):
            out[k] = v.strftime("%Y-%m-%d")
        # Numpy types
        elif hasattr(v, "item"):
            out[k] = v.item()
        # None → vide
        elif v is None:
            out[k] = ""
        # Types natifs OK
        elif isinstance(v, (int, float, str, bool)):
            out[k] = v
        # Fallback
        else:
            out[k] = str(v)

    return out


# ========================================================
# 🖥️ UI STREAMLIT
# ========================================================

st.title("🔄 Import Excel → Base JSON (Dropbox)")
st.write("Cette page importe automatiquement les fichiers Excel pour mettre à jour la base JSON.")


# --------------------------------------------------------
# Affichage JSON actuel
# --------------------------------------------------------
db = load_database()

st.subheader("📦 Contenu actuel du JSON Dropbox")
st.json(db)


# --------------------------------------------------------
# Bouton Import
# --------------------------------------------------------
if st.button("🚀 Importer les 4 fichiers Excel maintenant", type="primary"):

    st.subheader("📥 Lecture des fichiers Excel")

    df_clients = read_excel_from_dropbox(PATH_CLIENTS)
    df_visa_raw = read_excel_from_dropbox(PATH_VISA)
    df_visa = clean_visa_df(df_visa_raw)

    df_escrow = read_excel_from_dropbox(PATH_ESCROW)
    df_compta = read_excel_from_dropbox(PATH_COMPTA)

    # ----------- CLIENTS -----------
    db["clients"] = [] if df_clients is None else [
        normalize_record(r) for _, r in df_clients.iterrows()
    ]
    st.success("✔ Clients importés")

    # ----------- VISA -----------
    db["visa"] = [] if df_visa is None else [
        normalize_record(r) for _, r in df_visa.iterrows()
    ]
    st.success("✔ Visa importés")

    # ----------- ESCROW -----------
    db["escrow"] = [] if df_escrow is None else [
        normalize_record(r) for _, r in df_escrow.iterrows()
    ]
    st.success("✔ Escrow importé")

    # ----------- COMPTA -----------
    db["compta"] = [] if df_compta is None else [
        normalize_record(r) for _, r in df_compta.iterrows()
    ]
    st.success("✔ Compta importée")

    # ----------- ENREGISTREMENT -----------
    save_database(db)

    st.success("🎉 Mise à jour JSON terminée et synchronisée dans Dropbox ✔")
    st.balloons()
