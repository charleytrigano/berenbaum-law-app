import pandas as pd

# ---------------------------------------------------------
# NORMALISATION TABLE VISA
# ---------------------------------------------------------
def clean_visa_df(dfv):
    """Nettoie et normalise entièrement la table VISA."""

    if dfv is None or dfv.empty:
        return pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

    dfv = dfv.copy()

    # ---- Normalisation des noms de colonnes ----
    rename_map = {}
    for col in dfv.columns:
        col_clean = (
            col.lower()
               .replace("é", "e")
               .replace("è", "e")
               .replace("ê", "e")
               .replace("ï", "i")
               .replace("_", "")
               .strip()
        )

        if "categorie" in col_clean:
            rename_map[col] = "Categories"
        elif "sous" in col_clean:
            rename_map[col] = "Sous-categories"
        elif "visa" in col_clean:
            rename_map[col] = "Visa"

    dfv = dfv.rename(columns=rename_map)

    # ---- Supprimer anciennes colonnes incorrectes ----
    for bad in ["Catégories", "Sous-catégories"]:
        if bad in dfv.columns:
            dfv = dfv.drop(columns=[bad])

    # ---- Colonnes obligatoires ----
    for c in ["Categories", "Sous-categories", "Visa"]:
        if c not in dfv.columns:
            dfv[c] = ""

    # ---- Nettoyage des valeurs ----
    dfv["Categories"] = dfv["Categories"].astype(str).str.strip()
    dfv["Sous-categories"] = dfv["Sous-categories"].astype(str).str.strip()
    dfv["Visa"] = dfv["Visa"].astype(str).str.strip()

    # ---- Retirer les lignes vides ----
    dfv = dfv[
        (dfv["Categories"] != "") |
        (dfv["Sous-categories"] != "") |
        (dfv["Visa"] != "")
    ]

    return dfv


# ---------------------------------------------------------
# LISTES FILTRÉES
# ---------------------------------------------------------
def get_categories(dfv):
    return sorted(dfv["Categories"].dropna().unique().tolist())

def get_souscats(dfv, category=None):
    if category:
        return sorted(
            dfv[dfv["Categories"] == category]["Sous-categories"]
            .dropna().unique().tolist()
        )
    return sorted(dfv["Sous-categories"].dropna().unique().tolist())

def get_visas(dfv, souscat=None, category=None):
    if souscat:
        return sorted(
            dfv[dfv["Sous-categories"] == souscat]["Visa"]
            .dropna().unique().tolist()
        )
    if category:
        return sorted(
            dfv[dfv["Categories"] == category]["Visa"]
            .dropna().unique().tolist()
        )
    return sorted(dfv["Visa"].dropna().unique().tolist())
