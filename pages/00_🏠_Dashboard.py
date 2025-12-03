import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database
from utils.visa_filters import clean_visa_df, get_souscats, get_visas

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Tableau de bord – Berenbaum Law App")

# ---- LOAD DB ----
db = load_database()
clients = db.get("clients", [])
visa_raw = pd.DataFrame(db.get("visa", []))

# ---- DEBUG ----
st.write("===== DEBUG VISA RAW COLS =====", visa_raw.columns.tolist())
st.dataframe(visa_raw.head())

# Nettoyage VISA
visa_table = clean_visa_df(visa_raw)

# ---- STOP SI PAS DE CLIENTS ----
if not clients:
    st.warning("Aucun dossier trouvé dans Dropbox.")
    st.stop()

df = pd.DataFrame(clients)

# ---- NORMALISATION ----
df["Date"] = pd.to_datetime(df.get("Date"), errors="coerce")

num_cols = [
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4"
]

for c in num_cols:
    df[c] = pd.to_numeric(df.get(c, 0), errors="coerce").fillna(0)

df["Total facturé"] = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
df["Montant encaissé"] = df["Acompte 1"] + df["Acompte 2"] + df["Acompte 3"] + df["Acompte 4"]
df["Solde"] = df["Total facturé"] - df["Montant encaissé"]
df["Année"] = df["Date"].dt.year

# ---- KPI ----
st.subheader("📌 Indicateurs")
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Dossiers", len(df))
k2.metric("Honoraires", f"${df['Montant honoraires (US $)'].sum():,.2f}")
k3.metric("Autres frais", f"${df['Autres frais (US $)'].sum():,.2f}")
k4.metric("Facturé", f"${df['Total facturé'].sum():,.2f}")
k5.metric("Encaissé", f"${df['Montant encaissé'].sum():,.2f}")
k6.metric("Solde", f"${df['Solde'].sum():,.2f}")

st.markdown("---")

# ===========================================================
# 🔍 FILTRES INTELLIGENTS VISA
# ===========================================================
st.subheader("🎛️ Filtres")

colA, colB, colC, colD, colE = st.columns(5)

# --- Catégories ---
cat_list = sorted(visa_table["Categories"].dropna().astype(str).unique().tolist())
cat = colA.selectbox("Catégorie", ["Toutes"] + cat_list)

# --- Sous-catégories ---
if cat != "Toutes":
    souscat_list = ["Toutes"] + get_souscats(visa_table, cat)
else:
    souscat_list = ["Toutes"] + sorted(visa_table["Sous-categories"].dropna().astype(str).unique().tolist())

souscat = colB.selectbox("Sous-catégorie", souscat_list)

# --- Visa ---
if souscat != "Toutes":
    visa_list = ["Tous"] + get_visas(visa_table, cat, souscat)
elif cat != "Toutes":
    visa_list = ["Tous"] + sorted(visa_table[visa_table["Categories"] == cat]["Visa"].dropna().unique())
else:
    visa_list = ["Tous"] + sorted(visa_table["Visa"].dropna().unique())

visa_choice = colC.selectbox("Visa", visa_list)

# --- Année ---
annees = sorted(df["Année"].dropna().unique().tolist())
annee = colD.selectbox("Année", ["Toutes"] + annees)

# --- Dates ---
date_debut = colE.date_input("Date début")
date_fin   = colE.date_input("Date fin")

# ===========================================================
# 🔍 APPLY FILTERS
# ===========================================================
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

# ===========================================================
# TABLEAU FINAL
# ===========================================================
st.subheader("📋 Dossiers filtrés")
st.dataframe(filtered, use_container_width=True, height=600)

