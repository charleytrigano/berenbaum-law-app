# backend/clean_json.py
import pandas as pd

def clean_database(db):

    # Nettoyage des dossiers clients
    cleaned_clients = []
    for c in db.get("clients", []):
        c = c.copy()

        # Renommage automatique
        if "Catégories" in c:
            c["Categories"] = c.pop("Catégories")

        if "Sous-catégories" in c:
            c["Sous-categories"] = c.pop("Sous-catégories")

        # Valeurs vides → ""
        for k, v in c.items():
            if pd.isna(v):
                c[k] = ""

        cleaned_clients.append(c)

    # Nettoyage de la table VISA
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
