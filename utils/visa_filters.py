import pandas as pd

# ---------------------------------------------------------
# Nettoyage complet du tableau VISA
# ---------------------------------------------------------
def clean_visa_df(dfv):

    if dfv is None or dfv.empty:
        return pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

    # Normalisation intelligente des colonnes
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

        if "categorie" in col_clean:
            rename_map[col] = "Categories"
        elif "sous" in col_clean:
            rename_map[col] = "Sous-categories"
        elif "visa" in col_clean:
            rename_map[col] = "Visa"

    dfv = dfv.rename(columns=rename_map)

    # Nettoyage : supprimer les anciennes colonnes
    for bad in ["Catégories", "Sous-catégories"]:
        if bad in dfv.columns:
            dfv = dfv.drop(columns=[bad])

    # Colonnes obligatoires
    for c in ["Categories", "Sous-categories", "Visa"]:
        if c not in dfv.columns:
            dfv[c] = ""

    # Retirer les lignes vides
    dfv = dfv.dropna(how="all")

    return dfv


# ---------------------------------------------------------
# Retourne les sous-catégories d’une catégorie
# ---------------------------------------------------------
def get_souscats(dfv, categorie):
    dfv = clean_visa_df(dfv)
    return sorted(
        dfv[dfv["Categories"] == categorie]["Sous-categories"]
        .dropna().astype(str).unique().tolist()
    )


# ---------------------------------------------------------
# Retourne les visas pour une sous-catégorie donnée
# ---------------------------------------------------------
def get_visas(dfv, souscat):
    dfv = clean_visa_df(dfv)
    return sorted(
        dfv[dfv["Sous-categories"] == souscat]["Visa"]
        .dropna().astype(str).unique().tolist()
    )


# ---------------------------------------------------------
# Retourne les 3 listes complètes (cat / souscat / visa)
# ---------------------------------------------------------
def get_all_lists(dfv):
    dfv = clean_visa_df(dfv)

    cat_list = sorted(dfv["Categories"].dropna().astype(str).unique().tolist())
    souscat_list = sorted(dfv["Sous-categories"].dropna().astype(str).unique().tolist())
    visa_list = sorted(dfv["Visa"].dropna().astype(str).unique().tolist())

    return cat_list, souscat_list, visa_list
