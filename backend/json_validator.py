import json
import pandas as pd
from backend.dropbox_utils import load_database, save_database


def validate_and_fix_json():
    """
    Vérification et réparation automatique du JSON.
    """
    try:
        db = load_database()
    except Exception:
        return False

    if not isinstance(db, dict):
        return False

    fixed = False

    # Structure obligatoire
    for key in ["clients", "visa", "escrow", "compta"]:
        if key not in db or not isinstance(db[key], list):
            db[key] = []
            fixed = True

    cleaned_clients = []

    for c in db["clients"]:
        if not isinstance(c, dict):
            fixed = True
            continue

        row = c.copy()

        # Normalisation booléens
        bool_fields = [
            "Escrow", "Escrow_a_reclamer", "Escrow_reclame",
            "Dossier envoye", "Dossier accepte", "Dossier refuse",
            "Dossier Annule", "RFE"
        ]
        for b in bool_fields:
            if b in row:
                row[b] = True if str(row[b]).lower() in ["true", "1", "yes", "oui"] else False

        # Dates → format ISO
        for k in list(row.keys()):
            if "Date" in k:
                d = pd.to_datetime(row[k], errors="coerce")
                row[k] = None if pd.isna(d) else str(d.date())

        cleaned_clients.append(row)

    db["clients"] = cleaned_clients

    if fixed:
        save_database(db)

    return fixed


def analyse_incoherences():
    """
    Renvoie une liste d'avertissements métier.
    """
    try:
        db = load_database()
        clients = db.get("clients", [])
    except Exception:
        return []

    alerts = []

    for row in clients:
        if not isinstance(row, dict):
            continue

        num = row.get("Dossier N", "?")
        prefix = f"Dossier {num} : "

        # Cas métier cohérents
        if row.get("Dossier accepte") and not row.get("Dossier envoye"):
            alerts.append(prefix + "Accepté mais non envoyé.")

        if row.get("Escrow_reclame") and not row.get("Escrow_a_reclamer"):
            alerts.append(prefix + "Escrow réclamé alors qu'il n'était pas à réclamer.")

        if row.get("Escrow") and row.get("Dossier envoye"):
            alerts.append(prefix + "Dossier envoyé mais encore en Escrow.")

    return alerts