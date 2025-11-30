import streamlit as st
import pandas as pd
from utils.dropbox_utils import dropbox_download, dropbox_upload_json
import json

st.set_page_config(page_title="Import Excel", page_icon="📥")

st.title("📥 Import Excel → JSON (Dropbox)")

# ---------------------------------------------------------
# Chargement des chemins
# ---------------------------------------------------------
try:
    CLIENTS_PATH = st.secrets["paths"]["CLIENTS_FILE"]
    ESCROW_PATH = st.secrets["paths"]["ESCROW_FILE"]
    VISA_PATH = st.secrets["paths"]["VISA_FILE"]
    COMPTA_PATH = st.secrets["paths"]["COMPTA_FILE"]
    JSON_PATH = st.secrets["paths"]["DROPBOX_JSON"]
except Exception as e:
    st.error(f"❌ Erreur lecture secrets.toml : {e}")
    st.stop()

# ---------------------------------------------------------
# Fonction sécurisée
# ---------------------------------------------------------
def safe_xlsx_load(path):
    try:
        file_bytes = dropbox_download(path)
        return pd.ExcelFile(file_bytes)
    except Exception as e:
        st.error(f"❌ Impossible lire : {path} — {e}")
        return None

# ---------------------------------------------------------
# Importation des fichiers
# ---------------------------------------------------------
st.header("📄 Lecture des fichiers Excel")

xls_clients = safe_xlsx_load(CLIENTS_PATH)
xls_escrow = safe_xlsx_load(ESCROW_PATH)
xls_visa = safe_xlsx_load(VISA_PATH)
xls_compta = safe_xlsx_load(COMPTA_PATH)

# ---------------------------------------------------------
# Conversion → JSON
# ---------------------------------------------------------
st.header("🔄 Conversion Excel → JSON")

db = {"clients": [], "visa": [], "escrow": [], "compta": []}

if xls_clients and "Clients" in xls_clients.sheet_names:
    st.success("Clients → OK")
    db["clients"] = pd.read_excel(xls_clients, "Clients").fillna("").to_dict(orient="records")
else:
    st.warning("⚠ Feuille 'Clients' absente ou introuvable.")

if xls_visa and "Visa" in xls_visa.sheet_names:
    st.success("Visa → OK")
    db["visa"] = pd.read_excel(xls_visa, "Visa").fillna("").to_dict(orient="records")
else:
    st.warning("⚠ Feuille 'Visa' absente ou introuvable.")

if xls_escrow and "Escrow" in xls_escrow.sheet_names:
    st.success("Escrow → OK")
    db["escrow"] = pd.read_excel(xls_escrow, "Escrow").fillna("").to_dict(orient="records")
else:
    st.warning("⚠ Feuille 'Escrow' absente ou introuvable.")

if xls_compta and "ComptaCli" in xls_compta.sheet_names:
    st.success("ComptaCli → OK")
    db["compta"] = pd.read_excel(xls_compta, "ComptaCli").fillna("").to_dict(orient="records")
else:
    st.warning("⚠ Feuille 'ComptaCli' absente ou introuvable.")

# ---------------------------------------------------------
# SAUVEGARDE JSON Dropbox
# ---------------------------------------------------------
st.header("💾 Sauvegarde JSON dans Dropbox")

try:
    dropbox_upload_json(JSON_PATH, db)
    st.success("✔ Base JSON mise à jour dans Dropbox")
except Exception as e:
    st.error(f"❌ Erreur écriture JSON : {e}")

st.success("🎉 Import terminé")
