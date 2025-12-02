import pandas as pd

# ---------------------------------------------------------
# Nettoyage / normalisation du DataFrame VISA
# ---------------------------------------------------------
def clean_visa_df(dfv):
    if dfv is None or dfv.empty:
        return pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

    # Normalisation des noms de colonnes
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

    # Supprimer les anciennes colonnes
    for old in ["Catégories", "Sous-catégories"]:
        if old in dfv.columns:
            dfv = dfv.drop(columns=[old])

    # Colonnes obligatoires
    for c in ["Categories", "Sous-categories", "Visa"]:
        if c not in dfv.columns:
            dfv[c] = ""

    return dfv


# ---------------------------------------------------------
# Génération des listes de filtres dépendantes
# ---------------------------------------------------------
def get_filtered_lists(dfv, cat_selected=None, souscat_selected=None):
    """Retourne la liste des Catégories, Sous-catégories et Visa filtrées."""

    dfv = clean_visa_df(dfv)

    # --- Liste catégories ---
    cat_list = sorted(dfv["Categories"].dropna().unique().tolist())

    # --- Liste sous-catégories dépendantes ---
    if cat_selected and cat_selected != "Toutes":
        souscat_list = sorted(
            dfv[dfv["Categories"] == cat_selected]["Sous-categories"]
            .dropna().unique().tolist()
        )
    else:
        souscat_list = sorted(dfv["Sous-categories"].dropna().unique().tolist())

    # --- Liste visas dépendante ---
    if souscat_selected and souscat_selected != "Toutes":
        visa_list = sorted(
            dfv[dfv["Sous-categories"] == souscat_selected]["Visa"]
            .dropna().unique().tolist()
        )
    elif cat_selected and cat_selected != "Toutes":
        visa_list = sorted(
            dfv[dfv["Categories"] == cat_selected]["Visa"]
            .dropna().unique().tolist()
        )
    else:
        visa_list = sorted(dfv["Visa"].dropna().unique().tolist())

    return cat_list, souscat_list, visa_list
