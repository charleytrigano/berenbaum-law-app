import pandas as pd

# Nettoyage minimaliste et 100% compatible
def clean_visa_df(dfv):

    if dfv is None or dfv.empty:
        return pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

    dfv = dfv.copy()

    # Normalisation des noms de colonnes
    rename_map = {}

    for col in dfv.columns:
        col_clean = col.lower().strip().replace("é", "e").replace("è", "e")

        if "categorie" in col_clean:
            rename_map[col] = "Categories"
        elif "sous" in col_clean:
            rename_map[col] = "Sous-categories"
        elif "visa" in col_clean:
            rename_map[col] = "Visa"

    dfv = dfv.rename(columns=rename_map)

    # Forcer colonnes obligatoires
    for c in ["Categories", "Sous-categories", "Visa"]:
        if c not in dfv.columns:
            dfv[c] = ""

    # Ne garder QUE les colonnes utiles
    dfv = dfv[["Categories", "Sous-categories", "Visa"]]

    return dfv


def get_souscats(dfv, category):
    dfv = clean_visa_df(dfv)
    return sorted(
        dfv[dfv["Categories"] == category]["Sous-categories"].dropna().unique().tolist()
    )


def get_visas(dfv, category, souscategory):
    dfv = clean_visa_df(dfv)
    return sorted(
        dfv[
            (dfv["Categories"] == category)
            & (dfv["Sous-categories"] == souscategory)
        ]["Visa"].dropna().unique().tolist()
    )
