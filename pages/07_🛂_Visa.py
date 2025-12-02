import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.set_page_config(page_title="Visa – Paramétrage", page_icon="🛂", layout="wide")
st.title("🛂 Paramétrage des catégories / sous-catégories / visas")

# ---------------------------------------------------------
# Charger base Dropbox
# ---------------------------------------------------------
db = load_database()
visa_table = db.get("visa", [])

df = pd.DataFrame(visa_table)

# ---------------------------------------------------------
# Nettoyage strict : UNIQUEMENT 3 colonnes
# ---------------------------------------------------------
def clean_visa_df(df):
    if df is None or df.empty:
        return pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

    # normalisation
    rename_map = {}
    for col in df.columns:
        col_clean = col.lower().replace("é","e").replace("è","e").strip()

        if col_clean in ["categories", "categorie"]:
            rename_map[col] = "Categories"
        elif col_clean in ["sous-categories", "sous-categorie"]:
            rename_map[col] = "Sous-categories"
        elif col_clean == "visa":
            rename_map[col] = "Visa"

    df = df.rename(columns=rename_map)

    # supprimer toutes les colonnes inutiles
    for col in list(df.columns):
        if col not in ["Categories", "Sous-categories", "Visa"]:
            df = df.drop(columns=[col])

    # colonnes manquantes
    for c in ["Categories", "Sous-categories", "Visa"]:
        if c not in df.columns:
            df[c] = ""

    return df

df = clean_visa_df(df)


# ---------------------------------------------------------
# Affichage de la grille VISA
# ---------------------------------------------------------
st.subheader("📋 Grille Visa")

if df.empty:
    st.info("Aucun Visa n'est encore enregistré.")
else:
    st.dataframe(df, use_container_width=True, height=400)


st.markdown("---")

# ---------------------------------------------------------
# Ajouter un nouveau Visa (SANS édition / suppression)
# ---------------------------------------------------------
st.subheader("➕ Ajouter un Visa")

col1, col2, col3 = st.columns(3)

with col1:
    cat = st.text_input("Catégorie (ex: Affaires / Tourisme)")

with col2:
    souscat = st.text_input("Sous-catégorie (ex: B-1)")

with col3:
    visa = st.text_input("Visa (ex: B-1 COS)")


if st.button("Ajouter", type="primary"):
    if cat.strip() == "" or souscat.strip() == "" or visa.strip() == "":
        st.error("Merci de remplir les 3 champs.")
    else:
        new_row = {
            "Categories": cat.strip(),
            "Sous-categories": souscat.strip(),
            "Visa": visa.strip()
        }

        df = df.append(new_row, ignore_index=True)

        # Mise à jour base JSON
        db["visa"] = df.to_dict(orient="records")
        save_database(db)

        st.success("✔ Nouveau Visa ajouté")
        st.balloons()
