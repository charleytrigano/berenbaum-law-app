import pandas as pd
from datetime import datetime, date

# Colonnes standardisées
VALID_COLUMNS = {
    "Dossier N": None,
    "Nom": "",
    "Date": "",
    "Categories": "",
    "Sous-categories": "",
    "Visa": "",
    "Montant honoraires (US $)": 0.0,
    "Autres frais (US $)": 0.0,
    "Acompte 1": 0.0,
    "Acompte 2": 0.0,
    "Acompte 3": 0.0,
    "Acompte 4": 0.0,
    "Date Acompte 1": "",
    "Date Acompte 2": "",
    "Date Acompte 3": "",
    "Date Acompte 4": "",
    "mode de paiement": "",
    "Escrow": False,
    "Escrow_a_reclamer": False,
    "Escrow_reclame": False,
    "Dossier envoye": False,
    "Date envoi": "",
    "Dossier accepte": False,
    "Date acceptation": "",
    "Dossier refuse": False,
    "Date refus": "",
    "Dossier Annule": False,
    "Date annulation": "",
    "RFE": False,
    "Date reclamation": "",
}


def normalize_bool(v):
    if isinstance(v, bool):
        return v
    if v is None:
        return False
    return str(v).strip().lower() in ["1", "true", "yes", "oui"]


def serialize_value(val):
    """
    🔒 FONCTION CRITIQUE
    Convertit toute valeur non sérialisable JSON
    """
    if isinstance(val, pd.Timestamp):
        return val.date().isoformat()
    if isinstance(val, (datetime, date)):
        return val.isoformat()
    if pd.isna(val):
        return ""
    return val


def clean_database(db):
    cleaned_clients = []

    for item in db.get("clients", []):
        clean = {}

        for col, default in VALID_COLUMNS.items():
            if col in item:
                val = item[col]
            else:
                val = default

            # Booléens
            if isinstance(default, bool):
                val = normalize_bool(val)

            # Floats
            elif isinstance(default, float):
                try:
                    val = float(val)
                except Exception:
                    val = default

            # Dates / Timestamp / NaT
            val = serialize_value(val)

            clean[col] = val

        cleaned_clients.append(clean)

    return {
        "clients": cleaned_clients,
        "visa": db.get("visa", []),
        "escrow": db.get("escrow", []),
        "compta": db.get("compta", []),
        "history": db.get("history", []),
    }
