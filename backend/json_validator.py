import json
import pandas as pd
from backend.dropbox_utils import load_database, save_database


# ============================================================================
# 🔧 VALIDATION TECHNIQUE + CORRECTIONS AUTOMATIQUES DU JSON
# ============================================================================
def validate_and_fix_json():
    """
    Vérifie que le JSON est propre, corrige automatiquement les anomalies
    et renvoie True si des corrections ont été appliquées.
    """
    try:
        db = load_database()
    except Exception:
        return False

    if not isinstance(db, dict):
        db = {}
        fixed = True
    else:
        fixed = False

    # Vérification des sections principales
    required_sections = ["clients", "visa", "escrow", "compta"]

    for sec in required_sections:
        if sec not in db or not isinstance(db.get(sec), list):
            db[sec] = []
            fixed = True

    clients = db["clients"]
    cleaned = []

    for row in clients:
        if not isinstance(row, dict):
            fixed = True
            continue

        r = row.copy()

        # Renommage pour uniformisation
        if "Dossier_envoye" in r and "Dossier envoye" not in r:
            r["Dossier envoye"] = r.pop("Dossier_envoye")
            fixed = True

        # Normalisation booléens
        def to_bool(v):
            if isinstance(v, bool):
                return v
            return str(v).lower() in ["true", "1", "yes", "oui"]

        bool_fields = [
            "Escrow",
            "Escrow_a_reclamer",
            "Escrow_reclame",
            "Dossier envoye",
            "Dossier accepte",
            "Dossier refuse",
            "Dossier Annule",
            "RFE",
        ]

        for b in bool_fields:
            if b in r:
                r[b] = to_bool(r[b])

        # Nettoyage des dates → ISO YYYY-MM-DD
        for k in list(r.keys()):
            if "Date" in k:
                d = pd.to_datetime(r[k], errors="coerce")
                r[k] = None if pd.isna(d) else str(d.date())

        # Montants
        for k in ["Montant honoraires (US $)", "Autres frais (US $)"]:
            try:
                r[k] = float(r.get(k, 0) or 0)
            except:
                r[k] = 0.0
                fixed = True

        # Acomptes
        for i in range(1, 5):
            ak = f"Acompte {i}"
            try:
                r[ak] = float(r.get(ak, 0) or 0)
            except:
                r[ak] = 0.0
                fixed = True

        # Champs texte obligatoires
        for k in ["Categories", "Sous-categories", "Visa", "Commentaire"]:
            if k not in r or r[k] is None:
                r[k] = ""
                fixed = True

        cleaned.append(r)

    # Suppression des doublons Dossier N
    seen = set()
    unique = []
    for r in cleaned:
        num = r.get("Dossier N")
        if num in seen:
            fixed = True
            continue
        seen.add(num)
        unique.append(r)

    db["clients"] = unique

    if fixed:
        save_database(db)

    return fixed


# ============================================================================
# 🚨 ANALYSE DES INCOHERENCES METIER
# ============================================================================
def analyse_incoherences():
    """
    Retourne une liste de messages d'incohérences métier (statuts / escrow / acomptes).
    """
    try:
        db = load_database()
    except Exception:
        return []

    alerts = []
    clients = db.get("clients", [])

    for r in clients:
        if not isinstance(r, dict):
            continue

        num = r.get("Dossier N", "??")
        prefix = f"Dossier {num} : "

        # Statuts
        envoye = r.get("Dossier envoye", False)
        accepte = r.get("Dossier accepte", False)
        refuse = r.get("Dossier refuse", False)
        annule = r.get("Dossier Annule", False)
        rfe = r.get("RFE", False)

        escrow = r.get("Escrow", False)
        escrow_a_reclamer = r.get("Escrow_a_reclamer", False)
        escrow_reclame = r.get("Escrow_reclame", False)

        # Montants facturés
        total = (r.get("Montant honoraires (US $)", 0) or 0) + \
                (r.get("Autres frais (US $)", 0) or 0)

        acomptes = sum([
            float(r.get(f"Acompte {i}", 0) or 0) for i in range(1, 5)
        ])

        # Règles métier
        if acomptes > total + 0.01:
            alerts.append(prefix + "Acomptes supérieurs au total facturé.")

        if (accepte or refuse or annule) and not envoye:
            alerts.append(prefix + "Statut final actif mais dossier non envoyé.")

        if sum([accepte, refuse, annule]) > 1:
            alerts.append(prefix + "Plusieurs statuts finaux actifs simultanément.")

        if envoye and escrow:
            alerts.append(prefix + "Dossier envoyé mais toujours en Escrow.")

        if escrow_reclame and not escrow_a_reclamer:
            alerts.append(prefix + "Escrow réclamé alors qu'il n'était pas à réclamer.")

        if escrow_a_reclamer and not envoye:
            alerts.append(prefix + "Escrow à réclamer mais dossier non envoyé.")

    return alerts