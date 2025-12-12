# utils/timeline_builder.py
from datetime import datetime

def safe_date(val):
    if not val or val in ["", "None"]:
        return None
    try:
        return datetime.fromisoformat(str(val))
    except Exception:
        return None


def build_timeline(dossier: dict):
    """
    Construit la timeline chronologique d’un dossier
    Retourne une liste triée d’événements
    """
    events = []

    def add(date, label, amount=None, extra=None):
        if date:
            events.append({
                "date": date,
                "label": label,
                "amount": amount,
                "extra": extra,
            })

    # Création dossier
    add(
        safe_date(dossier.get("Date")),
        "📄 Dossier créé"
    )

    # Acomptes (avec date + mode)
    for i in range(1, 5):
        amt = float(dossier.get(f"Acompte {i}", 0) or 0)
        if amt > 0:
            add(
                safe_date(dossier.get(f"Date Acompte {i}")),
                f"💰 Acompte {i} encaissé",
                amount=amt,
                extra=dossier.get("mode de paiement", "")
            )

    # Escrow — Acompte 1 uniquement
    if dossier.get("Escrow"):
        add(
            safe_date(dossier.get("Date")),
            "💼 Escrow actif",
            amount=float(dossier.get("Acompte 1", 0) or 0)
        )

    if dossier.get("Escrow_a_reclamer"):
        add(
            safe_date(dossier.get("Date envoi")),
            "📤 Escrow à réclamer",
            amount=float(dossier.get("Acompte 1", 0) or 0)
        )

    if dossier.get("Escrow_reclame"):
        add(
            safe_date(dossier.get("Date reclamation")),
            "✅ Escrow réclamé",
            amount=float(dossier.get("Acompte 1", 0) or 0)
        )

    # Statuts
    if dossier.get("Dossier envoye"):
        add(safe_date(dossier.get("Date envoi")), "📤 Dossier envoyé")

    if dossier.get("Dossier accepte"):
        add(safe_date(dossier.get("Date acceptation")), "✅ Dossier accepté")

    if dossier.get("Dossier refuse"):
        add(safe_date(dossier.get("Date refus")), "❌ Dossier refusé")

    if dossier.get("Dossier Annule"):
        add(safe_date(dossier.get("Date annulation")), "🚫 Dossier annulé")

    if dossier.get("RFE"):
        add(safe_date(dossier.get("Date reclamation")), "📎 RFE")

    # Tri chronologique
    events = sorted([e for e in events if e["date"]], key=lambda x: x["date"])

    return events