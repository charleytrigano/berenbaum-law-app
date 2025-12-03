import pandas as pd

# ---------------------------------------------------------
# 🔧 Nettoyage du tableau VISA
# ---------------------------------------------------------
def clean_visa_df(dfv):

    if dfv is None or dfv.empty:
        return pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

    dfv = dfv.copy()

    # Normalisation des colonnes
    rename_map = {}

    for col in dfv.columns:
        c = col.lower().strip()
        c = c.replace("é", "e").replace("è", "e").replace("ê", "e")

        if "categorie" in c and "sous" not in c:
            rename_map[col] = "Categories"
        elif "sous" in c:
            rename_map[col] = "Sous-categories"
        elif "visa" in c:
            rename_map[col] = "Visa"

    dfv = dfv.rename(columns=rename_map)

    # Colonnes obligatoires
    for col in ["Categories", "Sous-categories", "Visa"]:
        if col not in dfv.columns:
            dfv[col] = ""

    # Nettoyage des valeurs
    dfv["Categories"] = dfv["Categories"].astype(str).str.strip()
    dfv["Sous-categories"] = dfv["Sous-categories"].astype(str).str.strip()
    dfv["Visa"] = dfv["Visa"].astype(str).str.strip()

    # Suppression lignes vides
    dfv = dfv[
        (dfv["Categories"] != "") |
        (dfv["Sous-categories"] != "") |
        (dfv["Visa"] != "")
    ]

    return dfv


# ---------------------------------------------------------
# 🔧 Générer listes simples
# ---------------------------------------------------------
def get_all_lists(dfv):
    dfv = clean_visa_df(dfv)

    cats = sorted(dfv["Categories"].unique())
    sous = sorted(dfv["Sous-categories"].unique())
    visas = sorted(dfv["Visa"].unique())

    return cats, sous, visas


# ---------------------------------------------------------
# 🔧 Sous-catégories d'une catégorie
# ---------------------------------------------------------
def get_souscats(dfv, category):
    dfv = clean_visa_df(dfv)
    return sorted(dfv[dfv["Categories"] == category]["Sous-categories"].unique())


# ---------------------------------------------------------
# 🔧 Visas d'une sous-catégorie
# ---------------------------------------------------------
def get_visas(dfv, souscat):
    dfv = clean_visa_df(dfv)
    return sorted(dfv[dfv["Sous-categories"] == souscat]["Visa"].unique())
