from datetime import datetime
import pandas as pd


def build_timeline(dossier: dict) -> list:
    """
    Construit une timeline STRICTEMENT basée sur des faits réels et datés.
    """
    events = []

    def add_event(date, label, amount=None, meta=None):
        if not date:
            return
        try:
            d = pd.to_datetime(date)
        except:
            return

        ev = {
            "date": d,
            "label": label
        }
        if amount is not None:
            ev["amount"] = amount
        if meta:
            ev["meta"] = meta

        events.append(ev)

    # -------------------------------------------------
    # Création du dossier
    # -------------------------------------------------
    add_event(
        dossier.get("Date"),
        "Création du dossier"
    )

    # -------------------------------------------------
    # Paiements (Acomptes)
    # -------------------------------------------------
    for i in range(1, 5):
        montant = dossier.get(f"Acompte {i}")
        date_pay = dossier.get(f"Date Acompte {i}")
        mode = dossier.get(f"Mode Acompte {i}") or dossier.get("mode de paiement")

        try:
            montant = float(montant or 0)
        except:
            montant = 0

        if montant > 0 and date_pay:
            add_event(
                date_pay,
                f"Paiement Acompte {i}",
                amount=montant,
                meta=f"Mode : {mode}"
            )

    # -------------------------------------------------
    # Statuts administratifs
    # -------------------------------------------------
    status_map = [
        ("Date envoi", "Dossier envoyé"),
        ("Date acceptation", "Dossier accepté"),
        ("Date refus", "Dossier refusé"),
        ("Date annulation", "Dossier annulé"),
        ("Date reclamation", "RFE")
    ]

    for date_field, label in status_map:
        add_event(dossier.get(date_field), label)

    # -------------------------------------------------
    # Escrow (logique métier)
    # -------------------------------------------------
    total_acomptes = 0.0
    for i in range(1, 5):
        try:
            total_acomptes += float(dossier.get(f"Acompte {i}") or 0)
        except:
            pass

    if total_acomptes > 0:
        if dossier.get("Escrow"):
            add_event(
                dossier.get("Date"),
                "Escrow actif",
                amount=total_acomptes
            )

        if dossier.get("Escrow_a_reclamer"):
            add_event(
                dossier.get("Date acceptation") or dossier.get("Date refus") or dossier.get("Date annulation"),
                "Escrow à réclamer",
                amount=total_acomptes
            )

        if dossier.get("Escrow_reclame"):
            add_event(
                dossier.get("Date reclamation"),
                "Escrow réclamé",
                amount=total_acomptes
            )

    # -------------------------------------------------
    # TRI FINAL
    # -------------------------------------------------
    events = sorted(events, key=lambda x: x["date"])

    return events