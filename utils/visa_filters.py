import pandas as pd

# Nettoyage complet et stable
def clean_visa_df(dfv):

    if dfv is None or dfv.empty:
        return pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

    dfv = dfv.copy()

    # Normalisation des noms
    rename_map = {}
    for col in dfv.columns:
        col_clean = (
            col.lower()
               .strip()
               .replace("é", "e")
               .replace("è", "e")
               .replace("ê", "e")
        )

        if "categories" in col_clean:
            rename_map[col] = "Categories"
        elif "sous-categories" in col_clean or "sous categorie" in col_clean:
            rename_map[col] = "Sous-categories"
        elif "visa" in col_clean:
            rename_map[col] = "Visa"

    dfv = dfv.rename(columns=rename_map)

    # Supprimer colonnes doublons
    for bad in ["Catégories", "Sous-catégories"]:
        if bad in dfv.columns:
            dfv = dfv.drop(columns=[bad])

    # Colonnes obligatoires
    for c in ["Categories", "Sous-categories", "Visa"]:
        if c not in dfv.columns:
            dfv[c] = ""

    # Ne garder QUE les 3 colonnes utiles
    dfv = dfv[["Categories", "Sous-categories", "Visa"]]

    return dfv


def get_souscats(dfv, category):
    dfv = clean_visa_df(dfv)
    return sorted(dfv[dfv["Categories"] == category]["Sous-categories"].dropna().unique())


def get_visas(dfv, category, souscat):
    dfv = clean_visa_df(dfv)
    return sorted(
        dfv[(dfv["Categories"] == category) & (dfv["Sous-categories"] == souscat)]["Visa"]
        .dropna()
        .unique()
    )


def get_all_lists(dfv):
    dfv = clean_visa_df(dfv)
    cats = sorted(dfv["Categories"].dropna().unique())
    sous = sorted(dfv["Sous-categories"].dropna().unique())
    visas = sorted(dfv["Visa"].dropna().unique())
    return cats, sous, visas
