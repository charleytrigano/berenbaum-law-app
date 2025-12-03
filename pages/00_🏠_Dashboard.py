import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database
from utils.visa_filters import clean_visa_df, get_all_lists, get_souscats, get_visas

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Tableau de bord – Berenbaum Law App")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
visa_raw = pd.DataFrame(db.get("visa", []))

if not clients:
    st.error("Aucun dossier client trouvé dans Dropbox.")
    st.stop()

df = pd.DataFrame(clients)

# ---------------------------------------------------------
# CLEAN VISA TABLE
# ---------------------------------------------------------
visa_table = clean_visa_df(visa_raw)

# Debug éventuel (à désactiver après tests)
# st.warning(f"DEBUG VISA RAW COLUMNS → {list(visa_raw.columns)}")
# st.dataframe(visa_table, use_container_width=True, height=200)

# ---------------------------------------------------------
# NORMALISATION CLIENTS
# ---------------------------------------------------------
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Année"] = df["Date"].dt.year

# Convertir montants
for col in [
    "Montant honoraires (US $)",
    "Autres frais (US $)",
    "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4"
]:
    df[col] = pd.to_numeric(df.get(col, 0), errors="coerce").fillna(0)

df["Total facturé"] = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
df["Montant encaissé"] = df["Acompte 1"] + df["Acompte 2"] + df["Acompte 3"] + df["Acompte 4"]
df["Solde"] = df["Total facturé"] - df["Montant encaissé"]

# ---------------------------------------------------------
# KPI
# ---------------------------------------------------------
st.subheader("📌 Indicateurs")
k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("Dossiers", len(df))
k2.metric("Honoraires", f"${df['Montant honoraires (US $)'].sum():,.2f}")
k3.metric("Autres frais", f"${df['Autres frais (US $)'].sum():,.2f}")
k4.metric("Facturé", f"${df['Total facturé'].sum():,.2f}")
k5.metric("Encaissé", f"${df['Montant encaissé'].sum():,.2f}")
k6.metric("Solde", f"${df['Solde'].sum():,.2f}")

st.markdown("---")

# ---------------------------------------------------------
# FILTRES
# ---------------------------------------------------------
st.subheader("🎛️ Filtres")

colA, colB, colC, colD, colE = st.columns(5)

# ---- Catégories disponibles ----
cat_list, souscat_list_total, visa_list_total = get_all_lists(visa_table)
cat = colA.selectbox("Catégorie", ["Toutes"] + cat_list)

# ---- Sous-catégories dépendantes ----
if cat != "Toutes":
    souscat_list = ["Toutes"] + get_souscats(visa_table, cat)
else:
    souscat_list = ["Toutes"] + souscat_list_total

souscat = colB.selectbox("Sous-catégorie", souscat_list)

# ---- Visa dépendant ----
if souscat != "Toutes":
    visa_list = ["Tous"] + get_visas(visa_table, souscat)
elif cat != "Toutes":
    visa_list = ["Tous"] + sorted(visa_table[visa_table["Categories"] == cat]["Visa"].dropna().unique())
else:
    visa_list = ["Tous"] + visa_list_total

visa_choice = colC.selectbox("Visa", visa_list)

# ---- Année ----
annees = ["Toutes"] + sorted(df["Année"].dropna().unique().tolist())
annee = colD.selectbox("Année", annees)

# ---- Dates ----
date_debut = colE.date_input("Date début")
date_fin = colE.date_input("Date fin")

# ---------------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# TABLEAU FINAL
# ---------------------------------------------------------
st.subheader("📋 Dossiers filtrés")
st.dataframe(filtered, use_container_width=True, height=600)
