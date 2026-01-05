
from datetime import datetime

def log_escrow_history(
    db,
    dossier,
    ancien_etat,
    nouvel_etat,
    montant,
    cause
):
    """
    Ajoute une entrée d'historique escrow dans la base.
    """
    if "escrow_history" not in db:
        db["escrow_history"] = []

    entry = {
        "Dossier N": str(dossier.get("Dossier N", "")),
        "Nom": dossier.get("Nom", ""),
        "Ancien_etat": ancien_etat,
        "Nouvel_etat": nouvel_etat,
        "Montant": float(montant or 0),
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Cause": cause,
    }

    db["escrow_history"].append(entry)