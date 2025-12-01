import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

st.set_page_config(page_title="Berenbaum Dashboard", page_icon="📊", layout="wide")

st.title("📊 Tableau de bord – Berenbaum Law App")
st.write("Bienvenue dans l'application professionnelle de gestion des dossiers.")

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
# Normalisation : créer toutes les colonnes manquantes
# ---------------------------------------------------
colonnes_requises = [
    "Dossier N",
    "Nom",
    "Catégories",
    "Sous-catégories",
    "Visa",
    "Montant honoraires (US $)",
    "Autres frais (US $)",
    "Acompte 1",
    "Acompte 2",
    "Acompte 3",
    "Acompte 4",
    "Date"
]

for col in colonnes_requises:
    if col not in df.columns:
        df[col] = ""

# Colonnes numériques
colonnes_num = [
    "Montant honoraires (US $)",
    "Autres frais (US $)",
    "Acompte 1",
    "Acompte 2",
    "Acompte 3",
    "Acompte 4"
]

for col in colonnes_num:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# ---------------------------------------------------
# Calculs financiers
# ---------------------------------------------------
df["Total facturé"] = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
df["Montant encaissé"] = df["Acompte 1"] + df["Acompte 2"] + df["Acompte 3"] + df["Acompte 4"]
df["Solde"] = df["Total facturé"] - df["Montant encaissé"]

# ---------------------------------------------------
# KPI
# ---------------------------------------------------
st.subheader("📌 Indicateurs")

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("Nombre de dossiers", len(df))
col2.metric("Total honoraires", f"${df['Montant honoraires (US $)'].sum():,.2f}")
col3.metric("Total autres frais", f"${df['Autres frais (US $)'].sum():,.2f}")
col4.metric("Total facturé", f"${df['Total facturé'].sum():,.2f}")
col5.metric("Montant encaissé", f"${df['Montant encaissé'].sum():,.2f}")
col6.metric("Solde", f"${df['Solde'].sum():,.2f}")

st.markdown("---")

# ---------------------------------------------------
# Filtres
# ---------------------------------------------------
st.subheader("🎛️ Filtres")

colA, colB, colC, colD, colE = st.columns(5)

cat_list = ["Toutes"] + sorted(df["Catégories"].dropna().unique().tolist())
cat_filter = colA.selectbox("Catégorie", cat_list)

souscat_list = ["Toutes"] + sorted(df["Sous-catégories"].dropna().unique().tolist())
souscat_filter = colB.selectbox("Sous-catégorie", souscat_list)

visa_list = ["Tous"] + sorted(df["Visa"].dropna().unique().tolist())
visa_filter = colC.selectbox("Visa", visa_list)

# Année
df["Année"] = pd.to_datetime(df["Date"], errors="coerce").dt.year
annee_list = ["Toutes"] + sorted(df["Année"].dropna().unique().tolist())
annee_filter = colD.selectbox("Année", annee_filter)

# Dates
date_debut = colE.date_input("Date début", value=None)
date_fin = colE.date_input("Date fin", value=None)

# ---------------------------------------------------
# Application des filtres
# ---------------------------------------------------
filtered = df.copy()

if cat_filter != "Toutes":
    filtered = filtered[filtered["Catégories"] == cat_filter]

if souscat_filter != "Toutes":
    filtered = filtered[filtered["Sous-catégories"] == souscat_filter]

if visa_filter != "Tous":
    filtered = filtered[filtered["Visa"] == visa_filter]

if annee_filter != "Toutes":
    filtered = filtered[filtered["Année"] == annee_filter]

# Filtre date
filtered["Date"] = pd.to_datetime(filtered["Date"], errors="coerce")

if date_debut:
    filtered = filtered[filtered["Date"] >= pd.to_datetime(date_debut)]

if date_fin:
    filtered = filtered[filtered["Date"] <= pd.to_datetime(date_fin)]

# ---------------------------------------------------
# Tableau final : Colonnes affichées garanties
# ---------------------------------------------------
affichage = [
    "Dossier N",
    "Nom",
    "Catégories",
    "Sous-catégories",
    "Visa",
    "Montant honoraires (US $)",
    "Autres frais (US $)",
    "Total facturé",
    "Montant encaissé",
    "Solde",
    "Date"
]

affichage = [col for col in affichage if col in filtered.columns]  # sécurité

st.subheader("📋 Dossiers filtrés")
st.dataframe(filtered[affichage], use_container_width=True, height=500)
