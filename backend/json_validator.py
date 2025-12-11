import json
import pandas as pd
from backend.dropbox_utils import load_database, save_database

REQUIRED_CLIENT_FIELDS = [
    "Dossier N", "Nom", "Date", "Categories", "Sous-categories", "Visa",
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4",
    "Dossier envoye", "Dossier accepte", "Dossier refuse", "Dossier Annule",
    "RFE", "Escrow", "Escrow_a_reclamer", "Escrow_reclame"
]

def analyse_incoherences(db):
    alerts = []
    clients = db.get("clients", [])

    for c in clients:
        dn = c.get("Dossier N")

        # Champs manquants
        for field in REQUIRED_CLIENT_FIELDS:
            if field not in c:
                alerts.append(f"[{dn}] Champ manquant : {field}")

        # Dates invalides
        for date_field in [
            "Date", "Date envoi", "Date acceptation",
            "Date refus", "Date annulation", "Date reclamation"
        ]:
            v = c.get(date_field)
            if v not in [None, "", "None"]:
                try:
                    pd.to_datetime(v, errors="raise")
                except:
                    alerts.append(f"[{dn}] Date invalide : {date_field} = {v}")

        # Montants incohérents
        try:
            if float(c.get("Acompte 1", 0)) > float(c.get("Montant honoraires (US $)", 0)):
                alerts.append(f"[{dn}] Acompte 1 supérieur aux honoraires")
        except:
            alerts.append(f"[{dn}] Valeur incohérente dans Acompte 1")

    return alerts


def validate_and_fix_json():
    db = load_database()
    clients = db.get("clients", [])
    fixed = False

    for c in clients:

        # 1️⃣ Ajouter les champs manquants (ne jamais écraser l'existant)
        for field in REQUIRED_CLIENT_FIELDS:
            if field not in c:
                if "Dossier" in field or "Escrow" in field or field == "RFE":
                    c[field] = False
                else:
                    c[field] = ""
                fixed = True

        # 2️⃣ Correction des dates invalides (sans toucher aux dates valides)
        for date_field in [
            "Date", "Date envoi", "Date acceptation",
            "Date refus", "Date annulation", "Date reclamation"
        ]:
            v = c.get(date_field)
            try:
                if v not in [None, "", "None"]:
                    pd.to_datetime(v, errors="raise")
            except:
                c[date_field] = None
                fixed = True

    if fixed:
        db["clients"] = clients
        save_database(db)

    return fixed
