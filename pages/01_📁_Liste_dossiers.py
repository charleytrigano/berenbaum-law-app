import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database


# ---------------------------------------------------
# PAGE SETUP
# ---------------------------------------------------
st.set_page_config(page_title="Liste des dossiers", page_icon="📁", layout="wide")

st.title("📁 Liste des dossiers")
st.write("Visualisez, recherchez et filtrez tous les dossiers clients.")

# ---------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------
db = load_database()

clients = db.get("clients", [])

# ---------------------------------------------------
# SI PAS DE DOSSIER
# ---------------------------------------------------
if not clients:
    st.info("Aucun dossier pour le moment. Ajoutez-en via la page ➕ Nouveau dossier.")
    st.stop()

df = pd.DataFrame(clients)

# ---------------------------------------------------
# BARRE DE RECHERCHE
# ---------------------------------------------------
st.subheader("🔎 Rechercher un dossier")

search = st.text_input("Recherche (nom, dossier, catégorie...)", "").lower()

if search:
    df = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(search).any(), axis=1)]

# ---------------------------------------------------
# FILTRES AVANCÉS
# ---------------------------------------------------
st.subheader("🎛️ Filtres avancés")

col1, col2, col3, col4 = st.columns(4)

with col1:
    categories = ["Toutes"] + sorted(df["Catégories"].dropna().unique().tolist())
    filter_cat = st.selectbox("Catégorie", categories)

with col2:
    sous_cat_list = ["Toutes"] + sorted(df["Sous-catégories"].dropna().unique().tolist())
    filter_souscat = st.selectbox("Sous-catégorie", sous_cat_list)

with col3:
    visas = ["Tous"] + sorted(df["Visa"].dropna().unique().tolist())
    filter_visa = st.selectbox("Type de Visa", visas)

with col4:
    filter_status = st.selectbox(
        "Statut du dossier",
        ["Tous", "Envoyé", "Accepté", "Refusé", "Annulé"]
    )

# Application des filtres
if filter_cat != "Toutes":
    df = df[df["Catégories"] == filter_cat]

if filter_souscat != "Toutes":
    df = df[df["Sous-catégories"] == filter_souscat]

if filter_visa != "Tous":
    df = df[df["Visa"] == filter_visa]

if filter_status != "Tous":
    target_col = {
        "Envoyé": "Date envoi",
        "Accepté": "Date acceptation",
        "Refusé": "Date refus",
        "Annulé": "Date annulation"
    }.get(filter_status)

    df = df[df[target_col].notna() & (df[target_col] != "")]

st.markdown("---")

# ---------------------------------------------------
# BOUTONS RAPIDES
# ---------------------------------------------------
colA, colB = st.columns([1, 1])

with colA:
    st.link_button("➕ Créer un nouveau dossier", "/02_➕_Nouveau_dossier")

with colB:
    st.write("")

# ---------------------------------------------------
# STATISTIQUES
# ---------------------------------------------------
st.subheader("📊 Aperçu global")

col1, col2, col3 = st.columns(3)
col1.metric("Nombre total de dossiers", len(df))

nb_acceptes = df[df["Date acceptation"].notna() & (df["Date acceptation"] != "")]
nb_refuses = df[df["Date refus"].notna() & (df["Date refus"] != "")]
nb_annules = df[df["Date annulation"].notna() & (df["Date annulation"] != "")]

col2.metric("Dossiers acceptés", len(nb_acceptes))
col3.metric("Dossiers refusés", len(nb_refuses))

# ---------------------------------------------------
# TABLEAU FINAL
# ---------------------------------------------------
st.subheader("📋 Dossiers")

# Colonnes pertinentes
colonnes = [
    "Dossier N",
    "Nom",
    "Catégories",
    "Sous-catégories",
    "Visa",
    "Date envoi",
    "Date acceptation",
    "Date refus"
]

display_cols = [c for c in colonnes if c in df.columns]

st.dataframe(df[display_cols], use_container_width=True, height=500)

# ---------------------------------------------------
# MODIFIER UN DOSSIER
# ---------------------------------------------------
st.markdown("---")
st.subheader("✏️ Modifier un dossier")

selected_dossier = st.selectbox(
    "Sélectionner un dossier",
    [""] + df["Dossier N"].unique().tolist()
)

if selected_dossier:
    st.link_button(
        f"Modifier le dossier {selected_dossier}",
        f"/03_✏️_Modifier_dossier?dossier={selected_dossier}"
    )
