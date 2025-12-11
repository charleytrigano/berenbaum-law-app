import pandas as pd

# Colonnes standardisées CANONIQUES (aucun alias dans ce fichier)
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

    # STATUTS — uniquement les colonnes CANONIQUES !
    "Dossier envoye": False,
    "Dossier accepte": False,
    "Dossier refuse": False,
    "Dossier Annule": False,
    "RFE": False,

    "Date envoi": "",
    "Date acceptation": "",
    "Date refus": "",
    "Date annulation": "",
    "Date reclamation": "",

    # ESCROW
    "Escrow": False,
    "Escrow_a_reclamer": False,
    "Escrow_reclame": False,
}


def normalize_bool(v):
    """Convertit toute valeur en booléen cohérent."""
    if isinstance(v, bool):
        return v
    if v is None:
        return False
    return str(v).strip().lower() in ["1", "true", "yes", "oui", "y", "vrai"]


def clean_database(db):
    """
    Nettoyage des données :
    - Fusion des noms de colonnes alias (Dossier_envoye → Dossier envoye)
    - Harmonisation des types
    - Dates invalides converties en ""
    - Ajout des colonnes manquantes
    """

    cleaned_clients = []

    for item in db.get("clients", []):
        # COPIE SOURCE
        original = item.copy()

        # ---------------------------------------------------------
        # 1. NORMALISATION DES ALIAS → colonnes canoniques
        # ---------------------------------------------------------

        # Alias → Dossier envoye
        if "Dossier_envoye" in original:
            original["Dossier envoye"] = normalize_bool(original["Dossier_envoye"])

        # Alias → Dossier accepte
        if "Dossier_accepté" in original:
            original["Dossier accepte"] = normalize_bool(original["Dossier_accepté"])
        if "Dossier accepté" in original:
            original["Dossier accepte"] = normalize_bool(original["Dossier accepté"])

        # Alias → Dossier refuse
        if "Dossier_refuse" in original:
            original["Dossier refuse"] = normalize_bool(original["Dossier_refuse"])
        if "Dossier refusé" in original:
            original["Dossier refuse"] = normalize_bool(original["Dossier refusé"])

        # Alias → Dossier Annule
        if "Dossier_annule" in original:
            original["Dossier Annule"] = normalize_bool(original["Dossier_annule"])
        if "Dossier annulé" in original:
            original["Dossier Annule"] = normalize_bool(original["Dossier annulé"])

        # ---------------------------------------------------------
        # 2. Construction finale nettoyée
        # ---------------------------------------------------------

        clean = {}

        for col, default_value in VALID_COLUMNS.items():

            if col in original:
                val = original[col]

                # booléens
                if isinstance(default_value, bool):
                    val = normalize_bool(val)

                # float
                elif isinstance(default_value, float):
                    try:
                        val = float(val)
                    except:
                        val = default_value

                # Dates (laisser string ou "")
                elif "Date" in col:
                    val = val if val not in [None, "None"] else ""

                # Textes
                elif isinstance(default_value, str):
                    val = val if val else ""

                clean[col] = val

            else:
                # Valeur par défaut si colonne manquante
                clean[col] = default_value

        cleaned_clients.append(clean)

    # Retour JSON normalisé
    return {
        "clients": cleaned_clients,
        "visa": db.get("visa", []),
        "escrow": db.get("escrow", []),
        "compta": db.get("compta", []),
    }
