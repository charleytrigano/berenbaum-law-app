import utils.config as cfg
st.warning(f"JSON lu : {cfg.DROPBOX_JSON}")
import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Berenbaum Law App",
    page_icon="📁",
    layout="wide"
)

st.title("📊 Tableau de bord – Berenbaum Law App")
st.write("Bienvenue dans l'application professionnelle de gestion des dossiers.")

# ---------------------------------------------------
# LOAD DB
# ---------------------------------------------------
try:
    db = load_database()
    st.success("Base de données chargée depuis Dropbox ✔")
except Exception as e:
    st.error(f"Erreur Dropbox : {e}")
    db = {"clients": []}
    st.subheader("DEBUG JSON (lu par Dashboard)")
st.json(db)


clients = db.get("clients", [])

if not clients:
    st.info("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)

# ---------------------------------------------------
# NORMALISATION
# ---------------------------------------------------
num_cols = [
    "Montant honoraires (US $)",
    "Autres frais (US $)",
    "Acompte 1",
    "Acompte 2",
    "Acompte 3",
    "Acompte 4"
]

for col in num_cols:
    if col not in df.columns:
        df[col] = 0
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# TOTALS
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
# FILTRES
# ---------------------------------------------------
st.subheader("🎛️ Filtres")

colA, colB, colC, colD, colE = st.columns(5)

# Catégorie
cat_list = ["Toutes"] + sorted(df["Catégories"].dropna().unique().tolist())
cat_filter = colA.selectbox("Catégorie", cat_list)

# Sous-catégorie
scat_list = ["Toutes"] + sorted(df["Sous-catégories"].dropna().unique().tolist())
souscat_filter = colB.selectbox("Sous-catégorie", scat_list)

# Visa
visa_list = ["Tous"] + sorted(df["Visa"].dropna().unique().tolist())
visa_filter = colC.selectbox("Visa", visa_list)

# Année
if "Date" in df.columns:
    df["Année"] = pd.to_datetime(df["Date"], errors="coerce").dt.year
    annee_list = ["Toutes"] + sorted(df["Année"].dropna().unique().tolist())
else:
    annee_list = ["Toutes"]

annee_filter = colD.selectbox("Année", annee_list)

date_debut = colE.date_input("Date début")
date_fin = colE.date_input("Date fin")

# ---------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------
filtered_df = df.copy()

if cat_filter != "Toutes":
    filtered_df = filtered_df[filtered_df["Catégories"] == cat_filter]

if souscat_filter != "Toutes":
    filtered_df = filtered_df[filtered_df["Sous-catégories"] == souscat_filter]

if visa_filter != "Tous":
    filtered_df = filtered_df[filtered_df["Visa"] == visa_filter]

if annee_filter != "Toutes":
    filtered_df = filtered_df[filtered_df["Année"] == annee_filter]

filtered_df["Date"] = pd.to_datetime(filtered_df["Date"], errors="coerce")

if date_debut:
    filtered_df = filtered_df[filtered_df["Date"] >= pd.to_datetime(date_debut)]

if date_fin:
    filtered_df = filtered_df[filtered_df["Date"] <= pd.to_datetime(date_fin)]

# ---------------------------------------------------
# RESULT TABLE
# ---------------------------------------------------
st.subheader("📋 Dossiers filtrés")

columns_to_display = [
    "Dossier N", "Nom", "Catégories", "Sous-catégories", "Visa",
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Total facturé", "Montant encaissé", "Solde", "Date"
]

cols = [c for c in columns_to_display if c in filtered_df.columns]

st.dataframe(filtered_df[cols], use_container_width=True, height=500)
