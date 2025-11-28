import json
import tempfile
import pandas as pd
import dropbox
from utils.config import DROPBOX_TOKEN, DROPBOX_EXCEL_PATH, DROPBOX_JSON_PATH


def migrate_all_sheets_to_json():
    print("🔄 Migration complète Excel → JSON…")

    # Connexion Dropbox
    dbx = dropbox.Dropbox(DROPBOX_TOKEN)

    # ============================
    # 1) Télécharger le fichier Excel
    # ============================
    print(f"📥 Téléchargement de : {DROPBOX_EXCEL_PATH}")

    _, res = dbx.files_download(DROPBOX_EXCEL_PATH)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        tmp.write(res.content)
        excel_path = tmp.name

    # ============================
    # 2) Lire TOUTES les feuilles
    # ============================
    print("📄 Lecture des feuilles Excel…")

    xls = pd.ExcelFile(excel_path)
    sheet_names = xls.sheet_names

    print(f"📚 Feuilles détectées : {sheet_names}")

    json_data = {}

    # Conversion automatique feuille → JSON
    for sheet in sheet_names:
        try:
            df = pd.read_excel(xls, sheet)
            # nettoyage éventuel : remplacer NaN par ""
            df = df.fillna("")
            json_data[sheet.lower()] = df.to_dict(orient="records")
            print(f"✔ Feuille convertie : {sheet}")
        except Exception as e:
            print(f"❌ Erreur sur la feuille {sheet} : {e}")

    # ============================
    # 3) Sauvegarde dans Dropbox
    # ============================
    print("📤 Upload du fichier JSON résultant…")

    dbx.files_upload(
        json.dumps(json_data, indent=4).encode(),
        DROPBOX_JSON_PATH,
        mode=dropbox.files.WriteMode("overwrite")
    )

    print("✅ Migration terminée : base JSON opérationnelle !")
    return json_data
