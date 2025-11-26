import json
import pandas as pd
from components.dropbox_utils import download_from_dropbox, upload_bytes_to_dropbox

DB_PATH = "/berenbaum/database.json"

# ----------------------------------------------
# CHARGEMENT / SAUVEGARDE DE LA BASE
# ----------------------------------------------

def initialize_database():
    default = {
        "Escrow": [],
        "Visa": [],
        "ComptaCli": [],
        "Clients": [],
        "Dossiers": [],
        "Documents": []
    }
    save_database(default)
    return default

def load_database():
    """Charge database.json depuis Dropbox."""
    try:
        content = download_from_dropbox(DB_PATH)
        return json.loads(content.decode("utf-8"))
    except Exception:
        return initialize_database()

def save_database(db):
    """Sauvegarde database.json dans Dropbox."""
    content = json.dumps(db, indent=2).encode("utf-8")
    upload_bytes_to_dropbox(content, DB_PATH)


# ----------------------------------------------
# UTILITAIRES DE TABLES
# ----------------------------------------------

def get_table(table_name: str) -> pd.DataFrame:
    db = load_database()
    if table_name not in db:
        raise Exception(f"Table {table_name} introuvable.")
    return pd.DataFrame(db[table_name])


def save_table(table_name: str, df: pd.DataFrame):
    db = load_database()
    db[table_name] = df.to_dict(orient="records")
    save_database(db)


# ----------------------------------------------
# LECTURE D'UNE "FEUILLE"
# ----------------------------------------------

def load_sheet(sheet_name: str) -> pd.DataFrame:
    return get_table(sheet_name)


# ----------------------------------------------
# AJOUT D'UNE LIGNE
# ----------------------------------------------

def append_row(sheet_name: str, row_data: list):
    df = get_table(sheet_name)

    # Si table vide → on crée les colonnes
    if df.empty:
        df = pd.DataFrame([row_data])
    else:
        df.loc[len(df)] = row_data

    save_table(sheet_name, df)


# ----------------------------------------------
# METTRE À JOUR UNE CELLULE
# ----------------------------------------------

def update_cell(sheet_name: str, row_idx: int, col_idx: int, value):
    df = get_table(sheet_name)
    df.iat[row_idx, col_idx] = value
    save_table(sheet_name, df)


# ----------------------------------------------
# SUPPRIMER UNE LIGNE PAR INDEX
# ----------------------------------------------

def delete_row(sheet_name: str, row_index: int):
    df = get_table(sheet_name)
    df = df.drop(index=row_index).reset_index(drop=True)
    save_table(sheet_name, df)


# ----------------------------------------------
# TROUVER INDEX PAR VALEUR (ex : “Dossier N”)
# ----------------------------------------------

def find_row_index(sheet_name: str, column: str, value):
    df = load_sheet(sheet_name)
    matches = df.index[df[column] == value].tolist()
    return matches[0] if matches else None


# ----------------------------------------------
# METTRE À JOUR UNE LIGNE ENTIÈRE
# ----------------------------------------------

def update_row(sheet_name: str, row_index: int, row_data: list):
    df = get_table(sheet_name)
    df.loc[row_index] = row_data
    save_table(sheet_name, df)


# ----------------------------------------------
# ESCROW
# ----------------------------------------------

def load_escrow():
    return load_sheet("Escrow")

def add_escrow_entry(row_data):
    append_row("Escrow", row_data)

def update_escrow_row(row_index, row_data):
    update_row("Escrow", row_index, row_data)

def delete_escrow_row(row_index):
    delete_row("Escrow", row_index)


# ----------------------------------------------
# VISA
# ----------------------------------------------

def load_visa():
    return load_sheet("Visa")

def add_visa_entry(row_data):
    append_row("Visa", row_data)

def update_visa_row(row_index, row_data):
    update_row("Visa", row_index, row_data)

def delete_visa_row(row_index):
    delete_row("Visa", row_index)


# ----------------------------------------------
# COMPTA
# ----------------------------------------------

def load_compta():
    return load_sheet("ComptaCli")

def add_compta_entry(row_data):
    append_row("ComptaCli", row_data)

def update_compta_row(row_index, row_data):
    update_row("ComptaCli", row_index, row_data)

def delete_compta_row(row_index):
    delete_row("ComptaCli", row_index)
