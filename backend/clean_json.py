import pandas as pd

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
    "Commentaire": "",  # ✅ AJOUT

    "Escrow": False,
    "Escrow_a_reclamer": False,
    "Escrow_reclame": False,

    "Dossier_envoye": False,
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
    if str(v).strip().lower() in ["1", "true", "yes", "oui"]:
        return True
    return False


def clean_database(db):
    cleaned_clients = []

    for item in db.get("clients", []):
        if not isinstance(item, dict):
            continue

        clean = {}

        for col, default in VALID_COLUMNS.items():
            if col in item:
                val = item[col]

                # bool
                if isinstance(default, bool):
                    val = normalize_bool(val)

                # float
                elif isinstance(default, float):
                    try:
                        val = float(val)
                    except Exception:
                        val = default

                # date (laisser string)
                elif isinstance(default, str) and "Date" in col:
                    val = val if val else ""

                # text
                elif isinstance(default, str):
                    val = val if val else ""

                clean[col] = val
            else:
                clean[col] = default

        cleaned_clients.append(clean)

    return {
        "clients": cleaned_clients,
        "visa": db.get("visa", []),
        "escrow": db.get("escrow", []),
        "compta": db.get("compta", []),
        "tarifs": db.get("tarifs", []),
        "tarifs_history": db.get("tarifs_history", []),
        "history": db.get("history", []),
    }
