import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(page_title="Liste des dossiers", page_icon="📁", layout="wide")

st.title("📁 Liste des dossiers")
st.write("Visualisez, recherchez et filtrez tous les dossiers clients.")

# ---------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.info("Aucun dossier pour le moment. Ajoutez-en via la page ➕ Nouveau dossier.")
    st.stop()

df = pd.DataFrame(clients)

# ---------------------------------------------------
# 🌐 BARRE DE RECHERCHE
# ---------------------------------------------------
st.subheader("🔎 Rechercher un dossier")

search = st.text_input("Recherche (Nom, Dossier, Catégorie…)", "").lower()

if search:
    df = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(search).any(), axis=1)]

# ---------------------------------------------------
# 🎛️ FILTRES DÉPENDANTS
# ---------------------------------------------------
st.subheader("🎛️ Filtres avancés (liés entre eux)")

col1, col2, col3 = st.columns(3)

# --------- 1️⃣ FILTRE CATÉGORIE ---------
with col1:
    categories = sorted(df["Catégories"].dropna().unique().tolist())
    cat_select = st.selectbox("Catégorie", ["Toutes"] + categories)

if cat_select != "Toutes":
    df = df[df["Catégories"] == cat_select]

# --------- 2️⃣ FILTRE SOUS-CATÉGORIE (dépend de catégorie) ---------
with col2:
    if cat_select != "Toutes":
        souscats = sorted(df["Sous-catégories"].dropna().unique().tolist())
    else:
        souscats = sorted(df["Sous-catégories"].dropna().unique().tolist())

    souscat_select = st.selectbox("Sous-catégorie", ["Toutes"] + souscats)

if souscat_select != "Toutes":
    df = df[df["Sous-catégories"] == souscat_select]

# --------- 3️⃣ FILTRE VISA (dépend des 2 précédents) ---------
with col3:
    if souscat_select != "Toutes":
        visas = sorted(df["Visa"].dropna().unique().tolist())
    elif cat_select != "Toutes":
        visas = sorted(df["Visa"].dropna().unique().tolist())
    else:
        visas = sorted(df["Visa"].dropna().unique().tolist())

    visa_select = st.selectbox("Visa", ["Tous"] + visas)

if visa_select != "Tous":
    df = df[df["Visa"] == visa_select]

st.markdown("---")

# ---------------------------------------------------
# 📊 STATISTIQUES
# ---------------------------------------------------
st.subheader("📊 Aperçu global")

colA, colB, colC = st.columns(3)

colA.metric("Nombre total de dossiers", len(df))
colB.metric("Dossiers acceptés", df["Date acceptation"].astype(str).str.len().gt(0).sum())
colC.metric("Dossiers refusés", df["Date refus"].astype(str).str.len().gt(0).sum())

st.markdown("---")

# ---------------------------------------------------
# 📋 TABLEAU FINAL
# ---------------------------------------------------
st.subheader("📋 Dossiers")

colonnes = [
    "Dossier N",
    "Nom",
    "Catégories",
    "Sous-catégories",
    "Visa",
    "Date envoi",
    "Date acceptation",
    "Date refus",
]

affichage = [c for c in colonnes if c in df.columns]

st.dataframe(df[affichage], use_container_width=True, height=500)

# ---------------------------------------------------
# ✏️ BOUTON MODIFIER
# ---------------------------------------------------
st.markdown("---")
st.subheader("✏️ Modifier un dossier")

# Liste des dossiers disponibles
list_dossiers = [""] + df["Dossier N"].astype(str).unique().tolist()

selected_dossier = st.selectbox("Sélectionner un dossier", list_dossiers)

if selected_dossier:
    st.link_button(
        f"Modifier le dossier {selected_dossier}",
        f"/03_✏️_Modifier_dossier?dossier={selected_dossier}"
    )
