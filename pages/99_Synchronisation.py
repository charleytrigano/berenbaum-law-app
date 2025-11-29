import streamlit as st
import pandas as pd
import json
import dropbox

# ============================================================
# CONFIG
# ============================================================
TOKEN = st.secrets["dropbox"]["DROPBOX_TOKEN"]

PATH_CLIENTS = st.secrets["paths"]["CLIENTS_FILE"]
PATH_ESCROW = st.secrets["paths"]["ESCROW_FILE"]
PATH_VISA = st.secrets["paths"]["VISA_FILE"]
PATH_COMPTA = st.secrets["paths"]["COMPTA_FILE"]
JSON_PATH = st.secrets["paths"]["DROPBOX_JSON"]

dbx = dropbox.Dropbox(TOKEN)

st.set_page_config(page_title="🔄 Synchronisation", layout="wide")
st.title("🔄 Synchronisation Excel ↔ JSON (Dropbox)")

# ============================================================
# UTILS
# ============================================================
def dl_excel(path):
    """Télécharge un fichier Excel depuis Dropbox."""
    try:
        meta, res = dbx.files_download(path)
        df = pd.read_excel(res.content)
        st.success(f"✔ Fichier chargé : {path}")
        return df
    except Exception as e:
        st.error(f"❌ Impossible de lire {path} : {e}")
        return pd.DataFrame()

def upload_excel(df, path):
    """Uploader un DataFrame en Excel vers Dropbox."""
    try:
        excel_bytes = df.to_excel(index=False, engine="openpyxl")
    except:
        import io
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        excel_bytes = buffer.getvalue()

    dbx.files_upload(excel_bytes, path, mode=dropbox.files.WriteMode("overwrite"))
    st.success(f"✔ Uploadé : {path}")

def load_json():
    """Télécharge le JSON depuis Dropbox."""
    try:
        _, res = dbx.files_download(JSON_PATH)
        data = json.loads(res.content.decode())
        st.success("✔ JSON chargé depuis Dropbox")
        return data
    except:
        st.warning("⚠ Aucun JSON existant → nouvelle base créée")
        return {"clients": [], "escrow": [], "visa": [], "compta": []}

def save_json(data):
    """Sauvegarde JSON → Dropbox."""
    dbx.files_upload(
        json.dumps(data, indent=2).encode(),
        JSON_PATH,
        mode=dropbox.files.WriteMode("overwrite"),
    )
    st.success("✔ database.json mis à jour")


# ============================================================
# 1️⃣ IMPORT EXCEL → JSON
# ============================================================
st.header("📥 Importer les fichiers Excel → JSON")

if st.button("Importer Excel → JSON (Dropbox)", type="primary"):

    df_clients = dl_excel(PATH_CLIENTS)
    df_escrow = dl_excel(PATH_ESCROW)
    df_visa = dl_excel(PATH_VISA)
    df_compta = dl_excel(PATH_COMPTA)

    db = {
        "clients": df_clients.to_dict("records"),
        "escrow": df_escrow.to_dict("records"),
        "visa": df_visa.to_dict("records"),
        "compta": df_compta.to_dict("records"),
    }

    save_json(db)
    st.success("🎉 Importation Excel → JSON terminée !")

st.markdown("---")


# ============================================================
# 2️⃣ EXPORT JSON → EXCEL
# ============================================================
st.header("📤 Exporter database.json → Excel")

if st.button("Exporter JSON → Excel (Dropbox)", type="primary"):

    db = load_json()

    upload_excel(pd.DataFrame(db["clients"]), PATH_CLIENTS)
    upload_excel(pd.DataFrame(db["escrow"]), PATH_ESCROW)
    upload_excel(pd.DataFrame(db["visa"]), PATH_VISA)
    upload_excel(pd.DataFrame(db["compta"]), PATH_COMPTA)

    st.success("🎉 Exportation JSON → Excel terminée !")


# ============================================================
# 3️⃣ PREVIEW JSON
# ============================================================
st.markdown("---")
st.header("🧐 Aperçu Database JSON")

db = load_json()
st.json(db, expanded=False)


