import pandas as pd

from backend.convert_excel_to_json import convert_clients_excel_to_json


def convert_all_excels_to_json():
    """
    Reconstruit database.json en lisant les Excels.
    IMPORTANT : ajoute la colonne Commentaire si elle est présente (sinon défaut "").
    """
    # Chemins / sources : on suppose que dropbox_utils / config gèrent déjà le téléchargement,
    # ici on lit des fichiers locaux si présents.
    # Si ton projet télécharge dans /tmp ou similaire, adapte uniquement les paths ci-dessous.
    clients_path = "Clients.xlsx"
    visa_path = "Visa.xlsx"
    escrow_path = "Escrow.xlsx"
    compta_path = "ComptaCli.xlsx"

    db = {"clients": [], "visa": [], "escrow": [], "compta": []}

    # CLIENTS
    try:
        df_clients = pd.read_excel(clients_path)
        db["clients"] = convert_clients_excel_to_json(df_clients)
    except Exception:
        db["clients"] = []

    # VISA
    try:
        df_visa = pd.read_excel(visa_path)
        db["visa"] = df_visa.fillna("").to_dict(orient="records")
    except Exception:
        db["visa"] = []

    # ESCROW
    try:
        df_escrow = pd.read_excel(escrow_path)
        db["escrow"] = df_escrow.fillna("").to_dict(orient="records")
    except Exception:
        db["escrow"] = []

    # COMPTA
    try:
        df_compta = pd.read_excel(compta_path)
        db["compta"] = df_compta.fillna("").to_dict(orient="records")
    except Exception:
        db["compta"] = []

    return db
