import pandas as pd

# ---------------------------------------------------------
# CLEAN VISA TABLE (VERSION SÉCURISÉE)
# ---------------------------------------------------------
def clean_visa_df(dfv):

    # Si vide → retourner structure propre
    if dfv is None or dfv.empty:
        return pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

    # Nettoyage des noms
    rename_map = {}

    for col in dfv.columns:
        c = col.lower().strip()
        c = c.replace("é", "e").replace("è", "e").replace("ê", "e")

        if "categorie" in c and "sous" not in c:
            rename_map[col] = "Categories"

        elif "sous" in c:
            rename_map[col] = "Sous-categories"

        elif "visa" in c:
            rename_map[col] = "Visa"

    # Renommage possible
    dfv = dfv.rename(columns=rename_map)

    # Sécuriser → si une colonne manque, la créer vide
    for col in ["Categories", "Sous-categories", "Visa"]:
        if col not in dfv.columns:
            dfv[col] = ""

    # Ne garder QUE les 3 colonnes attendues
    dfv = dfv[["Categories", "Sous-categories", "Visa"]]

    # Suppression lignes vides
    dfv = dfv.dropna(how="all")

    # Tout convertir en texte propre
    dfv = dfv.fillna("").astype(str).applymap(str.strip)

    return dfv
