import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database
from utils.visa_filters import clean_visa_df, get_souscats, get_visas, get_all_lists

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Tableau de bord – Berenbaum Law App")

# ---------------------------------------------------------
# 🔹 Charger la base Dropbox
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
visa_raw = pd.DataFrame(db.get("visa", []))

# Nettoyage du tableau Visa
visa_table = clean_visa_df(visa_raw)

# ---------------------------------------------------------
# 🔹 Sécurité colonnes Visa
# ---------------------------------------------------------
for col in ["Categories", "Sous-categories", "Visa"]:
    if col not in visa_table.columns:
        visa_table[col] = ""

# ---------------------------------------------------------
# 🔹 STOP si pas de clients
# ---------------------------------------------------------
if not clients:
    st.warning("Aucun dossier trouvé dans la base Dropbox.")
    st.stop()

df = pd.DataFrame(clients)

# ---------------------------------------------------------
# 🔹 Normalisation des données clients
# ---------------------------------------------------------
df["Date"] = pd.to_datetime(df.get("Date"), errors="coerce")

num_cols = [
    "Montant honoraires (US $)",
    "Autres frais (US $)",
    "Acompte 1",
    "Acompte 2",
    "Acompte 3",
    "Acompte 4"
]

for c in num_cols:
    df[c] = pd.to_numeric(df.get(c, 0), errors="coerce").fillna(0)

df["Total facturé"] = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
df["Montant encaissé"] = df["Acompte 1"] + df["Acompte 2"] + df["Acompte 3"] + df["Acompte 4"]
df["Solde"] = df["Total facturé"] - df["Montant encaissé"]
df["Année"] = df["Date"].dt.year

# ---------------------------------------------------------
# 🔹 KPI – Ligne colorée
# ---------------------------------------------------------
st.subheader("📌 Indicateurs")

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("Dossiers", len(df))
col2.metric("Honoraires", f"${df['Montant honoraires (US $)'].sum():,.2f}")
col3.metric("Autres frais", f"${df['Autres frais (US $)'].sum():,.2f}")
col4.metric("Facturé", f"${df['Total facturé'].sum():,.2f}")
col5.metric("Encaissé", f"${df['Montant encaissé'].sum():,.2f}")
col6.metric("Solde", f"${df['Solde'].sum():,.2f}")

st.markdown("---")

# ---------------------------------------------------------
# 🔹 FILTRES INTELLIGENTS
# ---------------------------------------------------------
st.subheader("🎛️ Filtres")

colA, colB, colC, colD, colE = st.columns(5)

# --- Catégories ---
cat_list, souscat_all, visa_all = get_all_lists(visa_table)
cat = colA.selectbox("Catégorie", ["Toutes"] + cat_list)

# --- Sous-catégories ---
if cat != "Toutes":
    souscats = get_souscats(visa_table, cat)
    souscat = colB.selectbox("Sous-catégorie", ["Toutes"] + souscats)
else:
    souscat = colB.selectbox("Sous-catégorie", ["Toutes"] + souscat_all)

# --- Visa ---
if souscat != "Toutes":
    visas = get_visas(visa_table, souscat)
elif cat != "Toutes":
    visas = sorted(visa_table[visa_table["Categories"] == cat]["Visa"].dropna().unique())
else:
    visas = visa_all

visa_choice = colC.selectbox("Visa", ["Tous"] + visas)

# --- Année ---
annees = sorted(df["Année"].dropna().unique().tolist())
annee = colD.selectbox("Année", ["Toutes"] + annees)

# --- Date à date ---
date_debut = colE.date_input("Date début")
date_fin = colE.date_input("Date fin")

# ---------------------------------------------------------
# 🔹 Application des filtres
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
# 🔹 Tableau final
# ---------------------------------------------------------
st.subheader("📋 Dossiers filtrés")

colonnes = [
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

cols_to_show = [c for c in colonnes if c in filtered.columns]

st.dataframe(filtered[cols_to_show], use_container_width=True, height=600)
