import pandas as pd
from backend.dropbox_utils import load_database, save_database

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

RENAME_MAP = {
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
}

BOOL_COLS = [
    "Escrow", "Escrow_a_reclamer", "Escrow_reclame",
    "Dossier envoye", "Dossier accepte", "Dossier refuse",
    "Dossier Annule", "RFE"
]

DATE_COLS = [
    "Date", "Date envoi", "Date acceptation",
    "Date refus", "Date annulation", "Date reclamation"
]


# ---------------------------------------------------------
# NORMALISATION UTILITAIRES
# ---------------------------------------------------------
def normalize_bool(x):
    if isinstance(x, bool):
        return x
    if str(x).lower() in ["1", "true", "yes", "oui"]:
        return True
    return False

def normalize_date(v):
    try:
        d = pd.to_datetime(v, errors="coerce")
        return None if pd.isna(d) else str(d.date())
    except:
        return None

# ---------------------------------------------------------
# VALIDATION AUTOMATIQUE
# ---------------------------------------------------------
def validate_and_fix_json():
    db = load_database()
    clients = db.get("clients", [])
    fixed = []
    changed = False

    for c in clients:
        c2 = c.copy()

        # 1 — Renommage
        for old, new in RENAME_MAP.items():
            if old in c2:
                c2[new] = c2.pop(old)
                changed = True

        # 2 — Booléens
        for col in BOOL_COLS:
            if c2.get(col) not in [True, False]:
                c2[col] = normalize_bool(c2.get(col, False))
                changed = True

        # 3 — Dates
        for col in DATE_COLS:
            nd = normalize_date(c2.get(col))
            if c2.get(col) != nd:
                c2[col] = nd
                changed = True

        # 4 — Nettoyage "None" / NaN
        for k, v in list(c2.items()):
            if v == "None" or (isinstance(v, float) and pd.isna(v)):
                c2[k] = ""
                changed = True

        fixed.append(c2)

    # ---------------------------------------------------------
    # SAUVEGARDE SI CHANGEMENT
    # ---------------------------------------------------------
    if changed:
        db["clients"] = fixed
        save_database(db)
        return True

    return False
