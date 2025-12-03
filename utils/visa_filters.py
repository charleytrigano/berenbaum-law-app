import pandas as pd

# ---------------------------------------------------------
# 🔧 Nettoyage des colonnes du tableau VISA
# ---------------------------------------------------------
def clean_visa_df(dfv):

    if dfv is None or dfv.empty:
        return pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

    rename_map = {}

    for col in dfv.columns:
        c = col.lower().replace("é", "e").replace("è", "e").replace("ê", "e")

        # IMPORTANT : détecter "sous" AVANT "categorie"
        if "sous" in c:
            rename_map[col] = "Sous-categories"

        elif c.startswith("categorie") or c == "categories":
            rename_map[col] = "Categories"

        elif "visa" in c:
            rename_map[col] = "Visa"

    # Appliquer renommage
    dfv = dfv.rename(columns=rename_map)

    # Sécurisation : garantir les 3 colonnes
    for col in ["Categories", "Sous-categories", "Visa"]:
        if col not in dfv.columns:
            dfv[col] = ""

    return dfv


# ---------------------------------------------------------
# Retourne l’arbre Cat → Sous-cat → Visas
# ---------------------------------------------------------
def get_visa_tree(dfv):

    dfv = clean_visa_df(dfv)
    tree = {}

    for _, row in dfv.iterrows():
        cat = str(row["Categories"]).strip()
        sous = str(row["Sous-categories"]).strip()
        visa = str(row["Visa"]).strip()

        if not cat:
            continue

        tree.setdefault(cat, {})
        tree[cat].setdefault(sous, [])

        if visa and visa not in tree[cat][sous]:
            tree[cat][sous].append(visa)

    return tree


# ---------------------------------------------------------
# Listes simples
# ---------------------------------------------------------
def get_all_lists(dfv):
    dfv = clean_visa_df(dfv)
    cat = sorted(dfv["Categories"].dropna().astype(str).unique())
    sous = sorted(dfv["Sous-categories"].dropna().astype(str).unique())
    vis = sorted(dfv["Visa"].dropna().astype(str).unique())
    return cat, sous, vis


# ---------------------------------------------------------
# Obtenir sous-catégories pour une catégorie
# ---------------------------------------------------------
def get_souscats(dfv, categorie):
    dfv = clean_visa_df(dfv)
    return sorted(dfv[dfv["Categories"] == categorie]["Sous-categories"]
                  .dropna().astype(str).unique().tolist())


# ---------------------------------------------------------
# Obtenir visas pour une sous-catégorie
# ---------------------------------------------------------
def get_visas(dfv, souscat):
    dfv = clean_visa_df(dfv)
    return sorted(dfv[dfv["Sous-categories"] == souscat]["Visa"]
                  .dropna().astype(str).unique().tolist())
