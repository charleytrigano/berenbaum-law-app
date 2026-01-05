from datetime import datetime


def add_escrow_history(
    db,
    dossier_n,
    ancien_etat,
    nouvel_etat,
    montant,
    action
):
    """
    Ajoute une ligne d'historique escrow.
    """
    history = db.get("escrow_history", [])

    history.append({
        "Dossier N": str(dossier_n),
        "Ancien état": ancien_etat,
        "Nouvel état": nouvel_etat,
        "Montant": round(float(montant or 0), 2),
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Action": action,
    })

    db["escrow_history"] = history