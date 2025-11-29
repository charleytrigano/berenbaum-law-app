import streamlit as st
import pandas as pd
import json
import dropbox

# -------------------------------------------------------
#  CONNECT TO DROPBOX
# -------------------------------------------------------
TOKEN = st.secrets["dropbox"]["DROPBOX_TOKEN"]
EXCEL_PATH = st.secrets["paths"]["EXCEL_FILE_PATH"]
JSON_PATH = st.secrets["paths"]["DROPBOX_FILE_PATH"]

dbx = dropbox.Dropbox(TOKEN)

st.title("📥 Importer Excel → Base JSON Dropbox")
st.write("Convertit automatiquement les 4 feuilles vers database.json.")


# -------------------------------------------------------
# LOAD EXCEL FROM DROPBOX
# -------------------------------------------------------
@st.cache_data
def load_excel_from_dropbox():
    try:
        metadata, res = dbx.files_download(EXCEL_PATH)
        return pd.ExcelFile(res.content)
    except Exception as e:
        st.error(f"Erreur lors du chargement de l’Excel : {e}")
        return None


xls = load_excel_from_dropbox()

if xls is None:
    st.stop()

st.success("Excel chargé depuis Dropbox ✔")


# -------------------------------------------------------
# CLEAN FUNCTION
# -------------------------------------------------------
def clean_value(x):
    """Convertit NaN, None, et formats Excel en JSON valide."""
    if pd.isna(x):
        return ""
    if isinstance(x, (pd.Timestamp)):
        return str(x.date())
    if isinstance(x, float):
        # si float sans décimales → convertir en int (ex: 12001)
        return int(x) if x.is_integer() else float(x)
    return str(x)


# -------------------------------------------------------
# IMPORT CLIENTS
# -------------------------------------------------------
if "Clients" in xls.sheet_names:
    df_clients = xls.parse("Clients")
    df_clients = df_clients.fillna("")

    clients_list = [
        {col: clean_value(row[col]) for col in df_clients.columns}
        for _, row in df_clients.iterrows()
    ]
else:
    clients_list = []


# -------------------------------------------------------
# IMPORT VISA
# -------------------------------------------------------
if "Visa" in xls.sheet_names:
    df_visa = xls.parse("Visa").fillna("")
    visa_list = [
        {col: clean_value(row[col]) for col in df_visa.columns}
        for _, row in df_visa.iterrows()
    ]
else:
    visa_list = []


# -------------------------------------------------------
# IMPORT ESCROW
# -------------------------------------------------------
if "Escrow" in xls.sheet_names:
    df_escrow = xls.parse("Escrow").fillna("")
    escrow_list = [
        {col: clean_value(row[col]) for col in df_escrow.columns}
        for _, row in df_escrow.iterrows()
    ]
else:
    escrow_list = []


# -------------------------------------------------------
# IMPORT COMPTABILITE
# -------------------------------------------------------
if "ComptaCli" in xls.sheet_names:
    df_compta = xls.parse("ComptaCli").fillna("")
    compta_list = [
        {col: clean_value(row[col]) for col in df_compta.columns}
        for _, row in df_compta.iterrows()
    ]
else:
    compta_list = []


# -------------------------------------------------------
# CREATE FINAL JSON STRUCTURE
# -------------------------------------------------------
final_json = {
    "clients": clients_list,
    "visa": visa_list,
    "escrow": escrow_list,
    "compta": compta_list
}


# -------------------------------------------------------
# SAVE TO DROPBOX JSON
# -------------------------------------------------------
if st.button("🚀 Importer maintenant dans database.json"):

    try:
        dbx.files_upload(
            json.dumps(final_json, indent=2).encode("utf-8"),
            JSON_PATH,
            mode=dropbox.files.WriteMode("overwrite")
        )
        st.success("Base JSON mise à jour avec succès ✔")
        st.balloons()

    except Exception as e:
        st.error(f"Erreur d’écriture Dropbox : {e}")
