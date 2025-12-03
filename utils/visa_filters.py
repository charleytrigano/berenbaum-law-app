import pandas as pd

# ---------------------------------------------------------
# Nettoyage VISAS : suppression colonnes parasites + standardisation
# ---------------------------------------------------------
def clean_visa_df(dfv):

    if dfv is None or dfv.empty:
        return pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

    # Supprimer les anciennes colonnes inutiles
    for bad in ["Catégories", "Sous-catégories"]:
        if bad in dfv.columns:
            dfv = dfv.drop(columns=[bad])

    # Normalisation des noms de colonnes sans jamais casser
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

        elif col_clean in ["sous-categories", "sous-categorie"]:
            rename_map[col] = "Sous-categories"

        elif col_clean == "visa":
            rename_map[col] = "Visa"

    dfv = dfv.rename(columns=rename_map)

    # Colonnes obligatoires
    for c in ["Categories", "Sous-categories", "Visa"]:
        if c not in dfv.columns:
            dfv[c] = ""

    # Nettoyage contenu
    dfv["Categories"] = dfv["Categories"].astype(str).str.strip()
    dfv["Sous-categories"] = dfv["Sous-categories"].astype(str).str.strip()
    dfv["Visa"] = dfv["Visa"].astype(str).str.strip()

    # Supprimer les lignes totalement vides
    dfv = dfv.dropna(how="all")

    return dfv


# ---------------------------------------------------------
# Listes de sélection pour Dashboard + Liste dossiers
# ---------------------------------------------------------

def get_all_lists(dfv):
    """Retourne (Categories, Sous-categories, Visa) propres et uniques."""
    dfv = clean_visa_df(dfv)

    cat = sorted(dfv["Categories"].dropna().unique().tolist())
    sous = sorted(dfv["Sous-categories"].dropna().unique().tolist())
    visa = sorted(dfv["Visa"].dropna().unique().tolist())

    return cat, sous, visa


def get_souscats(dfv, category):
    dfv = clean_visa_df(dfv)
    return sorted(dfv[dfv["Categories"] == category]["Sous-categories"].unique().tolist())


def get_visas(dfv, souscat):
    dfv = clean_visa_df(dfv)
    return sorted(dfv[dfv["Sous-categories"] == souscat]["Visa"].unique().tolist())
