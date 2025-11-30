import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database
import streamlit as st
st.json(st.secrets)


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

df_filtered = df.copy()

if search:
    df_filtered = df_filtered[
        df_filtered.apply(lambda row: row.astype(str).str.lower().str.contains(search).any(), axis=1)
    ]

# ---------------------------------------------------
# 🎛️ FILTRES INTELLIGENTS dépendants
# ---------------------------------------------------
st.subheader("🎛️ Filtres avancés (intelligents)")

col1, col2, col3 = st.columns(3)

# --------- 1️⃣ FILTRE CATÉGORIE ---------
with col1:
    categories = sorted(df["Catégories"].dropna().unique().tolist())
    cat_select = st.selectbox("Catégorie", ["Toutes"] + categories)

if cat_select != "Toutes":
    df_filtered = df_filtered[df_filtered["Catégories"] == cat_select]

# --------- 2️⃣ FILTRE SOUS-CATÉGORIE ---------
with col2:
    if cat_select != "Toutes":
        souscats = sorted(df_filtered["Sous-catégories"].dropna().unique().tolist())
    else:
        souscats = sorted(df["Sous-catégories"].dropna().unique().tolist())

    souscat_select = st.selectbox("Sous-catégorie", ["Toutes"] + souscats)

if souscat_select != "Toutes":
    df_filtered = df_filtered[df_filtered["Sous-catégories"] == souscat_select]

# --------- 3️⃣ FILTRE VISA ---------
with col3:
    visas = sorted(df_filtered["Visa"].dropna().unique().tolist())
    visa_select = st.selectbox("Visa", ["Tous"] + visas)

if visa_select != "Tous":
    df_filtered = df_filtered[df_filtered["Visa"] == visa_select]

# ---------------------------------------------------
# 📊 STATISTIQUES
# ---------------------------------------------------
st.markdown("---")
st.subheader("📊 Statistiques")

colA, colB, colC = st.columns(3)

colA.metric("Nombre total de dossiers", len(df_filtered))
colB.metric("Dossiers acceptés", df_filtered["Date acceptation"].astype(str).str.len().gt(0).sum())
colC.metric("Dossiers refusés", df_filtered["Date refus"].astype(str).str.len().gt(0).sum())

# ---------------------------------------------------
# 📋 TABLEAU FINAL
# ---------------------------------------------------
st.markdown("---")
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

cols_aff = [c for c in colonnes if c in df_filtered.columns]

st.dataframe(df_filtered[cols_aff], use_container_width=True, height=500)

# ---------------------------------------------------
# ✏️ BOUTON MODIFIER
# ---------------------------------------------------
st.markdown("---")
st.subheader("✏️ Modifier un dossier")

list_dossiers = [""] + df_filtered["Dossier N"].astype(str).unique().tolist()

selected_dossier = st.selectbox("Sélectionner un dossier", list_dossiers)

if selected_dossier:
    st.link_button(
        f"Modifier le dossier {selected_dossier}",
        f"/03_✏️_Modifier_dossier?dossier={selected_dossier}"
    )
