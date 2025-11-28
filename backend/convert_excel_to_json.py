import json
import tempfile
import pandas as pd
import dropbox
from utils.config import DROPBOX_TOKEN, DROPBOX_EXCEL_PATH, DROPBOX_JSON_PATH

def convert_excel_to_json():
    print("🔄 Conversion Excel → JSON...")

    # Connexion Dropbox
    dbx = dropbox.Dropbox(DROPBOX_TOKEN)

    # 1) Télécharger le fichier Excel temporairement
    print("📥 Téléchargement du fichier Excel depuis Dropbox...")
    _, res = dbx.files_download(DROPBOX_EXCEL_PATH)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        tmp.write(res.content)
        excel_path = tmp.name

    # 2) Charger l’Excel avec Pandas
    print("📄 Lecture du fichier Excel...")
    df = pd.read_excel(excel_path)

    # 3) Convertir en format JSON structurel
    json_data = {
        "clients": df.to_dict(orient="records")
    }

    # 4) Upload du JSON dans Dropbox
    print("📤 Upload du JSON vers Dropbox...")
    dbx.files_upload(
        json.dumps(json_data, indent=4).encode(),
        DROPBOX_JSON_PATH,
        mode=dropbox.files.WriteMode("overwrite")
    )

    print("✅ Conversion terminée : JSON mis à jour dans Dropbox !")

