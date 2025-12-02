import pandas as pd

# --------------------------------------------------------------------
# 🔧 Normalisation du DataFrame Visa (colonnes, doublons, nettoyage)
# --------------------------------------------------------------------
def clean_visa_df(dfv: pd.DataFrame) -> pd.DataFrame:
    if dfv is None or dfv.empty:
        return pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

    rename_map = {}
    for col in dfv.columns:
        cleaned = col.lower().replace("é", "e").replace("è", "e").strip()

        if cleaned in ["categories", "categorie"]:
            rename_map[col] = "Categories"
        elif cleaned in ["sous-categories", "sous-categorie"]:
            rename_map[col] = "Sous-categories"
        elif cleaned == "visa":
            rename_map[col] = "Visa"

    dfv = dfv.rename(columns=rename_map)

    # Suppression colonnes parasites éventuelles
    for old in ["Catégories", "Sous-catégories"]:
        if old in dfv.columns:
            dfv = dfv.drop(columns=[old])

    # Colonnes obligatoires
    for c in ["Categories", "Sous-categories", "Visa"]:
        if c not in dfv.columns:
            dfv[c] = ""

    # Suppression doublons
    dfv = dfv.drop_duplicates(subset=["Categories", "Sous-categories", "Visa"], keep="first")

    return dfv


# --------------------------------------------------------------------
# 🔧 Génération listes: Cat → Souscat → Visa
# --------------------------------------------------------------------
def get_filtered_lists(dfv: pd.DataFrame):
    """Retourne les listes complètes : catégories, sous-catégories, visas."""
    dfv = clean_visa_df(dfv)

    cat_list = sorted(dfv["Categories"].dropna().unique().tolist())
    souscat_list = sorted(dfv["Sous-categories"].dropna().unique().tolist())
    visa_list = sorted(dfv["Visa"].dropna().unique().tolist())

    return cat_list, souscat_list, visa_list


# --------------------------------------------------------------------
# 🔧 Sous-catégories dépendantes
# --------------------------------------------------------------------
def get_souscategories_for_category(dfv: pd.DataFrame, category: str):
    dfv = clean_visa_df(dfv)
    return sorted(dfv[dfv["Categories"] == category]["Sous-categories"].dropna().unique().tolist())


# --------------------------------------------------------------------
# 🔧 Visa dépendant
# --------------------------------------------------------------------
def get_visas_for_souscat(dfv: pd.DataFrame, souscat: str):
    dfv = clean_visa_df(dfv)
    return sorted(dfv[dfv["Sous-categories"] == souscat]["Visa"].dropna().unique().tolist())
