import pandas as pd

def clean_visa_df(dfv):
    """Nettoie et homogénéise la table VISA sans jamais provoquer de KeyError."""

    if dfv is None or dfv.empty:
        return pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

    df = dfv.copy()

    # 1️⃣ On convertit tout en string dès le début
    df.columns = df.columns.astype(str)

    # 2️⃣ Détection automatique des colonnes
    col_map = {
        "Categories": None,
        "Sous-categories": None,
        "Visa": None
    }

    for col in df.columns:
        col_clean = col.lower().replace("é", "e").replace("è", "e").replace("ê", "e")

        if "categorie" in col_clean and col_map["Categories"] is None:
            col_map["Categories"] = col
        elif "sous" in col_clean and col_map["Sous-categories"] is None:
            col_map["Sous-categories"] = col
        elif "visa" in col_clean and col_map["Visa"] is None:
            col_map["Visa"] = col

    # 3️⃣ Créer les colonnes manquantes
    for key in col_map:
        if col_map[key] is None:
            df[key] = ""
            col_map[key] = key

    # 4️⃣ Extraction et nettoyage final
    df_clean = pd.DataFrame({
        "Categories": df[col_map["Categories"]].astype(str).str.strip(),
        "Sous-categories": df[col_map["Sous-categories"]].astype(str).str.strip(),
        "Visa": df[col_map["Visa"]].astype(str).str.strip(),
    })

    # 5️⃣ Supprimer lignes vides
    df_clean = df_clean.replace({"nan": "", "None": ""}).fillna("")
    df_clean = df_clean[df_clean["Categories"] != ""]

    return df_clean


def get_all_lists(dfv):
    """Retourne les trois listes uniques triées."""
    df = clean_visa_df(dfv)

    cat = sorted(df["Categories"].dropna().unique().tolist())
    sous = sorted(df["Sous-categories"].dropna().unique().tolist())
    visas = sorted(df["Visa"].dropna().unique().tolist())

    return cat, sous, visas
