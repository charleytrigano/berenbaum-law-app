import pandas as pd

# Colonnes standardisées (VERSION FINALE)
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
    # ⚠️ IMPORTANT : nom canonique AVEC ESPACE
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
    "Commentaire": "",
}


def normalize_bool(v):
    if isinstance(v, bool):
        return v
    if v is None:
        return False
    return str(v).strip().lower() in ["1", "true", "yes", "oui", "y", "vrai"]


def clean_database(db):
    cleaned_clients = []

    for item in db.get("clients", []):
        # --------------------------------------------------
        # 1) Migration des anciens noms de colonnes (aliases)
        # --------------------------------------------------
        # Ancienne colonne avec underscore -> on la mappe vers la nouvelle
        if "Dossier_envoye" in item and "Dossier envoye" not in item:
            item["Dossier envoye"] = item["Dossier_envoye"]

        # On peut en ajouter d'autres si jamais tu avais des variations :
        # ex : "Dossier envoyé", "Dossier Envoye", etc.
        if "Dossier envoyé" in item and "Dossier envoye" not in item:
            item["Dossier envoye"] = item["Dossier envoyé"]

        clean = {}

        # --------------------------------------------------
        # 2) Normalisation stricte des colonnes connues
        # --------------------------------------------------
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

                # dates (laisser chaîne ou vide)
                elif isinstance(default, str) and "Date" in col:
                    val = val if val else ""

                # texte
                elif isinstance(default, str):
                    val = val if val else ""

                clean[col] = val
            else:
                clean[col] = default

        # --------------------------------------------------
        # 3) On ignore les anciennes colonnes parasites
        #    comme "Dossier_envoye", etc. (elles ne sont
        #    plus recréées).
        # --------------------------------------------------

        cleaned_clients.append(clean)

    return {
        "clients": cleaned_clients,
        "visa": db.get("visa", []),
        "escrow": db.get("escrow", []),
        "compta": db.get("compta", []),
    }