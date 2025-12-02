import pandas as pd

def clean_visa_df(dfv):
    """Normalise toutes les colonnes du tableau Visa."""
    if dfv is None or dfv.empty:
        return pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

    rename_map = {}

    for col in dfv.columns:
        col_clean = col.lower().replace("é", "e").replace("è", "e").strip()

        if col_clean in ["categories", "categorie"]:
            rename_map[col] = "Categories"
        elif col_clean in ["sous-categories", "sous-categorie"]:
            rename_map[col] = "Sous-categories"
        elif col_clean == "visa":
            rename_map[col] = "Visa"

    dfv = dfv.rename(columns=rename_map)

    # Colonnes obligatoires
    for c in ["Categories", "Sous-categories", "Visa"]:
        if c not in dfv.columns:
            dfv[c] = ""

    return dfv


def get_filtered_lists(dfv, cat=None, souscat=None):
    """Retourne les listes Catégories, Sous-catégories et Visa selon les filtres actifs."""

    if dfv is None or dfv.empty:
        return [], [], []

    dfv = clean_visa_df(dfv)

    # Liste catégories
    categories = sorted(dfv["Categories"].dropna().unique().tolist())

    # Liste sous-catégories dépendante
    if cat and cat != "Toutes":
        souscats = sorted(dfv[dfv["Categories"] == cat]["Sous-categories"].dropna().unique().tolist())
    else:
        souscats = sorted(dfv["Sous-categories"].dropna().unique().tolist())

    # Liste Visa dépendante
    if souscat and souscat != "Toutes":
        visas = sorted(dfv[dfv["Sous-categories"] == souscat]["Visa"].dropna().unique().tolist())
    elif cat and cat != "Toutes":
        visas = sorted(dfv[dfv["Categories"] == cat]["Visa"].dropna().unique().tolist())
    else:
        visas = sorted(dfv["Visa"].dropna().unique().tolist())

    return categories, souscats, visas
