import pandas as pd

# ---------------------------------------------------------
# Nettoyage BASIC du tableau VISA
# ---------------------------------------------------------
def clean_visa_df(dfv):

    if dfv is None or dfv.empty:
        return pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

    # On force seulement l’existence et l’ordre des colonnes
    cols = ["Categories", "Sous-categories", "Visa"]
    df = dfv.copy()

    # Ajoute une colonne manquante si nécessaire
    for c in cols:
        if c not in df.columns:
            df[c] = ""

    # Réduit le tableau aux colonnes correctes
    df = df[cols]

    # Nettoyage simple des espaces
    df["Categories"] = df["Categories"].astype(str).str.strip()
    df["Sous-categories"] = df["Sous-categories"].astype(str).str.strip()
    df["Visa"] = df["Visa"].astype(str).str.strip()

    return df


# ---------------------------------------------------------
# Listes CAT / SOUS-CAT / VISA
# ---------------------------------------------------------
def get_all_lists(dfv):
    df = clean_visa_df(dfv)

    cat_list = sorted(df["Categories"].dropna().unique().tolist())
    souscat_list = sorted(df["Sous-categories"].dropna().unique().tolist())
    visa_list = sorted(df["Visa"].dropna().unique().tolist())

    return cat_list, souscat_list, visa_list


# ---------------------------------------------------------
# Récupérer sous-catégories selon une catégorie
# ---------------------------------------------------------
def get_souscats(dfv, cat):
    df = clean_visa_df(dfv)
    return sorted(df[df["Categories"] == cat]["Sous-categories"].dropna().unique().tolist())


# ---------------------------------------------------------
# Récupérer visas selon une sous-catégorie
# ---------------------------------------------------------
def get_visas(dfv, souscat):
    df = clean_visa_df(dfv)
    return sorted(df[df["Sous-categories"] == souscat]["Visa"].dropna().unique().tolist())
