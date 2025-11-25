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
