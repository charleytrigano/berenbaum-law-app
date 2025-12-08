import pandas as pd

# Colonnes autorisées et normalisées
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

def normalize_bool(value):
    """Nettoyage strict des valeurs bool."""
    if isinstance(value, bool):
        return value
    if str(value).strip().lower() in ["true", "1", "yes", "oui"]:
        return True
    return False

def clean_database(db):
    cleaned_clients = []

    for item in db.get("clients", []):
        clean = {}

        # On force toutes les colonnes valides à exister
        for col, default in VALID_COLUMNS.items():

            if col in item:
                val = item[col]

                # Booléens
                if isinstance(default, bool):
                    val = normalize_bool(val)

                # Nombres
                elif isinstance(default, float):
                    try:
                        val = float(val)
                    except:
                        val = default

                # Dates : on laisse tel quel
                elif isinstance(default, str) and "Date" in col:
                    val = val if val else ""

                # Texte
                elif isinstance(default, str):
                    val = val if val else ""

                clean[col] = val

            else:
                # Colonne manquante → valeur par défaut
                clean[col] = default

        cleaned_clients.append(clean)

    return {
        "clients": cleaned_clients,
        "visa": db.get("visa", []),
        "escrow": db.get("escrow", []),
        "compta": db.get("compta", [])
    }
