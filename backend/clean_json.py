import pandas as pd

def clean_database(db):
    """ Nettoyage complet et unification des colonnes """

    cleaned_clients = []
    for c in db.get("clients", []):
        c = c.copy()

        # ------------------------------------------------------
        # Unifier Catégories / Sous-catégories
        # ------------------------------------------------------
        if "Catégories" in c:
            c["Categories"] = c.pop("Catégories")

        if "Sous-catégories" in c:
            c["Sous-categories"] = c.pop("Sous-catégories")

        # ------------------------------------------------------
        # Unifier Dossier envoye (PAS D’ACCENT)
        # ------------------------------------------------------
        if "Dossier envoyé" in c:  # mauvais champ → supprimer
            c["Dossier envoye"] = c.pop("Dossier envoyé")

        # si pas encore présent
        if "Dossier envoye" not in c:
            c["Dossier envoye"] = False

        # ------------------------------------------------------
        # Nettoyage valeurs None / NaN
        # ------------------------------------------------------
        for k, v in list(c.items()):
            if v is None:
                c[k] = ""
            elif isinstance(v, float) and pd.isna(v):
                c[k] = ""

        cleaned_clients.append(c)

    # VISA
    cleaned_visa = []
    for v in db.get("visa", []):
        v = v.copy()

        if "Catégories" in v:
            v["Categories"] = v.pop("Catégories")

        if "Sous-catégories" in v:
            v["Sous-categories"] = v.pop("Sous-catégories")

        cleaned_visa.append(v)

    return {
        "clients": cleaned_clients,
        "visa": cleaned_visa,
        "escrow": db.get("escrow", []),
        "compta": db.get("compta", [])
    }
