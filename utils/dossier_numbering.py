import re


def split_dossier_id(dossier_id: str):
    """
    Retourne (parent:int, suffix:int)
    12937     -> (12937, 0)
    12937-1   -> (12937, 1)
    """
    s = str(dossier_id)
    if "-" in s:
        p, suf = s.split("-", 1)
        return int(p), int(suf)
    return int(s), 0


def sort_dossiers(ids):
    """
    Trie correctement : 12937, 12937-1, 12937-2, 12938
    """
    return sorted(ids, key=lambda x: split_dossier_id(x))


def next_sub_dossier(existing_ids, parent_id):
    """
    Calcule le prochain suffixe disponible pour un parent
    """
    parent_id = str(parent_id)
    suffixes = []

    for d in existing_ids:
        d = str(d)
        if d.startswith(parent_id + "-"):
            try:
                suffixes.append(int(d.split("-")[1]))
            except:
                pass

    return max(suffixes) + 1 if suffixes else 1
