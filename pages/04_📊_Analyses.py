import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database
from utils.dossier_hierarchy import add_hierarchy_columns
from components.analysis_charts import (
    monthly_hist,
    multi_year_line,
    category_donut,
    heatmap_month,
    category_bars,
)

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="📊 Analyses", page_icon="📊", layout="wide")
render_sidebar()
st.title("📊 Analyses statistiques")

# ---------------------------------------------------------
# LOAD
# ---------------------------------------------------------
db = load_database()
df = pd.DataFrame(db.get("clients", []))

if df.empty:
    st.stop()

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Année"] = df["Date"].dt.year
df["Mois"] = df["Date"].dt.to_period("M").astype(str)
df = add_hierarchy_columns(df)

# ---------------------------------------------------------
# FILTRES
# ---------------------------------------------------------
st.subheader("🎛️ Filtres")

c1, c2, c3, c4 = st.columns(4)

annees = sorted(df["Année"].dropna().unique())
annee = c1.multiselect("Année", annees, default=annees)

cats = ["Tous"] + sorted(df["Categories"].dropna().unique())
cat = c2.selectbox("Catégorie", cats)

if cat != "Tous":
    df = df[df["Categories"] == cat]

souscats = ["Tous"] + sorted(df["Sous-categories"].dropna().unique())
sous = c3.selectbox("Sous-catégorie", souscats)

if sous != "Tous":
    df = df[df["Sous-categories"] == sous]

visas = ["Tous"] + sorted(df["Visa"].dropna().unique())
visa = c4.selectbox("Visa", visas)

if visa != "Tous":
    df = df[df["Visa"] == visa]

df = df[df["Année"].isin(annee)]

# ---------------------------------------------------------
# KPI
# ---------------------------------------------------------
st.subheader("📈 KPI filtrés")

k1, k2, k3, k4 = st.columns(4)

with k1:
    kpi_card("Dossiers", len(df), "📁")
with k2:
    kpi_card("Honoraires", f"${df['Montant honoraires (US $)'].sum():,.0f}", "💼")
with k3:
    kpi_card("Encaissé", f"${df[['Acompte 1','Acompte 2','Acompte 3','Acompte 4']].sum().sum():,.0f}", "🏦")
with k4:
    kpi_card("Escrow", f"${df[df['Escrow']==True]['Acompte 1'].sum():,.0f}", "🔒")

# ---------------------------------------------------------
# GRAPHIQUES
# ---------------------------------------------------------
st.subheader("📊 Graphiques")

t1, t2, t3, t4, t5 = st.tabs([
    "📅 Mensuel",
    "📈 Multi-années",
    "🎯 Catégories",
    "🔥 Heatmap",
    "📊 Revenus",
])

with t1:
    st.plotly_chart(monthly_hist(df), use_container_width=True)
with t2:
    st.plotly_chart(multi_year_line(df), use_container_width=True)
with t3:
    st.plotly_chart(category_donut(df), use_container_width=True)
with t4:
    st.plotly_chart(heatmap_month(df), use_container_width=True)
with t5:
    st.plotly_chart(category_bars(df), use_container_width=True)