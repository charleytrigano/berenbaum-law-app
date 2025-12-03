

import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database
from utils.visa_filters import clean_visa_df



# ===========================================================
# Fonctions manquantes
# ===========================================================
def get_souscategories_for_category(dfv, category):
    return (
        dfv[dfv["Categories"] == category]["Sous-categories"]
        .dropna().astype(str).unique().tolist()
    )

def get_visas_for_souscat(dfv, souscat):
    return (
        dfv[dfv["Sous-categories"] == souscat]["Visa"]
        .dropna().astype(str).unique().tolist()
    )

# ===========================================================
# PAGE CONFIG
# ===========================================================
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("📊 Tableau de bord – Berenbaum Law App")

# ===========================================================
# LOAD DATA
# ===========================================================
db = load_database()
clients = db.get("clients", [])
visa_raw = pd.DataFrame(db.get("visa", []))

# Nettoyage Visa
visa_table = clean_visa_df(visa_raw)

# 🔥 FORÇAGE DES COLONNES — ÉLIMINE LE PROBLÈME FINAL
for col in ["Categories", "Sous-categories", "Visa"]:
    if col not in visa_table.columns:
        visa_table[col] = ""

# Stop si pas de clients
if not clients:
    st.warning("Aucun dossier trouvé dans Dropbox.")
    st.stop()

df = pd.DataFrame(clients)

import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Tableau de bord – Berenbaum Law App")

# ---- LOAD DB ----
db = load_database()
clients = db.get("clients", [])
visa_raw = pd.DataFrame(db.get("visa", []))

# 🔍 DEBUG — afficher colonnes VISA réelles
st.write("Colonnes VISA réelles :", visa_raw.columns.tolist())


# ===========================================================
# NORMALISATION
# ===========================================================
df["Date"] = pd.to_datetime(df.get("Date"), errors="coerce")

num_cols = [
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4"
]

for c in num_cols:
    df[c] = pd.to_numeric(df.get(c, 0), errors="coerce").fillna(0)

df["Total facturé"]    = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
df["Montant encaissé"] = df["Acompte 1"] + df["Acompte 2"] + df["Acompte 3"] + df["Acompte 4"]
df["Solde"]            = df["Total facturé"] - df["Montant encaissé"]
df["Année"]            = df["Date"].dt.year

# ===========================================================
# KPI
# ===========================================================
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
# FILTRES INTELLIGENTS
# ===========================================================
st.subheader("🎛️ Filtres")
colA, colB, colC, colD, colE = st.columns(5)

# ---- CATEGORIE ----
cat_list = ["Toutes"] + sorted(visa_table["Categories"].dropna().astype(str).unique().tolist())
cat = colA.selectbox("Categorie", cat_list)

# ---- SOUS-CATEGORIE ----
if cat != "Toutes":
    souscat_list = ["Toutes"] + get_souscategories_for_category(visa_table, cat)
else:
    souscat_list = ["Toutes"] + sorted(visa_table["Sous-categories"].dropna().astype(str).unique().tolist())

souscat = colB.selectbox("Sous-categorie", souscat_list)

# ---- VISA ----
if souscat != "Toutes":
    visa_list = ["Tous"] + get_visas_for_souscat(visa_table, souscat)
elif cat != "Toutes":
    visa_list = ["Tous"] + sorted(visa_table[visa_table["Categories"] == cat]["Visa"].dropna().unique())
else:
    visa_list = ["Tous"] + sorted(visa_table["Visa"].dropna().unique())

visa_choice = colC.selectbox("Visa", visa_list)

# ---- ANNÉE ----
annee_list = ["Toutes"] + sorted(df["Année"].dropna().unique().tolist())
annee = colD.selectbox("Année", annee_list)

# ---- DATES ----
date_debut = colE.date_input("Date début")
date_fin   = colE.date_input("Date fin")

# ===========================================================
# APPLY FILTERS
# ===========================================================
filtered = df.copy()

if cat != "Toutes":
    filtered = filtered[filtered["Categories"] == cat]

if souscat != "Toutes":
    filtered = filtered[filtered["Sous-categories"] == souscat]

if visa_choice != "Tous":
    filtered = filtered[filtered["Visa"] == visa_choice]

if annee != "Toutes":
    filtered = filtered[filtered["Année"] == annee]

if date_debut:
    filtered = filtered[filtered["Date"] >= pd.to_datetime(date_debut)]

if date_fin:
    filtered = filtered[filtered["Date"] <= pd.to_datetime(date_fin)]

# ===========================================================
# TABLEAU
# ===========================================================
st.subheader("📋 Dossiers filtrés")
st.dataframe(filtered, use_container_width=True, height=600)
