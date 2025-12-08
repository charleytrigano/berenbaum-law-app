import pandas as pd

def clean_database(db):

    cleaned_clients = []
    for c in db.get("clients", []):
        c = c.copy()

        # Renommage anciens noms
        if "Catégories" in c:
            c["Categories"] = c.pop("Catégories")

        if "Sous-catégories" in c:
            c["Sous-categories"] = c.pop("Sous-catégories")

        # Important : NE RIEN TOUCHER si c'est un bool
        for k, v in list(c.items()):
            # bool → on NE touche pas
            if isinstance(v, bool):
                continue

            # None → remplacer
            if v is None:
                c[k] = ""
                continue

            # float NaN → remplacer
            if isinstance(v, float) and pd.isna(v):
                c[k] = ""
                continue

        cleaned_clients.append(c)

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
