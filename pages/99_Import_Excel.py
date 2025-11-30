import streamlit as st
import pandas as pd
from backend.dropbox_utils import dropbox_client, save_database, load_database

st.set_page_config(page_title="Importer Excel → JSON", page_icon="🔄")

st.title("🔄 Import Excel → Base JSON (Dropbox)")
st.write("Cette page permet d'importer automatiquement les fichiers Excel pour mettre à jour la base JSON.")

# -----------------------------
# Charger chemins depuis secrets
# -----------------------------
PATH_CLIENTS = st.secrets["paths"]["CLIENTS_FILE"]
PATH_ESCROW = st.secrets["paths"]["ESCROW_FILE"]
PATH_VISA = st.secrets["paths"]["VISA_FILE"]
PATH_COMPTA = st.secrets["paths"]["COMPTA_FILE"]

dbx = dropbox_client()

def read_excel_from_dropbox(path):
    """Téléchargement + lecture Excel."""
    try:
        md, res = dbx.files_download(path)
        return pd.ExcelFile(res.content)
    except Exception as e:
        st.error(f"❌ Erreur lecture fichier : {path} — {e}")
        return None


# -----------------------------
# IMPORT
# -----------------------------
if st.button("🚀 Importer les 4 fichiers Excel maintenant"):

    db = {"clients": [], "visa": [], "escrow": [], "compta": []}

    st.subheader("📥 Lecture des fichiers Excel")

    # === Clients ===
    xls_clients = read_excel_from_dropbox(PATH_CLIENTS)
    if xls_clients and "Clients" in xls_clients.sheet_names:
        df = pd.read_excel(xls_clients, "Clients")
        db["clients"] = df.fillna("").to_dict(orient="records")
        st.success("✔ Clients importés")
    else:
        st.warning("⚠ La feuille 'Clients' est absente dans Excel.")

    # === Visa ===
    xls_visa = read_excel_from_dropbox(PATH_VISA)
    if xls_visa and "Visa" in xls_visa.sheet_names:
        df = pd.read_excel(xls_visa, "Visa")
        db["visa"] = df.fillna("").to_dict(orient="records")
        st.success("✔ Visa importés")
    else:
        st.warning("⚠ La feuille 'Visa' est absente dans Excel.")

    # === Escrow ===
    xls_escrow = read_excel_from_dropbox(PATH_ESCROW)
    if xls_escrow and "Escrow" in xls_escrow.sheet_names:
        df = pd.read_excel(xls_escrow, "Escrow")
        db["escrow"] = df.fillna("").to_dict(orient="records")
        st.success("✔ Escrow importé")
    else:
        st.warning("⚠ La feuille 'Escrow' est absente dans Excel.")

    # === Compta ===
    xls_compta = read_excel_from_dropbox(PATH_COMPTA)
    if xls_compta and "ComptaCli" in xls_compta.sheet_names:
        df = pd.read_excel(xls_compta, "ComptaCli")
        db["compta"] = df.fillna("").to_dict(orient="records")
        st.success("✔ Compta importée")
    else:
        st.warning("⚠ La feuille 'ComptaCli' est absente dans Excel.")

    # -----------------------------
    # Écriture JSON
    # -----------------------------
    save_database(db)

    st.success("🎉 Import terminé et base JSON mise à jour !")
    st.balloons()


# -----------------------------
# Aperçu JSON actuel
# -----------------------------
st.subheader("📦 Contenu actuel du JSON Dropbox")
st.json(load_database())
