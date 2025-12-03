import pandas as pd

# ---------------------------------------------------------
# 1️⃣ Nettoyage du tableau Visa (Excel → DataFrame)
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

    # Appliquer les renommages
    dfv = dfv.rename(columns=rename_map)

    # Supprimer DEFINITIVEMENT les anciennes colonnes incorrectes
    for old in ["Catégories", "Sous-catégories"]:
        if old in dfv.columns:
            dfv = dfv.drop(columns=[old])

    # Colonnes obligatoires
    for required in ["Categories", "Sous-categories", "Visa"]:
        if required not in dfv.columns:
            dfv[required] = ""

    # Nettoyage des valeurs
    dfv["Categories"] = dfv["Categories"].astype(str).str.strip()
    dfv["Sous-categories"] = dfv["Sous-categories"].astype(str).str.strip()
    dfv["Visa"] = dfv["Visa"].astype(str).str.strip()

    # Supprimer lignes totalement vides
    dfv = dfv.dropna(how="all")

    return dfv


# ---------------------------------------------------------
# 2️⃣ Construction de l’arbre Catégorie → Sous-catégorie → Visa
# ---------------------------------------------------------
def get_visa_tree(dfv):
    dfv = clean_visa_df(dfv)
    tree = {}

    for _, row in dfv.iterrows():
        cat = row["Categories"]
        sous = row["Sous-categories"]
        visa = row["Visa"]

        if not cat:
            continue

        tree.setdefault(cat, {})
        tree[cat].setdefault(sous, [])

        if visa and visa not in tree[cat][sous]:
            tree[cat][sous].append(visa)

    return tree


# ---------------------------------------------------------
# 3️⃣ Listes simples : catégories, sous-catégories, visas
# ---------------------------------------------------------
def get_all_lists(dfv):
    dfv = clean_visa_df(dfv)

    cat_list = sorted(dfv["Categories"].dropna().unique().tolist())
    souscat_list = sorted(dfv["Sous-categories"].dropna().unique().tolist())
    visa_list = sorted(dfv["Visa"].dropna().unique().tolist())

    return cat_list, souscat_list, visa_list


# ---------------------------------------------------------
# 4️⃣ Fonctions dépendantes
# ---------------------------------------------------------
def get_souscats(dfv, cat):
    dfv = clean_visa_df(dfv)
    return sorted(dfv[dfv["Categories"] == cat]["Sous-categories"].dropna().unique().tolist())


def get_visas(dfv, souscat):
    dfv = clean_visa_df(dfv)
    return sorted(dfv[dfv["Sous-categories"] == souscat]["Visa"].dropna().unique().tolist())
