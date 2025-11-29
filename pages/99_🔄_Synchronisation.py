import streamlit as st
import pandas as pd
import dropbox
import io
from backend.dropbox_utils import load_database, save_database
from utils.config import DROPBOX_TOKEN

# ----------------------------------------------------
# Connexion Dropbox
# ----------------------------------------------------
dbx = dropbox.Dropbox(DROPBOX_TOKEN)

# Emplacements dans Dropbox
EXCEL_FILE = "/Apps/berenbaum-law/data.xlsx"     # FICHIER EXCEL CENTRAL
JSON_FILE = "/Apps/berenbaum-law/database.json"  # JSON DE L’APPLICATION


# ----------------------------------------------------
# Import Excel → JSON
# ----------------------------------------------------
def import_excel_to_json():
    try:
        metadata, res = dbx.files_download(EXCEL_FILE)
        excel_bytes = res.content
        xls = pd.ExcelFile(io.BytesIO(excel_bytes))

        db = {
            "clients": xls.parse("Clients").fillna("").to_dict(orient="records"),
            "visa": xls.parse("Visa").fillna("").to_dict(orient="records"),
            "escrow": xls.parse("Escrow").fillna("").to_dict(orient="records"),
            "compta": xls.parse("ComptaCli").fillna("").to_dict(orient="records"),
        }

        save_database(db)
        return True

    except Exception as e:
        st.error(f"Erreur lors de l’import Excel → JSON : {e}")
        return False


# ----------------------------------------------------
# Export JSON → Excel
# ----------------------------------------------------
def export_json_to_excel():
    try:
        db = load_database()

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            pd.DataFrame(db.get("clients", [])).to_excel(writer, index=False, sheet_name="Clients")
            pd.DataFrame(db.get("visa", [])).to_excel(writer, index=False, sheet_name="Visa")
            pd.DataFrame(db.get("escrow", [])).to_excel(writer, index=False, sheet_name="Escrow")
            pd.DataFrame(db.get("compta", [])).to_excel(writer, index=False, sheet_name="ComptaCli")

        dbx.files_upload(
            output.getvalue(),
            EXCEL_FILE,
            mode=dropbox.files.WriteMode("overwrite")
        )

        return True

    except Exception as e:
        st.error(f"Erreur lors de l’export JSON → Excel : {e}")
        return False


# ----------------------------------------------------
# PAGE UI
# ----------------------------------------------------
st.title("🔄 Synchronisation des données")
st.write("Synchronisez Excel ↔ JSON pour garder toutes les données à jour.")

st.markdown("---")

# ===================== IMPORT =====================

st.header("📥 Importer Excel → Base JSON")
st.write("Met à jour la base de données de l’application à partir du fichier Excel Dropbox.")

if st.button("📥 Importer depuis Excel", type="primary"):
    if import_excel_to_json():
        st.success("✔ Import Excel → JSON réussi !")
        st.balloons()

st.markdown("---")

# ===================== EXPORT =====================

st.header("📤 Exporter Base JSON → Excel")
st.write("Met à jour le fichier Excel Dropbox à partir de la base JSON courante.")

if st.button("📤 Exporter vers Excel", type="secondary"):
    if export_json_to_excel():
        st.success("✔ Export JSON → Excel réussi !")
        st.balloons()

