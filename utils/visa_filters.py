import pandas as pd

# ---------------- CLEAN VISA DATAFRAME ----------------
def clean_visa_df(dfv):

    if dfv is None or dfv.empty:
        return pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

    rename_map = {}

    for col in dfv.columns:
        col_clean = col.lower().replace("é", "e").replace("è", "e").strip()

        if "categorie" in col_clean:
            rename_map[col] = "Categories"
        elif "sous" in col_clean:
            rename_map[col] = "Sous-categories"
        elif "visa" in col_clean:
            rename_map[col] = "Visa"

    dfv = dfv.rename(columns=rename_map)

    # Supprimer anciennes colonnes
    for old in ["Catégories", "Sous-catégories"]:
        if old in dfv.columns:
            dfv = dfv.drop(columns=[old])

    # Ajouter colonnes manquantes
    for col in ["Categories", "Sous-categories", "Visa"]:
        if col not in dfv.columns:
            dfv[col] = ""

    dfv["Categories"] = dfv["Categories"].astype(str).str.strip()
    dfv["Sous-categories"] = dfv["Sous-categories"].astype(str).str.strip()
    dfv["Visa"] = dfv["Visa"].astype(str).str.strip()

    return dfv


# ---------------- TREE STRUCTURE ----------------
def get_visa_tree(dfv):
    tree = {}

    for _, row in dfv.iterrows():
        cat = row["Categories"]
        sous = row["Sous-categories"]
        visa = row["Visa"]

        if cat not in tree:
            tree[cat] = {}
        if sous not in tree[cat]:
            tree[cat][sous] = []

        if visa and visa not in tree[cat][sous]:
            tree[cat][sous].append(visa)

    return tree

# ---------------- UTILITIES ----------------
def get_souscats(dfv, cat):
    return sorted(dfv[dfv["Categories"] == cat]["Sous-categories"].unique())

def get_visas(dfv, souscat):
    return sorted(dfv[dfv["Sous-categories"] == souscat]["Visa"].unique())

def get_all_lists(dfv):
    return (
        sorted(dfv["Categories"].unique()),
        sorted(dfv["Sous-categories"].unique()),
        sorted(dfv["Visa"].unique())
    )
