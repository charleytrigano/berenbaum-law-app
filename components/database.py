import json
from components.dropbox_utils import download_from_dropbox, upload_bytes_to_dropbox

DB_PATH = "Apps/berenbaum/database.json"

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

