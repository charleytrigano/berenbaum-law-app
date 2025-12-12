import pandas as pd

# Colonnes standardisées (on utilise la version CANONIQUE : "Dossier envoye")
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

    # --- STATUTS (version canonique) ---
    "Dossier envoye": False,      # <- IMPORTANT : espace, pas underscore
    "Dossier accepte": False,
    "Dossier refuse": False,
    "Dossier Annule": False,
    "RFE": False,

    # --- DATES LIÉES AUX STATUTS ---
    "Date envoi": "",
    "Date acceptation": "",
    "Date refus": "",
    "Date annulation": "",
    "Date reclamation": "",

    # --- ESCROW ---
    "Escrow": False,
    "Escrow_a_reclamer": False,
    "Escrow_reclame": False,
}


def normalize_bool(v):
    if isinstance(v, bool):
        return v
    if v is None:
        return False
    if str(v).strip().lower() in ["1", "true", "yes", "oui"]:
        return True

    # -------------------------------------------------
# 🔒 GARANTIE EXCLUSIVITÉ ESCROW (CRITIQUE)
# -------------------------------------------------
for c in cleaned_clients:
    if c.get("Escrow_reclame"):
        c["Escrow"] = False
        c["Escrow_a_reclamer"] = False

    elif c.get("Escrow_a_reclamer"):
        c["Escrow"] = False
        c["Escrow_reclame"] = False

    elif c.get("Escrow"):
        c["Escrow_a_reclamer"] = False
        c["Escrow_reclame"] = False

    return False


def clean_database(db):
    cleaned_clients = []

    for original in db.get("clients", []):
        # On travaille sur une copie pour pouvoir migrer les vieux champs
        item = dict(original)

        # ---------- MIGRATION ANCIENS NOMS -> NOUVEAUX ----------
        # Si "Dossier_envoye" existe et "Dossier envoye" n'existe pas encore,
        # on copie la valeur vers le champ canonique.
        if "Dossier_envoye" in item and "Dossier envoye" not in item:
            item["Dossier envoye"] = item["Dossier_envoye"]

        # (On pourrait ajouter ici d'autres migrations si nécessaire)

        # ---------- NORMALISATION SELON VALID_COLUMNS ----------
        clean = {}

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
                        # date → STRING ISO (JSON SAFE)
                elif isinstance(val, pd.Timestamp):
                        val = val.date().isoformat()

                elif isinstance(default, str) and "Date" in col:
                    try:
                        if val in [None, "", "None"]:
                            val = ""
                        else:
                            val = pd.to_datetime(val, errors="coerce")
                            val = "" if pd.isna(val) else val.date().isoformat()
                        except Exception:
                        val = ""


            

   

                # texte générique
                elif isinstance(default, str):
                    val = val if val else ""

                clean[col] = val
            else:
                # colonne manquante → valeur par défaut
                clean[col] = default

        cleaned_clients.append(clean)

    return {
        "clients": cleaned_clients,
        "visa": db.get("visa", []),
        "escrow": db.get("escrow", []),
        "compta": db.get("compta", []),
    }
