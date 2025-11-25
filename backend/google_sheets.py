import pandas as pd
from backend.google_auth import get_gsheet_service
from utils.config import FILE_ID

# ------------------------------
# CHARGEMENT D'UN ONGLET COMPLET
# ------------------------------

def load_sheet(sheet_name: str) -> pd.DataFrame:
    service = get_gsheet_service()
    sheet = service.spreadsheets().values().get(
        spreadsheetId=FILE_ID,
        range=sheet_name
    ).execute()

    values = sheet.get("values", [])

    if not values:
        return pd.DataFrame()

    df = pd.DataFrame(values[1:], columns=values[0])
    return df


# ------------------------------
# AJOUT D'UNE LIGNE
# ------------------------------

def append_row(sheet_name: str, row_data: list):
    service = get_gsheet_service()
    service.spreadsheets().values().append(
        spreadsheetId=FILE_ID,
        range=sheet_name,
        valueInputOption="USER_ENTERED",
        body={"values": [row_data]}
    ).execute()


# ------------------------------
# MISE À JOUR D'UNE CELLULE
# ------------------------------

def update_cell(sheet_name: str, cell_range: str, value):
    service = get_gsheet_service()
    body = {
        "values": [[value]]
    }
    service.spreadsheets().values().update(
        spreadsheetId=FILE_ID,
        range=f"{sheet_name}!{cell_range}",
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()


# ------------------------------
# SUPPRESSION D'UNE LIGNE PAR INDEX
# ------------------------------

def delete_row(sheet_name: str, row_index: int):
    service = get_gsheet_service()
    body = {
        "requests": [
            {
                "deleteDimension": {
                    "range": {
                        "sheetId": get_sheet_id(sheet_name),
                        "dimension": "ROWS",
                        "startIndex": row_index,
                        "endIndex": row_index + 1
                    }
                }
            }
        ]
    }
    service.spreadsheets().batchUpdate(
        spreadsheetId=FILE_ID,
        body=body
    ).execute()


# ------------------------------
# RÉCUPÉRATION DU SHEET_ID
# ------------------------------

def get_sheet_id(sheet_name: str):
    service = get_gsheet_service()
    metadata = service.spreadsheets().get(spreadsheetId=FILE_ID).execute()
    sheets = metadata.get("sheets", "")

    for s in sheets:
        title = s["properties"]["title"]
        if title == sheet_name:
            return s["properties"]["sheetId"]

    raise Exception(f"Sheet {sheet_name} not found")

# ----------------------------------------
# TROUVER L’INDEX D’UN DOSSIER PAR "Dossier N"
# ----------------------------------------
def find_row_index(sheet_name: str, dossier_number: str):
    df = load_sheet(sheet_name)
    if "Dossier N" not in df.columns:
        raise Exception("Colonne 'Dossier N' introuvable dans le fichier.")

    matches = df.index[df["Dossier N"] == dossier_number].tolist()
    return matches[0] if matches else None


# ----------------------------------------
# METTRE À JOUR UNE LIGNE COMPLÈTE
# ----------------------------------------
def update_row(sheet_name: str, row_index: int, row_data: list):
    service = get_gsheet_service()

    body = {"values": [row_data]}

    service.spreadsheets().values().update(
        spreadsheetId=FILE_ID,
        range=f"{sheet_name}!A{row_index+2}",
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()


# ----------------------------------------
# SUPPRESSION SÉCURISÉE D’UNE LIGNE
# ----------------------------------------
def delete_row_safely(sheet_name: str, row_index: int):
    service = get_gsheet_service()
    sheet_id = get_sheet_id(sheet_name)

    body = {
        "requests": [{
            "deleteDimension": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "ROWS",
                    "startIndex": row_index,
                    "endIndex": row_index + 1
                }
            }
        }]
    }

    service.spreadsheets().batchUpdate(
        spreadsheetId=FILE_ID,
        body=body
    ).execute()


# ----------------------------------------
# CONVERTIR UN DICTIONNAIRE EN LISTE POUR GSHEETS
# ----------------------------------------
def convert_df_to_row(df_row, columns):
    return [df_row[col] if col in df_row else "" for col in columns]

# --------------------------------------------------
# ESCROW – Chargement complet
# --------------------------------------------------
def load_escrow():
    return load_sheet("Escrow")


# --------------------------------------------------
# ESCROW – Ajouter un mouvement
# --------------------------------------------------
def add_escrow_entry(row_data: list):
    append_row("Escrow", row_data)


# --------------------------------------------------
# ESCROW – Modifier un mouvement
# --------------------------------------------------
def update_escrow_row(row_index: int, row_data: list):
    update_row("Escrow", row_index, row_data)


# --------------------------------------------------
# ESCROW – Supprimer un mouvement
# --------------------------------------------------
def delete_escrow_row(row_index: int):
    delete_row_safely("Escrow", row_index)

# --------------------------------------------------
# VISA – Charger l’onglet Visa
# --------------------------------------------------
def load_visa():
    return load_sheet("Visa")


# --------------------------------------------------
# VISA – Ajouter une entrée
# --------------------------------------------------
def add_visa_entry(row_data: list):
    append_row("Visa", row_data)


# --------------------------------------------------
# VISA – Modifier une ligne Visa
# --------------------------------------------------
def update_visa_row(row_index: int, row_data: list):
    update_row("Visa", row_index, row_data)


# --------------------------------------------------
# VISA – Supprimer une ligne Visa
# --------------------------------------------------
def delete_visa_row(row_index: int):
    delete_row_safely("Visa", row_index)



