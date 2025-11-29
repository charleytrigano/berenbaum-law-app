import streamlit as st
import pandas as pd
import dropbox
import io

DROPBOX_TOKEN = st.secrets["dropbox"]["DROPBOX_TOKEN"]
EXCEL_PATH = st.secrets["paths"]["EXCEL_FILE_PATH"]
JSON_PATH = st.secrets["paths"]["DROPBOX_FILE_PATH"]

dbx = dropbox.Dropbox(DROPBOX_TOKEN)

EXCEL_PATH = st.secrets["paths"]["EXCEL_FILE_PATH"]
JSON_PATH = st.secrets["paths"]["DROPBOX_FILE_PATH"]

# ---------------------------------------------------------
# CLIENT DROPBOX
# ---------------------------------------------------------
dbx = dropbox.Dropbox(DROPBOX_TOKEN)

st.title("📥 Import Excel → Base Dropbox")
st.write("Synchroniser votre fichier Excel avec la base de données JSON Dropbox.")


# ---------------------------------------------------------
# CHARGEMENT FICHIER EXCEL DEPUIS DROPBOX
# ---------------------------------------------------------
def load_excel_from_dropbox():
    try:
        metadata, res = dbx.files_download(EXCEL_PATH)
        excel_bytes = res.content
        return pd.ExcelFile(io.BytesIO(excel_bytes))
    except Exception as e:
        st.error(f"❌ Impossible de télécharger le fichier Excel : {e}")
        return None


# ---------------------------------------------------------
# SAUVEGARDER JSON DANS DROPBOX
# ---------------------------------------------------------
def save_json_to_dropbox(data):
    try:
        dbx.files_upload(
            json.dumps(data, indent=2).encode("utf-8"),
            JSON_PATH,
            mode=dropbox.files.WriteMode("overwrite")
        )
        st.success("✔ Base mise à jour dans Dropbox !")
    except Exception as e:
        st.error(f"❌ Erreur lors de la sauvegarde du JSON : {e}")


# ---------------------------------------------------------
# LECTURE DU FICHIER EXCEL
# ---------------------------------------------------------
st.subheader("📄 Lecture du fichier Excel")

xls = load_excel_from_dropbox()

if xls is None:
    st.stop()

st.success("✔ Fichier Excel chargé depuis Dropbox")


# ---------------------------------------------------------
# LECTURE DES FEUILLES
# ---------------------------------------------------------
def read_sheet(name):
    if name in xls.sheet_names:
        return pd.read_excel(xls, sheet_name=name).fillna("")
    else:
        st.warning(f"⚠ La feuille '{name}' est absente dans Excel.")
        return pd.DataFrame()


df_clients = read_sheet("Clients")
df_visa = read_sheet("Visa")
df_escrow = read_sheet("Escrow")
df_compta = read_sheet("ComptaCli")


# ---------------------------------------------------------
# PREVIEW
# ---------------------------------------------------------
st.subheader("👀 Aperçu des données importées")

tabs = st.tabs(["Clients", "Visa", "Escrow", "Compta"])

with tabs[0]:
    st.dataframe(df_clients, use_container_width=True, height=300)

with tabs[1]:
    st.dataframe(df_visa, use_container_width=True, height=300)

with tabs[2]:
    st.dataframe(df_escrow, use_container_width=True, height=300)

with tabs[3]:
    st.dataframe(df_compta, use_container_width=True, height=300)


# ---------------------------------------------------------
# CONVERTIR EN JSON
# ---------------------------------------------------------
st.subheader("🔄 Conversion Excel → JSON Dropbox")

def df_to_list(df):
    return df.to_dict(orient="records") if not df.empty else []


database = {
    "clients": df_to_list(df_clients),
    "visa": df_to_list(df_visa),
    "escrow": df_to_list(df_escrow),
    "compta": df_to_list(df_compta)
}

if st.button("📤 Importer et mettre à jour la base Dropbox", type="primary"):
    save_json_to_dropbox(database)
    st.balloons()
