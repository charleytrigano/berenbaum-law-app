import re

def parse_dossier_number(dossier_n):
    """
    Retourne (parent:int, index:int)
    12937      -> (12937, 0)
    12937-2    -> (12937, 2)
    """
    if dossier_n is None:
        return None, None

    s = str(dossier_n).strip()

    match = re.match(r"^(\d+)(?:-(\d+))?$", s)
    if not match:
        return None, None

    parent = int(match.group(1))
    index = int(match.group(2)) if match.group(2) else 0

    return parent, index


def next_sub_dossier_number(clients, parent):
    """
    Retourne le prochain numéro disponible : parent-X
    """
    indexes = []

    for c in clients:
        p, i = parse_dossier_number(c.get("Dossier N"))
        if p == parent:
            indexes.append(i)

    next_index = max(indexes) + 1 if indexes else 1
    return f"{parent}-{next_index}"
