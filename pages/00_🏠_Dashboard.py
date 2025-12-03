import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database
from utils.visa_filters import clean_visa_df, get_souscats, get_visas

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Tableau de bord – Berenbaum Law App")

# ---------------------------------------------------------
# 🔹 Load DB
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
visa_raw = pd.DataFrame(db.get("visa", []))

if not clients:
    st.warning("Aucun dossier trouvé dans la base Dropbox.")
    st.stop()

df = pd.DataFrame(clients)

# ---------------------------------------------------------
# 🔹 Nettoyage VISA
# ---------------------------------------------------------
visa_table = clean_visa_df(visa_raw)

# ---------------------------------------------------------
# 🔹 Formatage du DataFrame client
# ---------------------------------------------------------
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

num_cols = [
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4"
]

for col in num_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

df["Total facturé"] = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
df["Montant encaissé"] = df["Acompte 1"] + df["Acompte 2"] + df["Acompte 3"] + df["Acompte 4"]
df["Solde"] = df["Total facturé"] - df["Montant encaissé"]
df["Année"] = df["Date"].dt.year

# ---------------------------------------------------------
# 🎯 KPI (textee réduit + couleurs dark mode)
# ---------------------------------------------------------
st.subheader("📌 Indicateurs")

k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("Dossiers", len(df))
k2.metric("Honoraires", f"${df['Montant honoraires (US $)'].sum():,.0f}")
k3.metric("Autres frais", f"${df['Autres frais (US $)'].sum():,.0f}")
k4.metric("Facturé", f"${df['Total facturé'].sum():,.0f}")
k5.metric("Encaissé", f"${df['Montant encaissé'].sum():,.0f}")
k6.metric("Solde", f"${df['Solde'].sum():,.0f}")

# Réduit la taille des nombres des KPI
st.markdown("""
<style>
[data-testid="stMetricValue"] {
    font-size: 18px !important;
    color: #4FC3F7;           /* Bleu clair pour dark mode */
}
[data-testid="stMetricLabel"] {
    font-size: 11px !important;
    color: #BBBBBB;
}
</style>
""", unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------
# 🎛️ FILTRES SUR UNE SEULE LIGNE
# ---------------------------------------------------------
st.subheader("🎛️ Filtres")

colA, colB, colC, colD, colE, colF = st.columns(6)

# --- Catégories ---
cat_list = ["Toutes"] + sorted(visa_table["Categories"].dropna().unique().tolist())
cat = colA.selectbox("Catégorie", cat_list)

# --- Sous-catégories ---
if cat != "Toutes":
    souscat_list = ["Toutes"] + get_souscats(visa_table, cat)
else:
    souscat_list = ["Toutes"] + sorted(visa_table["Sous-categories"].dropna().unique().tolist())

souscat = colB.selectbox("Sous-catégorie", souscat_list)

# --- Visa ---
if souscat != "Toutes":
    visa_list = ["Tous"] + get_visas(visa_table, souscat)
elif cat != "Toutes":
    visa_list = ["Tous"] + sorted(visa_table[visa_table["Categories"] == cat]["Visa"].dropna().unique())
else:
    visa_list = ["Tous"] + sorted(visa_table["Visa"].dropna().unique())

visa_choice = colC.selectbox("Visa", visa_list)

# --- Année ---
annee_list = ["Toutes"] + sorted(df["Année"].dropna().unique().tolist())
annee = colD.selectbox("Année", annee_list)

# --- Dates (sur une seule ligne) ---
date_debut = colE.date_input("Date début", value=df["Date"].min())
date_fin   = colF.date_input("Date fin", value=df["Date"].max())

# ---------------------------------------------------------
# 🔎 Application des filtres
# ---------------------------------------------------------
filtered = df.copy()

if cat != "Toutes":
    filtered = filtered[filtered["Categories"] == cat]

if souscat != "Toutes":
    filtered = filtered[filtered["Sous-categories"] == souscat]

if visa_choice != "Tous":
    filtered = filtered[filtered["Visa"] == visa_choice]

if annee != "Toutes":
    filtered = filtered[filtered["Année"] == annee]

filtered = filtered[
    (filtered["Date"] >= pd.to_datetime(date_debut)) &
    (filtered["Date"] <= pd.to_datetime(date_fin))
]

# ---------------------------------------------------------
# 📋 TABLEAU FINAL
# ---------------------------------------------------------
st.subheader("📋 Dossiers filtrés")

colonnes = [
    "Dossier N", "Nom", "Date", "Categories", "Sous-categories", "Visa",
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Total facturé", "Montant encaissé", "Solde"
]

colonnes = [c for c in colonnes if c in filtered.columns]

st.dataframe(filtered[colonnes], use_container_width=True, height=600)
