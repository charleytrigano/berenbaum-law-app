import json
from components.dropbox_utils import download_from_dropbox, upload_bytes_to_dropbox

DB_PATH = "/berenbaum/database.json"

def initialize_database():
    default_db = {
        "clients": [],
        "dossiers": [],
        "documents": [],
        "notes": [],
    }
    save_database(default_db)
    return default_db

def load_database():
    try:
        content = download_from_dropbox(DB_PATH)
        return json.loads(content.decode("utf-8"))
    except Exception:
        return initialize_database()

def save_database(db):
    json_bytes = json.dumps(db, indent=2).encode("utf-8")
    upload_bytes_to_dropbox(json_bytes, DB_PATH)
