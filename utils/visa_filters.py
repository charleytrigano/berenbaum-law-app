def clean_visa_df(dfv):
    import pandas as pd

    if dfv is None or dfv.empty:
        return pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

    new_cols = {}

    for col in dfv.columns:
        c = col.lower()
        c = (c.replace("é", "e")
               .replace("è", "e")
               .replace("ê", "e")
               .replace("_", "-")
               .strip())

        if "category" in c:   # ← accepte toutes les variantes
            new_cols[col] = "Categories"

        elif "sous" in c or "sub" in c:   # ← accepte sous-categorie, sous-cat, sousCateg, etc.
            new_cols[col] = "Sous-categories"

        elif "visa" in c:
            new_cols[col] = "Visa"

    dfv = dfv.rename(columns=new_cols)

    # Supprime les anciennes colonnes typiques
    drop_cols = [x for x in dfv.columns if x not in ["Categories", "Sous-categories", "Visa"]]
    # On ne supprime que si c’est 100% inutile
    # if needed: dfv = dfv.drop(columns=drop_cols)

    # Ajoute colonnes obligatoires
    for col in ["Categories", "Sous-categories", "Visa"]:
        if col not in dfv.columns:
            dfv[col] = ""

    return dfv
