import pandas as pd

# ---------------------------------------------------------
# Nettoyage des colonnes du tableau VISA
# ---------------------------------------------------------
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
               .strip()
        )

        if "categorie" in col_clean:
            rename_map[col] = "Categories"
        elif "sous" in col_clean:
            rename_map[col] = "Sous-categories"
        elif "visa" in col_clean:
            rename_map[col] = "Visa"

    dfv = dfv.rename(columns=rename_map)

    # Colonnes obligatoires
    for col in ["Categories", "Sous-categories", "Visa"]:
        if col not in dfv.columns:
            dfv[col] = ""

    # Nettoyage valeurs
    dfv["Categories"] = dfv["Categories"].astype(str).str.strip()
    dfv["Sous-categories"] = dfv["Sous-categories"].astype(str).str.strip()
    dfv["Visa"] = dfv["Visa"].astype(str).str.strip()

    return dfv


# ---------------------------------------------------------
# Retourne les sous-catégories d'une catégorie donnée
# ---------------------------------------------------------
def get_souscats(dfv, categorie):
    if categorie is None or categorie == "":
        return []
    df2 = dfv[dfv["Categories"] == categorie]
    return sorted(df2["Sous-categories"].dropna().unique().tolist())


# ---------------------------------------------------------
# Retourne les visas d'une sous-catégorie donnée
# ---------------------------------------------------------
def get_visas(dfv, souscat):
    if souscat is None or souscat == "":
        return []
    df2 = dfv[dfv["Sous-categories"] == souscat]
    return sorted(df2["Visa"].dropna().unique().tolist())
