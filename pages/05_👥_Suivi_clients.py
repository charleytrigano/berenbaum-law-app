import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

st.title("👥 Suivi des clients")

# ---------------------------------------------------
# Charger la base Dropbox
# ---------------------------------------------------
try:
    db = load_database()
    st.success("Base de données chargée depuis Dropbox ✔")
except Exception as e:
    st.error(f"Erreur Dropbox : {e}")
    st.stop()

clients = db.get("clients", [])

# ---------------------------------------------------
# DataFrame propre
# ---------------------------------------------------
if not clients:
    st.warning("Aucun client enregistré.")
    st.stop()

df = pd.DataFrame(clients)

# Colonnes utilisées
colonnes_interet = [
    "Dossier N",
    "Nom",
    "Catégories",
    "Sous-catégories",
    "Visa",
    "Date envoi",
    "Date acceptation",
    "Date refus",
    "Commentaires"
]

# Ajouter colonnes manquantes
for col in colonnes_interet:
    if col not in df.columns:
        df[col] = ""

# Forcer toutes les colonnes texte → str
for col in colonnes_interet:
    df[col] = df[col].astype(str).fillna("")

# ---------------------------------------------------
# FILTRE UTILISATEUR
# ---------------------------------------------------
st.subheader("🔎 Filtrer les clients")

col1, col2, col3 = st.columns(3)

with col1:
    filtre_nom = st.text_input("Rechercher par nom")

with col2:
    filtre_visa = st.text_input("Filtrer par Visa")

with col3:
    filtre_categorie = st.text_input("Filtrer par catégorie")

df_filtree = df.copy()

if filtre_nom.strip():
    df_filtree = df_filtree[df_filtree["Nom"].str.contains(filtre_nom, case=False, na=False)]

if filtre_visa.strip():
    df_filtree = df_filtree[df_filtree["Visa"].str.contains(filtre_visa, case=False, na=False)]

if filtre_categorie.strip():
    df_filtree = df_filtree[df_filtree["Catégories"].str.contains(filtre_categorie, case=False, na=False)]

# ---------------------------------------------------
# AFFICHAGE TABLEAU
# ---------------------------------------------------
st.subheader("📋 Liste des clients filtrés")

st.dataframe(
    df_filtree[colonnes_interet],
    use_container_width=True,
    height=450
)

# ---------------------------------------------------
# STATISTIQUES RAPIDES
# ---------------------------------------------------
st.subheader("📈 Statistiques")

colA, colB, colC = st.columns(3)

with colA:
    st.metric("Nombre total de clients", len(df))

# Dossier envoyé = champ non vide
with colB:
    st.metric("Dossiers envoyés", (df["Date envoi"].str.len() > 0).sum())

with colC:
    st.metric("Dossiers acceptés", (df["Date acceptation"].str.len() > 0).sum())
