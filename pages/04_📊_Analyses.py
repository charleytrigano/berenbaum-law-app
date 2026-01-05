import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database
from components.kpi_cards import kpi_card
from components.analysis_charts import (
    monthly_hist,
    multi_year_line,
    category_donut,
    heatmap_month,
    category_bars,
)
from utils.status_utils import normalize_bool

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(page_title="📊 Analyses", page_icon="📊", layout="wide")
render_sidebar()
st.title("📊 Analyses statistiques – Tableau de bord")

# =====================================================
# LOAD DATABASE
# =====================================================
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.info("Aucune donnée disponible.")
    st.stop()

df = pd.DataFrame(clients).copy()

# =====================================================
# NORMALISATION
# =====================================================
df["Dossier N"] = df["Dossier N"].astype(str)

for col in [
    "Dossier envoye",
    "Dossier accepte",
    "Dossier refuse",
    "Dossier Annule",
    "RFE",
]:
    if col not in df.columns:
        df[col] = False
    df[col] = df[col].apply(normalize_bool)

df["Date"] = pd.to_datetime(df.get("Date"), errors="coerce")
df["Année"] = df["Date"].dt.year

# =====================================================
# CALCULS FINANCIERS
# =====================================================
def to_float(v):
    try:
        return float(v or 0)
    except:
        return 0.0


df["Honoraires"] = df["Montant honoraires (US $)"].apply(to_float)
df["Frais"] = df["Autres frais (US $)"].apply(to_float)
df["Total facturé"] = df["Honoraires"] + df["Frais"]

df["Total encaissé"] = 0.0
for i in range(1, 5):
    col = f"Acompte {i}"
    if col in df.columns:
        df["Total encaissé"] += df[col].apply(to_float)

df["Solde"] = df["Total facturé"] - df["Total encaissé"]

# =====================================================
# 🟡 NOUVELLE LOGIQUE ESCROW (VALIDÉE)
# =====================================================
def calc_escrow(row):
    if row["Dossier accepte"] or row["Dossier refuse"] or row["Dossier Annule"]:
        return 0.0

    total = 0.0
    for i in range(1, 5):
        total += to_float(row.get(f"Acompte {i}", 0))
    return total


df["Escrow Montant"] = df.apply(calc_escrow, axis=1)

# =====================================================
# FILTRES AVANCÉS
# =====================================================
st.subheader("🎛️ Filtres")

c1, c2, c3, c4, c5 = st.columns(5)

# Années
years = sorted(df["Année"].dropna().unique().tolist())
year_sel = c1.multiselect("Année", years, default=years)

# Catégories
cats = ["Tous"] + sorted(df["Categories"].dropna().unique().tolist())
cat = c2.selectbox("Catégorie", cats)

# Sous-catégories
if cat != "Tous":
    souscats = ["Tous"] + sorted(df[df["Categories"] == cat]["Sous-categories"].dropna().unique())
else:
    souscats = ["Tous"] + sorted(df["Sous-categories"].dropna().unique())

sous = c3.selectbox("Sous-catégorie", souscats)

# Visa
if sous != "Tous":
    visas = ["Tous"] + sorted(df[df["Sous-categories"] == sous]["Visa"].dropna().unique())
else:
    visas = ["Tous"] + sorted(df["Visa"].dropna().unique())

visa = c4.selectbox("Visa", visas)

# Statut
statut = c5.selectbox(
    "Statut",
    ["Tous", "Envoyé", "Accepté", "Refusé", "Annulé", "RFE"]
)

# =====================================================
# APPLICATION FILTRES
# =====================================================
df_f = df.copy()

df_f = df_f[df_f["Année"].isin(year_sel)]

if cat != "Tous":
    df_f = df_f[df_f["Categories"] == cat]

if sous != "Tous":
    df_f = df_f[df_f["Sous-categories"] == sous]

if visa != "Tous":
    df_f = df_f[df_f["Visa"] == visa]

if statut != "Tous":
    mapping = {
        "Envoyé": "Dossier envoye",
        "Accepté": "Dossier accepte",
        "Refusé": "Dossier refuse",
        "Annulé": "Dossier Annule",
        "RFE": "RFE",
    }
    df_f = df_f[df_f[mapping[statut]]]

# =====================================================
# KPI
# =====================================================
st.subheader("📈 Indicateurs clés")

k1, k2, k3, k4, k5, k6, k7 = st.columns(7)

k1.metric("Dossiers", len(df_f))
k2.metric("Honoraires", f"${df_f['Honoraires'].sum():,.2f}")
k3.metric("Frais", f"${df_f['Frais'].sum():,.2f}")
k4.metric("Total facturé", f"${df_f['Total facturé'].sum():,.2f}")
k5.metric("Total encaissé", f"${df_f['Total encaissé'].sum():,.2f}")
k6.metric("Solde dû", f"${df_f['Solde'].sum():,.2f}")
k7.metric("Escrow", f"${df_f['Escrow Montant'].sum():,.2f}")

# =====================================================
# GRAPHIQUES
# =====================================================
st.subheader("📊 Graphiques interactifs")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅 Histogramme mensuel",
    "📈 Courbes multi-années",
    "🎯 Répartition catégories",
    "🔥 Heatmap activité",
    "💰 Revenus par catégorie",
])

with tab1:
    st.plotly_chart(monthly_hist(df_f), use_container_width=True)

with tab2:
    st.plotly_chart(multi_year_line(df_f), use_container_width=True)

with tab3:
    st.plotly_chart(category_donut(df_f), use_container_width=True)

with tab4:
    st.plotly_chart(heatmap_month(df_f), use_container_width=True)

with tab5:
    st.plotly_chart(category_bars(df_f), use_container_width=True)

# =====================================================
# TABLEAU FINAL
# =====================================================
st.subheader("📋 Dossiers filtrés")

cols = [
    "Dossier N", "Nom", "Date",
    "Categories", "Sous-categories", "Visa",
    "Total facturé", "Total encaissé", "Solde",
    "Escrow Montant",
    "Dossier envoye", "Dossier accepte", "Dossier refuse", "Dossier Annule",
]

st.dataframe(
    df_f[[c for c in cols if c in df_f.columns]],
    use_container_width=True,
    height=400
)