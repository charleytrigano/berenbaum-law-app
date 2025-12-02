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

    # Retirer anciennes colonnes parasites
    to_remove = ["Catégories", "Sous-catégories"]
    for c in to_remove:
        if c in dfv.columns:
            dfv = dfv.drop(columns=[c])

    # Colonnes obligatoires
    for required in ["Categories", "Sous-categories", "Visa"]:
        if required not in dfv.columns:
            dfv[required] = ""

    # Retirer lignes vides
    dfv = dfv.dropna(how="all")

    return dfv


# ---------------------------------------------------------
# Fonction de regroupement CATEGORIES → SOUS-CAT → VISA
# ---------------------------------------------------------
def get_visa_tree(dfv):
    """
    Retourne une structure :
    {
        "Affaires / Tourisme": {
            "B-1": ["B-1 COS", "B-1 EOS"],
            "B-2": ["B-2 COS", "B-2 EOS"]
        },
        "Travail": {
            "H-1B": ["H-1B Initial", "H-1B Extension"]
        }
    }
    """

    tree = {}

    for _, row in dfv.iterrows():
        cat = str(row.get("Categories", "")).strip()
        sous = str(row.get("Sous-categories", "")).strip()
        visa = str(row.get("Visa", "")).strip()

        if not cat:
            continue

        if cat not in tree:
            tree[cat] = {}

        if sous not in tree[cat]:
            tree[cat][sous] = []

        if visa and visa not in tree[cat][sous]:
            tree[cat][sous].append(visa)

    return tree


# ---------------------------------------------------------
# Génération des listes filtrées
# ---------------------------------------------------------
def get_filtered_lists(dfv):
    dfv = clean_visa_df(dfv)

    cat_list = sorted(dfv["Categories"].dropna().astype(str).unique().tolist())
    souscat_list = sorted(dfv["Sous-categories"].dropna().astype(str).unique().tolist())
    visa_list = sorted(dfv["Visa"].dropna().astype(str).unique().tolist())

    return cat_list, souscat_list, visa_list
