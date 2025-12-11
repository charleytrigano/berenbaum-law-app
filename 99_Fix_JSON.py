import json
import pandas as pd
from backend.dropbox_utils import load_database, save_database

print("🔧 Lancement de la réparation du JSON Dropbox…")

# ---------------------------------------------------------
# 🟦 CHARGEMENT DU JSON ACTUEL
# ---------------------------------------------------------
db = load_database()

clients = db.get("clients", [])
visa = db.get("visa", [])
escrow = db.get("escrow", [])
compta = db.get("compta", [])

cleaned = []

# ---------------------------------------------------------
# 🟨 MAP DE NORMALISATION DES COLONNES
# ---------------------------------------------------------
rename_map = {
    "Dossier_envoye": "Dossier envoye",
    "Dossier Envoye": "Dossier envoye",
    "Dossier envoyé": "Dossier envoye",

    "Dossier_accepte": "Dossier accepte",
    "Dossier accepté": "Dossier accepte",
    "Dossier accepte": "Dossier accepte",

    "Dossier_refuse": "Dossier refuse",
    "Dossier refusé": "Dossier refuse",
    "Dossier refuse": "Dossier refuse",

    "Dossier_annule": "Dossier Annule",
    "Dossier annulé": "Dossier Annule",

    "Date_accepte": "Date acceptation",
    "Date_acceptation": "Date acceptation",

    "Date_refuse": "Date refus",
    "Date_refus": "Date refus",

    "Date_annule": "Date annulation",
    "Date_annulation": "Date annulation",

    "Date_envoi": "Date envoi",
}

def normalize_bool(x):
    if isinstance(x, bool):
        return x
    if str(x).strip().lower() in ["1", "true", "yes", "oui"]:
        return True
    return False

def clean_date(x):
    try:
        d = pd.to_datetime(x, errors="coerce")
        return None if pd.isna(d) else str(d.date())
    except:
        return None

# ---------------------------------------------------------
# 🔧 BOUCLE SUR CLIENTS
# ---------------------------------------------------------
for c in clients:
    c = c.copy()

    # Renommage
    for old, new in rename_map.items():
        if old in c:
            c[new] = c.pop(old)

    # Sécurisation booléens Escrow + Statuts
    for col in ["Escrow", "Escrow_a_reclamer", "Escrow_reclame",
                "Dossier envoye", "Dossier accepte", "Dossier refuse",
                "Dossier Annule", "RFE"]:
        c[col] = normalize_bool(c.get(col, False))

    # Nettoyage des valeurs NaN / None
    for k, v in list(c.items()):
        if isinstance(v, float) and pd.isna(v):
            c[k] = ""
        if v == "None":
            c[k] = ""

    # Dates normalisées
    for dcol in ["Date", "Date envoi", "Date acceptation", "Date refus",
                 "Date annulation", "Date reclamation"]:
        c[dcol] = clean_date(c.get(dcol))

    cleaned.append(c)

# ---------------------------------------------------------
# 💾 SAUVEGARDE JSON RÉPARÉ
# ---------------------------------------------------------
db["clients"] = cleaned
save_database(db)

print("✔ JSON réparé et sauvegardé avec succès !")
