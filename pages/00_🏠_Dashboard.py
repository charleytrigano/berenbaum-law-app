import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database
from utils.visa_filters import clean_visa_df, get_all_lists, get_souscats, get_visas

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Tableau de bord – Berenbaum Law App")

db = load_database()
clients = db.get("clients", [])
visa_raw = pd.DataFrame(db.get("visa", []))

# Nettoyage Visa
visa_table = clean_visa_df(visa_raw)

# STOP si pas de dossiers
if not clients:
    st.warning("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)

# ---------------------- Normalisation ----------------------
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

# ---------------------- KPI ----------------------
st.subheader("📌 Indicateurs")

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Dossiers", len(df))
c2.metric("Honoraires", f"${df['Montant honoraires (US $)'].sum():,.2f}")
c3.metric("Autres frais", f"${df['Autres frais (US $)'].sum():,.2f}")
c4.metric("Facturé", f"${df['Total facturé'].sum():,.2f}")
c5.metric("Encaissé", f"${df['Montant encaissé'].sum():,.2f}")
c6.metric("Solde", f"${df['Solde'].sum():,.2f}")

st.markdown("---")

# ---------------------- FILTRES ----------------------
st.subheader("🎛️ Filtres")

colA, colB, colC, colD, colE = st.columns(5)

cat_list, sous_all, visa_all = get_all_lists(visa_table)

cat = colA.selectbox("Catégorie", ["Toutes"] + cat_list)

# Sous-catégories dépendantes
if cat != "Toutes":
    sous_list = ["Toutes"] + get_souscats(visa_table, cat)
else:
    sous_list = ["Toutes"] + sous_all

souscat = colB.selectbox("Sous-catégorie", sous_list)

# Visa dépendant
if souscat != "Toutes":
    visas = ["Tous"] + get_visas(visa_table, souscat)
elif cat != "Toutes":
    visas = ["Tous"] + sorted(visa_table[visa_table["Categories"] == cat]["Visa"].tolist())
else:
    visas = ["Tous"] + visa_all

visa_choice = colC.selectbox("Visa", visas)

annee = colD.selectbox("Année", ["Toutes"] + sorted(df["Année"].dropna().unique().tolist()))
date_debut = colE.date_input("Date début")
date_fin = colE.date_input("Date fin")

# ---------------------- APPLICATION FILTRES ----------------------
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

# ---------------------- TABLEAU FINAL ----------------------
st.subheader("📋 Dossiers filtrés")
st.dataframe(filtered, use_container_width=True, height=600)
