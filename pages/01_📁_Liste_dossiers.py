import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

st.set_page_config(page_title="Liste des dossiers", page_icon="📁", layout="wide")
st.title("📁 Liste des dossiers")
st.write("Visualisez et filtrez tous les dossiers enregistrés.")

# ---------------------------------------------------
# Charger la base
# ---------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.info("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)

# ---------------------------------------------------
# Normalisation colonnes nécessaires
# ---------------------------------------------------
for col in ["Catégories", "Sous-catégories", "Visa", "Date"]:
    if col not in df.columns:
        df[col] = ""

# ---------------------------------------------------
# Filtres
# ---------------------------------------------------
st.subheader("🎛️ Filtres avancés")

col1, col2, col3 = st.columns(3)

# 🔹 Catégories
categories = ["Toutes"] + sorted(df["Catégories"].dropna().unique().tolist())
filter_cat = col1.selectbox("Catégorie", categories)

# 🔹 Sous-catégories
sous_cat = ["Toutes"] + sorted(df["Sous-catégories"].dropna().unique().tolist())
filter_souscat = col2.selectbox("Sous-catégorie", sous_cat)

# 🔹 Visa
visa_types = ["Tous"] + sorted(df["Visa"].dropna().unique().tolist())
filter_visa = col3.selectbox("Visa", visa_types)

# ---------------------------------------------------
# Application des filtres
# ---------------------------------------------------
filtered = df.copy()

if filter_cat != "Toutes":
    filtered = filtered[filtered["Catégories"] == filter_cat]

if filter_souscat != "Toutes":
    filtered = filtered[filtered["Sous-catégories"] == filter_souscat]

if filter_visa != "Tous":
    filtered = filtered[filtered["Visa"] == filter_visa]

# ---------------------------------------------------
# Résultat
# ---------------------------------------------------
st.markdown("---")
st.subheader("📋 Résultat")

colonnes_affichage = [
    "Dossier N",
    "Nom",
    "Catégories",
    "Sous-catégories",
    "Visa",
    "Date",
]

existing_cols = [c for c in colonnes_affichage if c in filtered.columns]

st.dataframe(filtered[existing_cols], use_container_width=True)
