import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database
from utils.visa_filters import clean_visa_df, get_souscategories_for_category, get_visas_for_souscat

# --------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------
st.set_page_config(page_title="Berenbaum Dashboard", page_icon="📊", layout="wide")

st.title("📊 Tableau de bord – Berenbaum Law App")
st.write("Bienvenue dans l'application professionnelle de gestion des dossiers.")

# --------------------------------------------------------
# LOAD DATABASE
# --------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
visa_table = clean_visa_df(pd.DataFrame(db.get("visa", [])))

# --------------------------------------------------------
# STOP SI VIDE
# --------------------------------------------------------
if not clients:
    st.warning("Aucun dossier trouvé dans le JSON Dropbox.")
    st.stop()

df = pd.DataFrame(clients)

# --------------------------------------------------------
# NORMALISATION
# --------------------------------------------------------
df["Montant honoraires (US $)"] = pd.to_numeric(df.get("Montant honoraires (US $)", 0), errors="coerce").fillna(0)
df["Autres frais (US $)"] = pd.to_numeric(df.get("Autres frais (US $)", 0), errors="coerce").fillna(0)

df["Acompte 1"] = pd.to_numeric(df.get("Acompte 1", 0), errors="coerce").fillna(0)
df["Acompte 2"] = pd.to_numeric(df.get("Acompte 2", 0), errors="coerce").fillna(0)
df["Acompte 3"] = pd.to_numeric(df.get("Acompte 3", 0), errors="coerce").fillna(0)
df["Acompte 4"] = pd.to_numeric(df.get("Acompte 4", 0), errors="coerce").fillna(0)

df["Total facturé"] = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
df["Montant encaissé"] = df["Acompte 1"] + df["Acompte 2"] + df["Acompte 3"] + df["Acompte 4"]
df["Solde"] = df["Total facturé"] - df["Montant encaissé"]

df["Date"] = pd.to_datetime(df.get("Date", None), errors="coerce")
df["Année"] = df["Date"].dt.year

# --------------------------------------------------------
# KPI – dark mode amélioré
# --------------------------------------------------------
st.subheader("📌 Indicateurs")

k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("Total dossiers", len(df))
k2.metric("Honoraires", f"${df['Montant honoraires (US $)'].sum():,.2f}")
k3.metric("Autres frais", f"${df['Autres frais (US $)'].sum():,.2f}")
k4.metric("Total facturé", f"${df['Total facturé'].sum():,.2f}")
k5.metric("Encaissé", f"${df['Montant encaissé'].sum():,.2f}")
k6.metric("Solde restant", f"${df['Solde'].sum():,.2f}")

st.markdown("---")

# --------------------------------------------------------
# 🎛️ FILTRES
# --------------------------------------------------------
st.subheader("🎛️ Filtres")

colA, colB, colC, colD, colE = st.columns(5)

# Catégorie
cat_list = ["Toutes"] + sorted(visa_table["Categories"].unique().tolist())
cat = colA.selectbox("Catégorie", cat_list)

# Sous-catégorie dépendante
if cat != "Toutes":
    souscat_list = ["Toutes"] + get_souscategories_for_category(visa_table, cat)
else:
    souscat_list = ["Toutes"] + sorted(visa_table["Sous-categories"].unique().tolist())

souscat = colB.selectbox("Sous-catégorie", souscat_list)

# Visa dépendant
if souscat != "Toutes":
    visa_list = ["Tous"] + get_visas_for_souscat(visa_table, souscat)
elif cat != "Toutes":
    visa_list = ["Tous"] + sorted(visa_table[visa_table["Categories"] == cat]["Visa"].unique().tolist())
else:
    visa_list = ["Tous"] + sorted(visa_table["Visa"].unique().tolist())

visa_choice = colC.selectbox("Visa", visa_list)

# Année
annee_list = ["Toutes"] + sorted(df["Année"].dropna().unique().tolist())
annee = colD.selectbox("Année", annee_list)

# Date
date_debut = colE.date_input("Date début")
date_fin = colE.date_input("Date fin")

# --------------------------------------------------------
# Application des filtres
# --------------------------------------------------------
filtered = df.copy()

if cat != "Toutes":
    filtered = filtered[filtered["Catégories"] == cat]

if souscat != "Toutes":
    filtered = filtered[filtered["Sous-catégories"] == souscat]

if visa_choice != "Tous":
    filtered = filtered[filtered["Visa"] == visa_choice]

if annee != "Toutes":
    filtered = filtered[filtered["Année"] == annee]

if date_debut:
    filtered = filtered[filtered["Date"] >= pd.to_datetime(date_debut)]

if date_fin:
    filtered = filtered[filtered["Date"] <= pd.to_datetime(date_fin)]

# --------------------------------------------------------
# TABLEAU FINAL
# --------------------------------------------------------
st.subheader("📋 Dossiers filtrés")

colonnes = [
    "Dossier N", "Nom", "Catégories", "Sous-catégories", "Visa",
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Total facturé", "Montant encaissé", "Solde", "Date"
]

colonnes = [c for c in colonnes if c in filtered.columns]

st.dataframe(filtered[colonnes], use_container_width=True, height=600)
