import pandas as pd

# ---------------------------------------------------------
# 1️⃣ Nettoyage robuste de la table VISA
# ---------------------------------------------------------
def clean_visa_df(dfv):

    if dfv is None or dfv.empty:
        return pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

    # Normalisation des noms de colonnes
    new_cols = {}

    for col in dfv.columns:
        col_clean = (
            col.lower()
               .replace("é", "e")
               .replace("è", "e")
               .replace("ê", "e")
               .replace("-", " ")
               .replace("_", " ")
               .strip()
        )

        if "categorie" in col_clean:
            new_cols[col] = "Categories"

        elif "sous" in col_clean:
            new_cols[col] = "Sous-categories"

        elif "visa" in col_clean:
            new_cols[col] = "Visa"

    dfv = dfv.rename(columns=new_cols)

    # 🔥 Supprimer toutes les colonnes non reconnues
    dfv = dfv[["Categories", "Sous-categories", "Visa"]]

    # Nettoyage textuel
    for c in ["Categories", "Sous-categories", "Visa"]:
        dfv[c] = dfv[c].astype(str).str.strip()

    dfv = dfv[dfv["Categories"] != ""]
    dfv = dfv[dfv["Visa"] != ""]

    return dfv


# ---------------------------------------------------------
# 2️⃣ Retourne toutes les listes
# ---------------------------------------------------------
def get_all_lists(dfv):
    dfv = clean_visa_df(dfv)

    cats = sorted(dfv["Categories"].unique().tolist())
    souscats = sorted(dfv["Sous-categories"].unique().tolist())
    visas = sorted(dfv["Visa"].unique().tolist())

    return cats, souscats, visas


# ---------------------------------------------------------
# 3️⃣ Sous-catégories pour une catégorie donnée
# ---------------------------------------------------------
def get_souscats(dfv, cat):
    dfv = clean_visa_df(dfv)
    return sorted(dfv[dfv["Categories"] == cat]["Sous-categories"].unique().tolist())


# ---------------------------------------------------------
# 4️⃣ Visas pour une sous-catégorie donnée
# ---------------------------------------------------------
def get_visas(dfv, souscat):
    dfv = clean_visa_df(dfv)
    return sorted(dfv[dfv["Sous-categories"] == souscat]["Visa"].unique().tolist())
