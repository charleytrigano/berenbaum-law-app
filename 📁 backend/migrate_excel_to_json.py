import json
import tempfile
import pandas as pd
import dropbox
from utils.config import DROPBOX_TOKEN, DROPBOX_EXCEL_PATH, DROPBOX_JSON_PATH


def migrate_all_sheets_to_json():
    print("🔄 Migration Excel → JSON en cours…")

    dbx = dropbox.Dropbox(DROPBOX_TOKEN)

    # 1️⃣ Télécharger Excel
    print("📥 Téléchargement de l'Excel...")
    _, res = dbx.files_download(DROPBOX_EXCEL_PATH)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        tmp.write(res.content)
        excel_path = tmp.name

    # 2️⃣ Charger toutes les feuilles
    print("📄 Lecture des feuilles...")
    xls = pd.ExcelFile(excel_path)

    json_data = {}

    # Liste des feuilles attendues
    mapping = {
        "Clients": "clients",
        "Visa": "visa",
        "Escrow": "escrow",
        "ComptaCli": "comptacli"
    }

    for sheet_excel_name, json_key_name in mapping.items():
        if sheet_excel_name not in xls.sheet_names:
            print(f"⚠️ Feuille manquante dans Excel : {sheet_excel_name}")
            json_data[json_key_name] = []
            continue

        print(f"✔ Conversion : {sheet_excel_name} → {json_key_name}")

        df = pd.read_excel(xls, sheet_excel_name)
        df = df.fillna("")  # nettoyer valeurs NaN

        json_data[json_key_name] = df.to_dict(orient="records")

    # 3️⃣ Upload du nouveau JSON
    print("📤 Upload du JSON...")
    dbx.files_upload(
        json.dumps(json_data, indent=4).encode("utf-8"),
        DROPBOX_JSON_PATH,
        mode=dropbox.files.WriteMode("overwrite")
    )

    print("✅ Migration terminée ! Votre base JSON est prête.")
    return json_data
