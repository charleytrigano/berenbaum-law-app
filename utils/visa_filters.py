import pandas as pd

# ---------------------------------------------------------
# Nettoyage du tableau VISA
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
               .strip()
        )

        # Détection des colonnes correctes
        if "categorie" in col_clean and "sous" not in col_clean:
            rename_map[col] = "Categories"

        elif "sous" in col_clean:
            rename_map[col] = "Sous-categories"

        elif "visa" in col_clean:
            rename_map[col] = "Visa"

    dfv = dfv.rename(columns=rename_map)

    # Colonnes obligatoires
    for col in ["Categories", "Sous-categories", "Visa"]:
        if col not in dfv.columns:
            dfv[col] = ""

    # Nettoyage valeurs
    dfv["Categories"] = dfv["Categories"].astype(str).str.strip()
    dfv["Sous-categories"] = dfv["Sous-categories"].astype(str).str.strip()
    dfv["Visa"] = dfv["Visa"].astype(str).str.strip()

    return dfv


# ---------------------------------------------------------
# Retourner listes simples
# ---------------------------------------------------------
def get_all_lists(dfv):
    dfv = clean_visa_df(dfv)

    cat = sorted(dfv["Categories"].unique().tolist())
    sous = sorted(dfv["Sous-categories"].unique().tolist())
    visa = sorted(dfv["Visa"].unique().tolist())

    return cat, sous, visa
