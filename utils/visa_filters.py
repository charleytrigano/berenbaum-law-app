import pandas as pd

# ---------------------------------------------------------
# 1) Nettoyage correct du tableau VISA
# ---------------------------------------------------------
def clean_visa_df(dfv):
    """
    Nettoie entièrement le tableau VISA et garantit
    les colonnes : Categories – Sous-categories – Visa
    """

    if dfv is None or dfv.empty:
        return pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

    # Supprime les colonnes parasites venues du JSON ou Excel
    for col in ["Catégories", "Sous-catégories", "Categorie", "Sous-categorie"]:
        if col in dfv.columns:
            dfv = dfv.drop(columns=[col])

    # Renommage intelligent
    rename_map = {}
    for col in dfv.columns:
        col_clean = (
            col.lower()
            .replace("é", "e")
            .replace("è", "e")
            .replace("ê", "e")
            .replace("ï", "i")
            .strip()
        )

        if "category" in col_clean or col_clean == "categories":
            rename_map[col] = "Categories"
        elif "sous" in col_clean:
            rename_map[col] = "Sous-categories"
        elif "visa" in col_clean:
            rename_map[col] = "Visa"

    dfv = dfv.rename(columns=rename_map)

    # Ajoute les colonnes manquantes (sécurité)
    for required in ["Categories", "Sous-categories", "Visa"]:
        if required not in dfv.columns:
            dfv[required] = ""

    # Nettoyage valeurs
    dfv["Categories"] = dfv["Categories"].astype(str).str.strip()
    dfv["Sous-categories"] = dfv["Sous-categories"].astype(str).str.strip()
    dfv["Visa"] = dfv["Visa"].astype(str).str.strip()

    # Supprime lignes vides
    dfv = dfv[(dfv["Categories"] != "") | (dfv["Sous-categories"] != "") | (dfv["Visa"] != "")]

    # Supprime doublons éventuels
    dfv = dfv.drop_duplicates()

    return dfv


# ---------------------------------------------------------
# 2) Liste des catégories uniques (propres)
# ---------------------------------------------------------
def get_categories(dfv):
    dfv = clean_visa_df(dfv)
    return sorted(dfv["Categories"].dropna().unique().tolist())


# ---------------------------------------------------------
# 3) Liste des sous-catégories dépendantes d’une catégorie
# ---------------------------------------------------------
def get_souscats(dfv, category):
    dfv = clean_visa_df(dfv)
    if not category or category == "Toutes":
        return sorted(dfv["Sous-categories"].dropna().unique().tolist())
    
    return sorted(
        dfv[dfv["Categories"] == category]["Sous-categories"]
        .dropna()
        .unique()
        .tolist()
    )


# ---------------------------------------------------------
# 4) Liste Visa dépendante d’une sous-catégorie ou d’une catégorie
# ---------------------------------------------------------
def get_visas(dfv, category=None, souscat=None):
    dfv = clean_visa_df(dfv)

    if souscat and souscat != "Toutes":
        return sorted(
            dfv[dfv["Sous-categories"] == souscat]["Visa"]
            .dropna()
            .unique()
            .tolist()
        )

    if category and category != "Toutes":
        return sorted(
            dfv[dfv["Categories"] == category]["Visa"]
            .dropna()
            .unique()
            .tolist()
        )

    return sorted(dfv["Visa"].dropna().unique().tolist())


# ---------------------------------------------------------
# 5) Tout récupérer : catégories, sous-catégories, visas
# ---------------------------------------------------------
def get_all_lists(dfv):
    dfv = clean_visa_df(dfv)

    cats = get_categories(dfv)
    sous = sorted(dfv["Sous-categories"].dropna().unique().tolist())
    visas = sorted(dfv["Visa"].dropna().unique().tolist())

    return cats, sous, visas
