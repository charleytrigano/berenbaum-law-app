import pandas as pd

# ---------------------------------------------------------
# Nettoyage universel du tableau VISA
# ---------------------------------------------------------
def clean_visa_df(dfv):

    if dfv is None or dfv.empty:
        return pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

    dfv = dfv.copy()

    # 🔍 Détection automatique des colonnes
    col_map = {}

    for col in dfv.columns:
        col_clean = (
            col.lower()
                .replace("é", "e")
                .replace("è", "e")
                .replace("ê", "e")
                .replace("_", "")
                .replace("-", "")
                .strip()
        )

        if col_clean in ["categories", "categorie", "category"]:
            col_map[col] = "Categories"

        elif "sous" in col_clean or "sub" in col_clean:
            col_map[col] = "Sous-categories"

        elif col_clean == "visa":
            col_map[col] = "Visa"

    # Renommage intelligent
    dfv = dfv.rename(columns=col_map)

    # Suppression colonnes parasites
    for bad in ["Catégories", "Sous-catégories"]:
        if bad in dfv.columns:
            dfv = dfv.drop(columns=[bad])

    # Colonnes obligatoires
    for req in ["Categories", "Sous-categories", "Visa"]:
        if req not in dfv.columns:
            dfv[req] = ""

    # Normalisation valeurs
    dfv["Categories"] = dfv["Categories"].astype(str).str.strip()
    dfv["Sous-categories"] = dfv["Sous-categories"].astype(str).str.strip()
    dfv["Visa"] = dfv["Visa"].astype(str).str.strip()

    # Retirer lignes vides
    dfv = dfv[(dfv["Categories"] != "") | (dfv["Sous-categories"] != "") | (dfv["Visa"] != "")]

    return dfv


# ---------------------------------------------------------
# Sous-catégories pour une catégorie
# ---------------------------------------------------------
def get_souscats(dfv, categorie):
    if not categorie:
        return []
    df2 = dfv[dfv["Categories"] == categorie]
    return sorted(df2["Sous-categories"].dropna().unique().tolist())


# ---------------------------------------------------------
# Visas pour une sous-catégorie
# ---------------------------------------------------------
def get_visas(dfv, souscat):
    if not souscat:
        return []
    df2 = dfv[dfv["Sous-categories"] == souscat]
    return sorted(df2["Visa"].dropna().unique().tolist())


# ---------------------------------------------------------
# Toutes les listes (utile Dashboard)
# ---------------------------------------------------------
def get_all_lists(dfv):
    dfv = clean_visa_df(dfv)
    cats = sorted(dfv["Categories"].dropna().unique().tolist())
    sous = sorted(dfv["Sous-categories"].dropna().unique().tolist())
    visas = sorted(dfv["Visa"].dropna().unique().tolist())
    return cats, sous, visas
