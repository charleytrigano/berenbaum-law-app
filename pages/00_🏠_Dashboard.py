import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database
from utils.visa_filters import clean_visa_df, get_all_lists

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("📊 Tableau de bord – Berenbaum Law App")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
visa_raw = pd.DataFrame(db.get("visa", []))

if not clients:
    st.warning("Aucun dossier trouvé dans Dropbox.")
    st.stop()

df = pd.DataFrame(clients)

# ---------------------------------------------------------
# CLEAN VISA TABLE
# ---------------------------------------------------------
visa_table = clean_visa_df(visa_raw)

# ---------------------------------------------------------
# NORMALISATION CLIENTS
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# STYLE KPI
# ---------------------------------------------------------
st.markdown("""
<style>
div[data-testid="stMetricValue"] {
    font-size: 18px !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# KPI ZONE
# ---------------------------------------------------------
st.subheader("📌 Indicateurs")

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Dossiers", len(df))
k2.metric("Honoraires", f"${df['Montant honoraires (US $)'].sum():,.0f}")
k3.metric("Autres frais", f"${df['Autres frais (US $)'].sum():,.0f}")
k4.metric("Facturé", f"${df['Total facturé'].sum():,.0f}")
k5.metric("Encaissé", f"${df['Montant encaissé'].sum():,.0f}")
k6.metric("Solde", f"${df['Solde'].sum():,.0f}")

st.markdown("---")

# ---------------------------------------------------------
# FILTRES INTELLIGENTS CATEGORIE → SOUS-CATEGORIE → VISA
# ---------------------------------------------------------
st.subheader("🧩 Filtres")

colA, colB, colC, colD, colE, colF = st.columns(6)

# --- 1️⃣ CATEGORIES ---
cat_list, souscat_all, visa_all = get_all_lists(visa_table)
cat = colA.selectbox("Catégorie", ["Toutes"] + cat_list)

# --- 2️⃣ SOUS-CATEGORIES dépendantes ---
if cat != "Toutes":
    souscat_list = ["Toutes"] + sorted(
        visa_table.loc[visa_table["Categories"] == cat, "Sous-categories"].dropna().unique()
    )
else:
    souscat_list = ["Toutes"] + souscat_all

souscat = colB.selectbox("Sous-catégorie", souscat_list)

# --- 3️⃣ VISA dépendant ---
if souscat != "Toutes":
    visa_list = ["Tous"] + sorted(
        visa_table.loc[visa_table["Sous-categories"] == souscat, "Visa"].dropna().unique()
    )
elif cat != "Toutes":
    visa_list = ["Tous"] + sorted(
        visa_table.loc[visa_table["Categories"] == cat, "Visa"].dropna().unique()
    )
else:
    visa_list = ["Tous"] + visa_all

visa_choice = colC.selectbox("Visa", visa_list)

# --- 4️⃣ ANNÉE ---
annees = ["Toutes"] + sorted(df["Année"].dropna().unique().tolist())
annee = colD.selectbox("Année", annees)

# --- 5️⃣ DATE À DATE ---
date_debut = colE.date_input("Date début")
date_fin   = colF.date_input("Date fin")

# ---------------------------------------------------------
# APPLY FILTERS
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

if date_debut:
    filtered = filtered[filtered["Date"] >= pd.to_datetime(date_debut)]

if date_fin:
    filtered = filtered[filtered["Date"] <= pd.to_datetime(date_fin)]

# ---------------------------------------------------------
# KPI MIS À JOUR AVEC LES FILTRES
# ---------------------------------------------------------
st.subheader("📈 KPI après filtres")

fk1, fk2, fk3, fk4, fk5, fk6 = st.columns(6)
fk1.metric("Dossiers", len(filtered))
fk2.metric("Honoraires", f"${filtered['Montant honoraires (US $)'].sum():,.0f}")
fk3.metric("Autres frais", f"${filtered['Autres frais (US $)'].sum():,.0f}")
fk4.metric("Facturé", f"${filtered['Total facturé'].sum():,.0f}")
fk5.metric("Encaissé", f"${filtered['Montant encaissé'].sum():,.0f}")
fk6.metric("Solde", f"${filtered['Solde'].sum():,.0f}")

# ---------------------------------------------------------
# TABLEAU FINAL
# ---------------------------------------------------------
st.subheader("📋 Dossiers filtrés")

st.dataframe(filtered, use_container_width=True, height=600)
