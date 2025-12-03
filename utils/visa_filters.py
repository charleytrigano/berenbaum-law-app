import pandas as pd

def clean_visa_df(dfv):
    """
    Nettoie le tableau VISA sans jamais écraser les colonnes existantes.
    Garantie :
    - Les colonnes 'Categories', 'Sous-categories', 'Visa' existent toujours.
    - On supprime toutes les colonnes parasites ('Catégories', 'Sous-catégories', etc.)
    """

    if dfv is None or dfv.empty:
        return pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

    # 1️⃣ Normaliser les noms de colonnes existants
    def normalize(col):
        col = col.strip().lower()
        col = col.replace("é", "e").replace("è", "e").replace("ê", "e")
        col = col.replace("_", "-")
        return col

    rename = {}
    for col in dfv.columns:
        col_norm = normalize(col)

        if col_norm == "categories":
            rename[col] = "Categories"
        elif col_norm == "category":
            rename[col] = "Categories"
        elif col_norm in ["sous-categories", "sous-categorie"]:
            rename[col] = "Sous-categories"
        elif col_norm == "visa":
            rename[col] = "Visa"

    dfv = dfv.rename(columns=rename)

    # 2️⃣ Supprimer les colonnes parasites SI elles existent
    for bad in ["Catégories", "Sous-catégories", "Categorie", "Sous-categorie"]:
        if bad in dfv.columns:
            dfv = dfv.drop(columns=[bad])

    # 3️⃣ Ajouter colonnes manquantes
    for needed in ["Categories", "Sous-categories", "Visa"]:
        if needed not in dfv.columns:
            dfv[needed] = ""

    # 4️⃣ Nettoyage valeurs
    dfv["Categories"] = dfv["Categories"].astype(str).str.strip()
    dfv["Sous-categories"] = dfv["Sous-categories"].astype(str).str.strip()
    dfv["Visa"] = dfv["Visa"].astype(str).str.strip()

    return dfv
