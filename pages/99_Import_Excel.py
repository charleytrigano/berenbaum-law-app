import streamlit as st
import pandas as pd
import json
import dropbox

# === Chargement config Dropbox ===
TOKEN = st.secrets["dropbox"]["DROPBOX_TOKEN"]

PATH_CLIENTS = st.secrets["paths"]["CLIENTS_FILE"]
PATH_ESCROW = st.secrets["paths"]["ESCROW_FILE"]
PATH_VISA = st.secrets["paths"]["VISA_FILE"]
PATH_COMPTA = st.secrets["paths"]["COMPTA_FILE"]

JSON_PATH = st.secrets["paths"]["DROPBOX_JSON"]

dbx = dropbox.Dropbox(TOKEN)


def read_xlsx(path):
    """Télécharge un fichier Excel depuis Dropbox et retourne un DataFrame."""
    try:
        metadata, res = dbx.files_download(path)
        df = pd.read_excel(res.content)
        st.success(f"✔ Chargé : {path}")
        return df
    except Exception as e:
        st.error(f"❌ Erreur lecture fichier : {path} — {e}")
        return pd.DataFrame()


def save_json(data):
    """Sauvegarde du JSON final dans Dropbox."""
    dbx.files_upload(
        json.dumps(data, indent=2).encode(),
        JSON_PATH,
        mode=dropbox.files.WriteMode("overwrite")
    )
    st.success("✔ Base JSON sauvegardée dans Dropbox")


st.title("📥 Import Excel → JSON (Dropbox)")

# === 1) Import des fichiers Excel ===

df_clients = read_xlsx(PATH_CLIENTS)
df_escrow = read_xlsx(PATH_ESCROW)
df_visa = read_xlsx(PATH_VISA)
df_compta = read_xlsx(PATH_COMPTA)

# === 2) Conversion en dictionnaires ===

database = {
    "clients": df_clients.to_dict(orient="records"),
    "escrow": df_escrow.to_dict(orient="records"),
    "visa": df_visa.to_dict(orient="records"),
    "compta": df_compta.to_dict(orient="records")
}

# === 3) Sauvegarde JSON ===

if st.button("📤 Générer et envoyer database.json"):
    save_json(database)
