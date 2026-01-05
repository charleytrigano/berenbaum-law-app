import pandas as pd


def _to_float(v):
    try:
        return float(v or 0)
    except Exception:
        return 0.0


def _to_date(v):
    if v in [None, "", "None"]:
        return None
    d = pd.to_datetime(v, errors="coerce")
    return None if pd.isna(d) else d


def _sum_acomptes(dossier: dict) -> float:
    return sum(_to_float(dossier.get(f"Acompte {i}", 0)) for i in range(1, 5))


def build_timeline(dossier: dict) -> list:
    """
    Timeline FACTUELLE et DATÉE (pas d'événement sans date).
    - Paiements: uniquement si montant > 0 ET date de paiement renseignée
    - Statuts: uniquement si date de statut renseignée
    - Escrow: montant = somme acomptes (1..4) selon logique métier
    """
    events = []

    def add_event(date_value, label, amount=None, meta=None):
        d = _to_date(date_value)
        if d is None:
            return
        ev = {"date": d, "label": label}
        if amount is not None:
            ev["amount"] = float(amount)
        if meta:
            ev["meta"] = meta
        events.append(ev)

    # -------------------------------------------------
    # Création
    # -------------------------------------------------
    add_event(dossier.get("Date"), "Création du dossier")

    # -------------------------------------------------
    # Paiements Acomptes (1..4) - uniquement si datés
    # -------------------------------------------------
    for i in range(1, 5):
        montant = _to_float(dossier.get(f"Acompte {i}", 0))
        date_pay = dossier.get(f"Date Acompte {i}", "")
        mode = dossier.get(f"Mode Acompte {i}", "") or dossier.get("mode de paiement", "")

        if montant > 0 and date_pay:
            add_event(
                date_pay,
                f"Paiement Acompte {i}",
                amount=montant,
                meta=f"Mode : {mode}" if mode else None,
            )

    # -------------------------------------------------
    # Statuts (uniquement si date)
    # -------------------------------------------------
    add_event(dossier.get("Date envoi"), "Dossier envoyé")
    add_event(dossier.get("Date acceptation"), "Dossier accepté")
    add_event(dossier.get("Date refus"), "Dossier refusé")
    add_event(dossier.get("Date annulation"), "Dossier annulé")
    add_event(dossier.get("Date reclamation"), "RFE")

    # -------------------------------------------------
    # Escrow (montant = somme acomptes 1..4)
    # Logique attendue:
    # - Escrow actif tant que pas accepté/refusé/annulé
    # - à réclamer quand accepté/refusé/annulé (date = date du statut déclencheur si dispo)
    # - réclamé date = Date reclamation si tu l'utilises ainsi (sinon à adapter)
    # -------------------------------------------------
    escrow_amount = _sum_acomptes(dossier)

    if escrow_amount > 0:
        if bool(dossier.get("Escrow", False)):
            add_event(dossier.get("Date"), "Escrow actif", amount=escrow_amount)

        trigger_date = (
            dossier.get("Date acceptation")
            or dossier.get("Date refus")
            or dossier.get("Date annulation")
        )

        if bool(dossier.get("Escrow_a_reclamer", False)):
            add_event(trigger_date, "Escrow à réclamer", amount=escrow_amount)

        if bool(dossier.get("Escrow_reclame", False)):
            # Si tu as une date dédiée à l'encaissement / réclamation escrow,
            # remplace Date reclamation par le champ correct.
            add_event(dossier.get("Date reclamation"), "Escrow réclamé", amount=escrow_amount)

    # -------------------------------------------------
    # Tri chrono
    # -------------------------------------------------
    events.sort(key=lambda x: x["date"])
    return events