import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database
from utils.visa_filters import clean_visa_df

st.set_page_config(page_title="Liste des dossiers", page_icon="📁", layout="wide")

st.title("📁 Liste des dossiers – Analyse & Filtrage avancé")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
visa_raw = pd.DataFrame(db.get("visa", []))

if not clients:
    st.warning("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)
visa_table = clean_visa_df(visa_raw)

# ---------------------------------------------------------
# NORMALISATION DES DONNÉES CLIENTS
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
df["Montant encaissé"] = (
    df["Acompte 1"] + df["Acompte 2"] + df["Acompte 3"] + df["Acompte 4"]
)
df["Solde"] = df["Total facturé"] - df["Montant encaissé"]
df["Année"] = df["Date"].dt.year

# ---------------------------------------------------------
# CALCUL STATUT DOSSIER
# ---------------------------------------------------------
def compute_status(row):
    if str(row.get("RFE", "")).strip() not in ["", "nan", "None"]:
        return "RFE"
    if str(row.get("Date annulation", "")).strip() not in ["", "nan", "None"]:
        return "Annulé"
    if str(row.get("Date refus", "")).strip() not in ["", "nan", "None"]:
        return "Refusé"
    if str(row.get("Date acceptation", "")).strip() not in ["", "nan", "None"]:
        return "Accepté"
    if str(row.get("Date envoi", "")).strip() not in ["", "nan", "None"]:
        return "Envoyé"
    return "En cours"

df["Statut"] = df.apply(compute_status, axis=1)

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
# KPI (Dynamiques selon filtres)
# ---------------------------------------------------------
def show_kpis(df_local):
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Dossiers", len(df_local))
    c2.metric("Honoraires", f"${df_local['Montant honoraires (US $)'].sum():,.0f}")
    c3.metric("Autres frais", f"${df_local['Autres frais (US $)'].sum():,.0f}")
    c4.metric("Facturé", f"${df_local['Total facturé'].sum():,.0f}")
    c5.metric("Encaissé", f"${df_local['Montant encaissé'].sum():,.0f}")
    c6.metric("Solde", f"${df_local['Solde'].sum():,.0f}")

st.subheader("📌 Indicateurs (Filtres actifs)")
show_kpis(df)

st.markdown("---")

# ---------------------------------------------------------
# 🧩 FILTRES
# ---------------------------------------------------------
st.subheader("🎛️ Filtres")

colA, colB, colC, colD, colE = st.columns(5)

# ---- FILTRE CATÉGORIE ----
cat_list = ["Toutes"] + sorted(visa_table["Categories"].unique())
cat = colA.selectbox("Catégorie", cat_list)

# ---- FILTRE SOUS-CAT ----
if cat != "Toutes":
    souscat_list = ["Toutes"] + sorted(
        visa_table.loc[visa_table["Categories"] == cat]["Sous-categories"].unique()
    )
else:
    souscat_list = ["Toutes"] + sorted(visa_table["Sous-categories"].unique())

souscat = colB.selectbox("Sous-catégorie", souscat_list)

# ---- FILTRE VISA ----
if souscat != "Toutes":
    visa_list = ["Tous"] + sorted(
        visa_table.loc[visa_table["Sous-categories"] == souscat]["Visa"].unique()
    )
elif cat != "Toutes":
    visa_list = ["Tous"] + sorted(
        visa_table.loc[visa_table["Categories"] == cat]["Visa"].unique()
    )
else:
    visa_list = ["Tous"] + sorted(visa_table["Visa"].unique())

visa_choice = colC.selectbox("Visa", visa_list)

# ---- FILTRE ANNÉE ----
annees = ["Toutes"] + sorted(df["Année"].dropna().unique().tolist())
annee = colD.selectbox("Année", annees)

# ---- FILTRE STATUT ----
status_filter = colE.selectbox(
    "Statut dossier",
    ["Tous", "En cours", "Envoyé", "Accepté", "Refusé", "Annulé", "RFE"]
)

# ---------------------------------------------------------
# APPLICATION DES FILTRES
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

if status_filter != "Tous":
    filtered = filtered[filtered["Statut"] == status_filter]

# ---------------------------------------------------------
# KPI MIS À JOUR
# ---------------------------------------------------------
st.subheader("📌 Indicateurs avec filtres")
show_kpis(filtered)

st.markdown("---")

# ---------------------------------------------------------
# TABLEAU FINAL
# ---------------------------------------------------------
st.subheader("📋 Dossiers filtrés")

colonnes = [
    "Dossier N", "Nom", "Categories", "Sous-categories", "Visa",
    "Date", "Statut",
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Total facturé", "Montant encaissé", "Solde"
]

affichage = [c for c in colonnes if c in filtered.columns]

st.dataframe(filtered[affichage], use_container_width=True, height=650)
