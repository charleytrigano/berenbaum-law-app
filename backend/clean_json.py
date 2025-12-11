import pandas as pd

# Colonnes standardisées avec les statuts inclus
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
    
    # --- STATUTS (LE GRAND MANQUANT !) ---
    "Dossier envoye": False,
    "Dossier accepte": False,
    "Dossier refuse": False,
    "Dossier Annule": False,
    "RFE": False,

    # --- DATES STATUTS ---
    "Date envoi": "",
    "Date acceptation": "",
    "Date refus": "",
    "Date annulation": "",
    "Date reclamation": "",

    # --- ESCROW ---
    "Escrow": False,
    "Escrow_a_reclamer": False,
    "Escrow_reclame": False,
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
                    except:
                        val = default

                # date (string)
                elif isinstance(default, str) and "Date" in col:
                    val = val if val else ""

                # generic string
                elif isinstance(default, str):
                    val = val if val else ""

                clean[col] = val

            else:
                # Colonne manquante → ajout avec valeur par défaut
                clean[col] = default

        cleaned_clients.append(clean)

    return {
        "clients": cleaned_clients,
        "visa": db.get("visa", []),
        "escrow": db.get("escrow", []),
        "compta": db.get("compta", [])
    }