import json
from datetime import datetime

import pandas as pd

from backend.dropbox_utils import load_database, save_database


# ---------------------------------------------------------
# 🔧 Validation + réparation "structurelles" du JSON
# ---------------------------------------------------------
def validate_and_fix_json() -> bool:
    """
    Valide et répare la base JSON si nécessaire.
    Retourne True si des corrections ont été appliquées, False sinon.
    """
    try:
        db = load_database()
    except Exception:
        # Si on ne peut pas charger, on ne fait rien
        return False

    if not isinstance(db, dict):
        db = {}
        fixed = True
    else:
        fixed = False

    # Garantir la présence des clés principales
    for key in ["clients", "visa", "escrow", "compta"]:
        if key not in db or not isinstance(db.get(key), list):
            db[key] = []
            fixed = True

    # Normalisation de base sur les clients
    clients = db.get("clients", [])
    normalized_clients = []

    for row in clients:
        if not isinstance(row, dict):
            fixed = True
            continue

        r = row.copy()

        # Harmonisation du nom de colonne "Dossier envoye"
        if "Dossier_envoye" in r and "Dossier envoye" not in r:
            r["Dossier envoye"] = r.pop("Dossier_envoye")
            fixed = True

        # Normalisation des booléens
        def to_bool(v):
            if isinstance(v, bool):
                return v
            if str(v).lower() in ["true", "1", "yes", "oui"]:
                return True
            return False

        for key in [
            "Escrow",
            "Escrow_a_reclamer",
            "Escrow_reclame",
            "Dossier envoye",
            "Dossier accepte",
            "Dossier refuse",
            "Dossier Annule",
            "RFE",
        ]:
            if key in r:
                r[key] = to_bool(r.get(key, False))

        # Dates → str ISO ou None
        for key in list(r.keys()):
            if "Date" in key:
                try:
                    d = pd.to_datetime(r[key], errors="coerce")
                    r[key] = None if pd.isna(d) else str(d.date())
                except Exception:
                    r[key] = None
                fixed = True

        # Revenus numériques
        for key in ["Montant honoraires (US $)", "Autres frais (US $)"]:
            try:
                r[key] = float(r.get(key, 0) or 0)
            except Exception:
                r[key] = 0.0
                fixed = True

        # Acomptes
        for i in range(1, 5):
            k = f"Acompte {i}"
            try:
                r[k] = float(r.get(k, 0) or 0)
            except Exception:
                r[k] = 0.0
                fixed = True

        # Champs texte obligatoires
        for key in ["Categories", "Sous-categories", "Visa", "Commentaire"]:
            if key not in r or r[key] is None:
                r[key] = ""
                fixed = True

        normalized_clients.append(r)

    # Suppression des doublons de "Dossier N"
    seen = set()
    unique_clients = []
    for r in normalized_clients:
        dossier_num = r.get("Dossier N")
        if dossier_num in seen:
            fixed = True
            continue
        seen.add(dossier_num)
        unique_clients.append(r)

    db["clients"] = unique_clients

    if fixed:
        save_database(db)

    return fixed


# ---------------------------------------------------------
# 🚨 Détection d'incohérences métier
# ---------------------------------------------------------
def analyse_incoherences():
    """
    Analyse les dossiers et retourne une liste de messages d'alerte
    décrivant les incohérences détectées.
    """
    try:
        db = load_database()
    except Exception:
        return []

    alerts = []
    clients = db.get("clients", [])

    for row in clients:
        if not isinstance(row, dict):
            continue

        num = row.get("Dossier N", "??")
        prefix = f"Dossier {num} : "

        # Flags de statuts
        envoye = bool(row.get("Dossier envoye") or row.get("Dossier_envoye"))
        accepte = bool(row.get("Dossier accepte"))
        refuse = bool(row.get("Dossier refuse"))
        annule = bool(row.get("Dossier Annule"))
        rfe = bool(row.get("RFE"))

        escrow = bool(row.get("Escrow"))
        escrow_a_reclamer = bool(row.get("Escrow_a_reclamer"))
        escrow_reclame = bool(row.get("Escrow_reclame"))

        # Montants
        try:
            honoraires = float(row.get("Montant honoraires (US $)", 0) or 0)
        except Exception:
            honoraires = 0.0

        try:
            frais = float(row.get("Autres frais (US $)", 0) or 0)
        except Exception:
            frais = 0.0

        total = honoraires + frais

        acomptes = 0.0
        for i in range(1, 5):
            try:
                acomptes += float(row.get(f"Acompte {i}", 0) or 0)
            except Exception:
                pass

        # 1) Acomptes > total facturé
        if acomptes > total + 0.01:
            alerts.append(
                prefix
                + f"Acomptes ({acomptes:.2f} $) supérieurs au total facturé ({total:.2f} $)."
            )

        # 2) Dossier accepté / refusé / annulé mais pas envoyé
        if (accepte or refuse or annule) and not envoye:
            alerts.append(
                prefix
                + "Statut final (accepté / refusé / annulé) actif alors que le dossier n'est pas marqué comme envoyé."
            )

        # 3) Plusieurs statuts finaux simultanés
        if sum([accepte, refuse, annule]) > 1:
            alerts.append(
                prefix
                + "Plusieurs statuts finaux sont actifs en même temps (accepté / refusé / annulé)."
            )

        # 4) Escrow incohérent avec l'envoi
        if envoye and escrow:
            alerts.append(
                prefix
                + "Dossier envoyé mais toujours en 'Escrow en cours' (Escrow=True)."
            )

        # 5) Escrow réclamé alors que rien n'est à réclamer
        if escrow_reclame and not escrow_a_reclamer:
            alerts.append(
                prefix
                + "Escrow marqué comme réclamé alors qu'il n'est pas en 'Escrow à réclamer'."
            )

        # 6) Escrow à réclamer alors que le dossier n'est pas envoyé
        if escrow_a_reclamer and not envoye:
            alerts.append(
                prefix
                + "Escrow à réclamer mais le dossier n'est pas marqué comme envoyé."
            )

    return alerts