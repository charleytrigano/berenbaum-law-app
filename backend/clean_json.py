# backend/clean_json.py
import pandas as pd

def clean_database(db):
    """ Nettoie complètement la base JSON pour assurer cohérence totale """

    cleaned_clients = []
    for c in db.get("clients", []):
        c = c.copy()

        # --- Renommer anciennes colonnes ---
        if "Catégories" in c:
            c["Categories"] = c.pop("Catégories")

        if "Sous-catégories" in c:
            c["Sous-categories"] = c.pop("Sous-catégories")

        # --- Supprimer colonne obsolète ---
        if "Escrow_final" in c:
            c.pop("Escrow_final")

        # --- Assurer présence de la colonne Escrow ---
        if "Escrow" not in c:
            c["Escrow"] = False

        # --- Normaliser Escrow ---
        esc = c["Escrow"]
        if isinstance(esc, str):
            esc = esc.strip().lower() in ["true", "1", "yes"]
        elif isinstance(esc, (int, float)):
            esc = (esc == 1)
        else:
            esc = bool(esc)
        c["Escrow"] = esc

        # --- Nettoyage générique mais préserver les bool ---
        for k, v in list(c.items()):
            if isinstance(v, bool):
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
