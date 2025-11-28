import json
import dropbox
import streamlit as st
from utils.config import DROPBOX_TOKEN, DROPBOX_FILE_PATH


# ---------------------------------------------------------
# 🔹 Charger la base de données depuis Dropbox
# ---------------------------------------------------------
def load_database():
    dbx = dropbox.Dropbox(DROPBOX_TOKEN)

    st.write("📁 Chargement depuis Dropbox :", DROPBOX_FILE_PATH)

    try:
        metadata, res = dbx.files_download(DROPBOX_FILE_PATH)
        data = json.loads(res.content.decode("utf-8"))

        # Sécurité : si la structure n’est pas correcte
        if "clients" not in data:
            data["clients"] = []

        return data

    except dropbox.exceptions.ApiError as e:
        st.error(f"⚠️ Impossible de charger la base depuis Dropbox : {e}")
        return {"clients": []}

    except Exception as e:
        st.error(f"⚠️ Erreur lors du chargement du JSON : {e}")
        return {"clients": []}


# ---------------------------------------------------------
# 🔹 Sauvegarder la base de données dans Dropbox
# ---------------------------------------------------------
def save_database(data):
    dbx = dropbox.Dropbox(DROPBOX_TOKEN)

    try:
        dbx.files_upload(
            json.dumps(data, indent=4).encode("utf-8"),
            DROPBOX_FILE_PATH,
            mode=dropbox.files.WriteMode("overwrite")
        )

        st.success("💾 Base de données sauvegardée dans Dropbox ✔")

    except Exception as e:
        st.error(f"❌ Erreur lors de l’enregistrement dans Dropbox : {e}")
