from datetime import datetime

def get_tarif_for_visa(visa, date_dossier, tarifs):
    """
    Retourne le tarif applicable pour un visa à une date donnée
    """
    applicable = []

    for t in tarifs:
        if t["Visa"] != visa:
            continue

        try:
            d_effet = datetime.strptime(t["Date_effet"], "%Y-%m-%d").date()
            if d_effet <= date_dossier:
                applicable.append(t)
        except:
            continue

    if not applicable:
        return 0.0

    applicable.sort(
        key=lambda x: datetime.strptime(x["Date_effet"], "%Y-%m-%d"),
        reverse=True
    )
    return float(applicable[0]["Tarif"])
