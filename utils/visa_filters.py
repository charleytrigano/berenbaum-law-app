def clean_visa_df(dfv):
    import pandas as pd

    if dfv is None or dfv.empty:
        return pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

    # --- Normalisation brute des noms de colonnes ---
    new_cols = []
    for c in dfv.columns:
        c_norm = (
            c.lower()
             .strip()
             .replace("é", "e")
             .replace("è", "e")
             .replace("ê", "e")
             .replace("à", "a")
             .replace("â", "a")
             .replace("ô", "o")
             .replace("î", "i")
             .replace("ï", "i")
             .replace("_", "")
             .replace("-", "")
             .replace(" ", "")
        )
        new_cols.append(c_norm)

    dfv.columns = new_cols

    # Mapping intelligent
    rename_map = {}
    for c in dfv.columns:
        if "categorie" in c:
            rename_map[c] = "Categories"
        elif "sous" in c:
            rename_map[c] = "Sous-categories"
        elif "visa" in c:
            rename_map[c] = "Visa"

    dfv = dfv.rename(columns=rename_map)

    # Colonnes obligatoires
    for col in ["Categories", "Sous-categories", "Visa"]:
        if col not in dfv.columns:
            dfv[col] = ""

    # Nettoyer valeurs
    dfv["Categories"] = dfv["Categories"].astype(str).str.strip()
    dfv["Sous-categories"] = dfv["Sous-categories"].astype(str).str.strip()
    dfv["Visa"] = dfv["Visa"].astype(str).str.strip()

    return dfv
