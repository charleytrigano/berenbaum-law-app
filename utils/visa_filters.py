def clean_visa_df(dfv):
    dfv = dfv.copy()

    # Normaliser noms de colonnes
    new_cols = []
    for col in dfv.columns:
        c = col.lower()
        c = c.replace("é","e").replace("è","e").replace("ê","e")
        c = c.replace("categorie","categories")
        c = c.replace("sous-categorie","sous-categories")
        c = c.replace("visa","visa")
        new_cols.append(c)

    dfv.columns = new_cols

    # Colonnes obligatoires
    for col in ["categories", "sous-categories", "visa"]:
        if col not in dfv.columns:
            dfv[col] = ""

    # Nettoyage valeurs
    dfv["categories"] = dfv["categories"].astype(str).str.strip()
    dfv["sous-categories"] = dfv["sous-categories"].astype(str).str.strip()
    dfv["visa"] = dfv["visa"].astype(str).str.strip()

    # On renvoie les colonnes standardisées
    return dfv.rename(columns={
        "categories": "Categories",
        "sous-categories": "Sous-categories",
        "visa": "Visa"
    })
