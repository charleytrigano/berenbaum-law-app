import pandas as pd

# ----------------------------------------
# 🔧 Normalisation des colonnes VISA
# ----------------------------------------
def clean_visa_df(dfv):

    if dfv is None or dfv.empty:
        return pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

    rename_map = {}

    for col in dfv.columns:
        col_clean = (
            col.lower()
               .replace("é", "e")
               .replace("è", "e")
               .replace("ê", "e")
               .replace("_", "-")
               .strip()
        )

        if col_clean in ["categories", "categorie"]:
            rename_map[col] = "Categories"

        elif col_clean in ["sous-categories", "sous-categorie", "sous-categ", "sous-cats"]:
            rename_map[col] = "Sous-categories"

        elif col_clean in ["visa", "visas"]:
            rename_map[col] = "Visa"

    # Applique les renommages détectés
    dfv = dfv.rename(columns=rename_map)

    # Supprime les anciennes colonnes parasites
    for old in ["Catégories", "Sous-catégories", "Sous-categorie"]:
        if old in dfv.columns:
            dfv = dfv.drop(columns=[old])

    # Ajoute colonnes manquantes
    for col in ["Categories", "Sous-categories", "Visa"]:
        if col not in dfv.columns:
            dfv[col] = ""

    # Supprime lignes vides
    dfv = dfv.dropna(how="all")

    return dfv


# ----------------------------------------
# 🔍 Retourne sous-catégories pour une catégorie
# ----------------------------------------
def get_souscategories_for_category(dfv, cat):
    dfv = clean_visa_df(dfv)
    return (
        dfv[dfv["Categories"] == cat]["Sous-categories"]
        .dropna()
        .unique()
        .tolist()
    )


# ----------------------------------------
# 🔍 Retourne visas pour une sous-catégorie
# ----------------------------------------
def get_visas_for_souscat(dfv, souscat):
    dfv = clean_visa_df(dfv)
    return (
        dfv[dfv["Sous-categories"] == souscat]["Visa"]
        .dropna()
        .unique()
        .tolist()
    )
