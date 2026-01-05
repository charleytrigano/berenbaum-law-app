def compute_escrow_amount(dossier: dict) -> float:
    """
    Tant que le dossier n'est PAS accepté / refusé / annulé :
    -> tous les acomptes sont en escrow
    Dès qu'un de ces statuts est TRUE :
    -> escrow = 0
    """

    def to_float(v):
        try:
            return float(v or 0)
        except:
            return 0.0

    # Statuts finaux = sortie d'escrow
    if (
        dossier.get("Dossier accepte")
        or dossier.get("Dossier refuse")
        or dossier.get("Dossier Annule")
    ):
        return 0.0

    # Sinon : tous les acomptes vont en escrow
    total = 0.0
    for i in range(1, 5):
        total += to_float(dossier.get(f"Acompte {i}"))

    return total
