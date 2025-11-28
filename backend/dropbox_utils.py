import pandas as pd
from backend.google_auth import get_gsheet_service
from utils.config import FILE_ID

# ---------------------------------------
# CHARGEMENT D’UN ONGLET (sheet)
# ---------------------------------------
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


# ---------------------------------------
# AJOUT D’UNE LIGNE
# ---------------------------------------
def append_row(sheet_name: str, row_data: list):
    service = get_gsheet_service()

    service.spreadsheets().values().append(
        spreadsheetId=FILE_ID,
        range=sheet_name,
        valueInputOption="USER_ENTERED",
        body={"values": [row_data]}
    ).execute()


# ---------------------------------------
# MISE À JOUR D’UNE CELLULE
# ---------------------------------------
def update_cell(sheet_name: str, cell_range: str, value):
    service = get_gsheet_service()

    body = {"values": [[value]]}

    service.spreadsheets().values().update(
        spreadsheetId=FILE_ID,
        range=f"{sheet_name}!{cell_range}",
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()


# ---------------------------------------
# TROUVER L’INDEX D’UNE LIGNE PAR DOSSIER N
# ---------------------------------------
def find_row_index(sheet_name: str, dossier_number: str):
    df = load_sheet(sheet_name)

    if "Dossier N" not in df.columns:
        raise Exception("La colonne 'Dossier N' est introuvable.")

    matches = df.index[df["Dossier N"] == dossier_number].tolist()
    return matches[0] if matches else None


# ---------------------------------------
# MISE À JOUR D’UNE LIGNE COMPLÈTE
# ---------------------------------------
def update_row(sheet_name: str, row_index: int, row_data: list):
    service = get_gsheet_service()

    body = {"values": [row_data]}

    service.spreadsheets().values().update(
        spreadsheetId=FILE_ID,
        range=f"{sheet_name}!A{row_index+2}",
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()


# ---------------------------------------
# SUPPRESSION D’UNE LIGNE
# ---------------------------------------
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


# ---------------------------------------
# OBTENIR L’ID INTERNE D’UNE FEUILLE
# ---------------------------------------
def get_sheet_id(sheet_name: str):
    service = get_gsheet_service()

    metadata = service.spreadsheets().get(
        spreadsheetId=FILE_ID
    ).execute()

    sheets = metadata.get("sheets", [])

    for s in sheets:
        if s["properties"]["title"] == sheet_name:
            return s["properties"]["sheetId"]

    raise Exception(f"Sheet {sheet_name} not found")

