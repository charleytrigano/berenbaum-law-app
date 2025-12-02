import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.set_page_config(page_title="Gestion Visa", page_icon="🛂", layout="wide")
st.title("🛂 Grille Visa – Catégorie → Sous-catégorie → Visa")

db = load_database()
visa_data = db.get("visa", [])

df = pd.DataFrame(visa_data)

if df.empty:
    df = pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

# -------------------------------------------------
# Affichage grille Visa
# -------------------------------------------------
st.subheader("📋 Grille actuelle")
st.dataframe(df, use_container_width=True, height=500)

st.markdown("---")

# -------------------------------------------------
# Ajouter un Visa
# -------------------------------------------------
st.subheader("➕ Ajouter un nouveau Visa")

col1, col2, col3 = st.columns(3)

with col1:
    cat = st.text_input("Catégorie").strip()

with col2:
    souscat = st.text_input("Sous-catégorie").strip()

with col3:
    visa = st.text_input("Visa").strip()

if st.button("➕ Ajouter", type="primary"):
    if not cat or not souscat or not visa:
        st.error("Les trois champs sont obligatoires.")
    else:
        df.loc[len(df)] = {
            "Categories": cat,
            "Sous-categories": souscat,
            "Visa": visa
        }
        db["visa"] = df.to_dict(orient="records")
        save_database(db)
        st.success("Visa ajouté ✔")
        st.balloons()
