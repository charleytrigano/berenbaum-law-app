# backend/clean_json.py
import pandas as pd

def clean_database(db):
    """ Nettoie complètement la base JSON pour assurer cohérence totale """

    cleaned_clients = []
    for c in db.get("clients", []):
        c = c.copy()

        # Renommage des anciennes colonnes françaises
        if "Catégories" in c:
            c["Categories"] = c.pop("Catégories")

        if "Sous-catégories" in c:
            c["Sous-categories"] = c.pop("Sous-catégories")

        # Correction automatique des valeurs d'Escrow
        # Si la valeur est "", None, NaN → on passe à False
        if "Escrow" in c:
            if c["Escrow"] in ["", None] or (isinstance(c["Escrow"], float) and pd.isna(c["Escrow"])):
                c["Escrow"] = False

        # Préserver les booléens, nettoyer uniquement les autres types
        for k, v in list(c.items()):
            if isinstance(v, bool):     # Ne pas toucher les bool
                continue
            if pd.isna(v) or v is None:
                c[k] = ""

        cleaned_clients.append(c)

    # ---------------- CLEAN VISA ----------------
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
