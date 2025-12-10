import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

from utils.sidebar import render_sidebar
render_sidebar()

st.set_page_config(page_title="Visa – Paramétrage", page_icon="🛂", layout="wide")
st.title("🛂 Paramétrage des categories, sous-categories et visas")

# ---------------------------------------------------------
# Charger base Dropbox
# ---------------------------------------------------------
db = load_database()
visa_table = db.get("visa", [])

df = pd.DataFrame(visa_table)

# ---------------------------------------------------------
# Nettoyage dur : garder seulement 3 colonnes & enlever doublons
# ---------------------------------------------------------
def clean_visa_df(df):
    if df is None or df.empty:
        return pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

   

    # 1️⃣ Renommage intelligent
    rename_map = {}
    for col in df.columns:
        col_clean = col.lower().replace("é", "e").replace("è", "e").strip()

        if col_clean in ["categories", "categorie"]:
            rename_map[col] = "Categories"
        elif col_clean in ["sous-categories", "sous-categorie"]:
            rename_map[col] = "Sous-categories"
        elif col_clean == "visa":
            rename_map[col] = "Visa"

    df = df.rename(columns=rename_map)

    # 2️⃣ Suppression des colonnes non désirées
    df = df[[c for c in df.columns if c in ["Categories", "Sous-categories", "Visa"]]]

    # 3️⃣ Forcer unicité des colonnes
    df = df.loc[:, ~df.columns.duplicated()]

    # 4️⃣ Colonnes manquantes
    for c in ["Categories", "Sous-categories", "Visa"]:
        if c not in df.columns:
            df[c] = ""

    # 5️⃣ Enlever lignes vides
    df = df.dropna(how="all")

    return df

df = clean_visa_df(df)
import pandas as pd

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

        if "categorie" in col_clean and "sous" not in col_clean:
            rename_map[col] = "Categories"

        elif "sous" in col_clean:
            rename_map[col] = "Sous-categories"

        elif col_clean == "visa":
            rename_map[col] = "Visa"

    dfv = dfv.rename(columns=rename_map)

    # Colonnes obligatoires
    for col in ["Categories", "Sous-categories", "Visa"]:
        if col not in dfv.columns:
            dfv[col] = ""

    # Supprimer anciennes colonnes non normalisées
    for bad in ["Catégories", "Sous-catégories", "Sous-categorie"]:
        if bad in dfv.columns:
            dfv = dfv.drop(columns=[bad])

    return dfv

st.write("Colonnes Visa détectées :", df.columns.tolist())



# ---------------------------------------------------------
# Affichage
# ---------------------------------------------------------
st.subheader("📋 Grille Visa")

if df.empty:
    st.info("Aucun Visa n'est enregistré.")
else:
    st.dataframe(df, use_container_width=True, height=400)

st.markdown("---")

# ---------------------------------------------------------
# Ajouter un Visa
# ---------------------------------------------------------
st.subheader("➕ Ajouter un Visa")

col1, col2, col3 = st.columns(3)

cat = col1.text_input("Categorie")
souscat = col2.text_input("Sous-categorie")
visa = col3.text_input("Visa")

if st.button("Ajouter", type="primary"):
    if not cat or not souscat or not visa:
        st.error("Merci de compléter les 3 champs.")
    else:
        new_row = {
            "Categories": cat.strip(),
            "Sous-categories": souscat.strip(),
            "Visa": visa.strip()
        }

        df = df.append(new_row, ignore_index=True)

        # Sauvegarde JSON
        db["visa"] = df.to_dict(orient="records")
        save_database(db)

        st.success("✔ Nouveau Visa ajouté")
        st.balloons()
