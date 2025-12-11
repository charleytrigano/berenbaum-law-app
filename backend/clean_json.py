import pandas as pd

# Colonnes standardisées (aucune colonne statut avec underscore)
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

# Aliases détectés et fusionnés automatiquement
STATUS_ALIASES = {
    "Dossier envoye": [
        "Dossier_envoye",
        "Dossier envoyé",
        "Dossier Envoye",
        "Dossier envoyee",
        "Dossier Envoyé"
    ],
    "Dossier accepte": [
        "Dossier_accepte",
        "Dossier accepté",
        "Dossier Accepte",
        "Dossier Accepté"
    ],
    "Dossier refuse": [
        "Dossier_refuse",
        "Dossier refusé",
        "Dossier Refuse",
        "Dossier Refusé"
    ],
    "Dossier Annule": [
        "Dossier_annule",
        "Dossier annulé",
        "Dossier Annulé",
        "Dossier Annule"
    ],
    "RFE": ["RFE"],
}


def normalize_bool(v):
    """Convertit n'importe quelle valeur en bool."""
    if isinstance(v, bool):
        return v
    if v is None:
        return False
    return str(v).strip().lower() in ["1", "true", "yes", "oui", "y", "vrai"]


def clean_database(db):
    """Nettoyage complet et harmonisation du JSON."""
    cleaned_clients = []

    for item in db.get("clients", []):
        clean = {}

        # ------------------------------------------------------
        # 1) Fusion et normalisation de TOUS les statuts
        # ------------------------------------------------------
        for canonical, aliases in STATUS_ALIASES.items():
            val = item.get(canonical, False)

            for alias in aliases:
                if alias in item:
                    val = val or normalize_bool(item[alias])

            clean[canonical] = normalize_bool(val)

        # ------------------------------------------------------
        # 2) Normalisation des autres colonnes standard
        # ------------------------------------------------------
        for col, default in VALID_COLUMNS.items():
            if col in clean:
                # colonne déjà traitée (statuts)
                continue

            val = item.get(col, default)

            # BOOL
            if isinstance(default, bool):
                val = normalize_bool(val)

            # FLOAT
            elif isinstance(default, float):
                try:
                    val = float(val)
                except:
                    val = default

            # DATES
            elif isinstance(default, str) and "Date" in col:
                val = val if val else ""

            # TEXTE
            elif isinstance(default, str):
                val = val if val else ""

            clean[col] = val

        cleaned_clients.append(clean)

    # ------------------------------------------------------
    # FIN – Reconstruction DB normalisée
    # ------------------------------------------------------
    return {
        "clients": cleaned_clients,
        "visa": db.get("visa", []),
        "escrow": db.get("escrow", []),
        "compta": db.get("compta", []),
    }
