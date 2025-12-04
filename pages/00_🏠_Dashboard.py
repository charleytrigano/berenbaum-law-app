import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database
from utils.visa_filters import clean_visa_df   # ✔️ seule version valide

# ---------------------------------------------------------
# PAGE CONFIG
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
# NORMALISATION VISA (corrigée)
# ---------------------------------------------------------
visa_table = clean_visa_df(visa_raw)  # ✔️ version stable depuis utils/visa_filters.py

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
# KPI (avec taille de texte réduite)
# ---------------------------------------------------------
st.markdown("""
<style>
div[data-testid="stMetricValue"] {
    font-size: 18px !important;
}
</style>
""", unsafe_allow_html=True)

st.subheader("📌 Indicateurs")

k1, k2, k3, k4, k5, k6 = st.columns(6)

with k1:
    st.metric("Dossiers", len(df))

with k2:
    st.metric("Honoraires", f"${df['Montant honoraires (US $)'].sum():,.0f}")

with k3:
    st.metric("Autres frais", f"${df['Autres frais (US $)'].sum():,.0f}")

with k4:
    st.metric("Facturé", f"${df['Total facturé'].sum():,.0f}")

with k5:
    st.metric("Encaissé", f"${df['Montant encaissé'].sum():,.0f}")

with k6:
    st.metric("Solde", f"${df['Solde'].sum():,.0f}")

st.markdown("---")

# ---------------------------------------------------------
# FILTRES
# ---------------------------------------------------------
st.subheader("🧩 Filtres")

colA, colB, colC, colD, colE, colF = st.columns([1,1,1,1,1,1])

# ---------------- CATÉGORIES réelles (plus de mélange avec Sous-cat)
real_categories = sorted(
    set(visa_table["Categories"].dropna())
)

cat_list = ["Toutes"] + real_categories
cat = colA.selectbox("Catégorie", cat_list)

# ---------------- SOUS-CATÉGORIES dépendantes ----------
if cat != "Toutes":
    souscat_list = (
        ["Toutes"] +
        sorted(
            visa_table.loc[
                visa_table["Categories"] == cat, "Sous-categories"
            ].dropna().unique().tolist()
        )
    )
else:
    souscat_list = ["Toutes"] + sorted(
        visa_table["Sous-categories"].dropna().unique().tolist()
    )

souscat = colB.selectbox("Sous-catégorie", souscat_list)

# ---------------- VISA dépendant ------------------------
if souscat != "Toutes":
    visa_list = ["Tous"] + sorted(
        visa_table.loc[
            visa_table["Sous-categories"] == souscat, "Visa"
        ].dropna().unique().tolist()
    )
elif cat != "Toutes":
    visa_list = ["Tous"] + sorted(
        visa_table.loc[
            visa_table["Categories"] == cat, "Visa"
        ].dropna().unique().tolist()
    )
else:
    visa_list = ["Tous"] + sorted(visa_table["Visa"].dropna().unique().tolist())

visa_choice = colC.selectbox("Visa", visa_list)

# ---------------- ANNÉE ------------------------
annees = ["Toutes"] + sorted(df["Année"].dropna().unique().tolist())
annee = colD.selectbox("Année", annees)

# ---------------- DATES ------------------------
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
# TABLEAU FINAL
# ---------------------------------------------------------
st.subheader("📋 Dossiers filtrés")
st.dataframe(filtered, use_container_width=True, height=600)
