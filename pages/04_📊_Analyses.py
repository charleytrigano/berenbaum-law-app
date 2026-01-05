import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database

from components.analysis_charts import (
    monthly_hist,
    multi_year_line,
    category_donut,
    heatmap_month,
    category_bars
)

from components.analysis_escrow_charts import (
    escrow_state_donut,
    escrow_aging_bar,
    escrow_monthly_line
)

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(page_title="📊 Analyses", page_icon="📊", layout="wide")
render_sidebar()
st.title("📊 Analyses & indicateurs")

# =====================================================
# LOAD DATABASE
# =====================================================
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.warning("Aucune donnée disponible.")
    st.stop()

df = pd.DataFrame(clients).copy()

# =====================================================
# NORMALISATION
# =====================================================
df["Dossier N"] = df["Dossier N"].astype(str)

df["Date"] = pd.to_datetime(df.get("Date"), errors="coerce")
df["Année"] = df["Date"].dt.year
df["Mois"] = df["Date"].dt.to_period("M").astype(str)

for col in [
    "Dossier envoye", "Dossier accepte", "Dossier refuse",
    "Dossier Annule", "RFE",
    "Escrow", "Escrow_a_reclamer", "Escrow_reclame"
]:
    if col in df.columns:
        df[col] = df[col].astype(bool)
    else:
        df[col] = False

# =====================================================
# FILTRES
# =====================================================
st.subheader("🎛️ Filtres")

f1, f2, f3, f4, f5 = st.columns(5)

years = sorted(df["Année"].dropna().unique())
year = f1.selectbox("Année", ["Toutes"] + years)

categories = sorted(df["Categories"].dropna().unique())
categorie = f2.selectbox("Catégorie", ["Toutes"] + categories)

if categorie != "Toutes":
    souscats = sorted(df[df["Categories"] == categorie]["Sous-categories"].dropna().unique())
else:
    souscats = sorted(df["Sous-categories"].dropna().unique())

souscat = f3.selectbox("Sous-catégorie", ["Toutes"] + souscats)

if souscat != "Toutes":
    visas = sorted(df[df["Sous-categories"] == souscat]["Visa"].dropna().unique())
else:
    visas = sorted(df["Visa"].dropna().unique())

visa = f4.selectbox("Visa", ["Tous"] + visas)

statut = f5.selectbox(
    "Statut",
    ["Tous", "Envoyé", "Accepté", "Refusé", "Annulé", "RFE"]
)

# =====================================================
# APPLICATION FILTRES
# =====================================================
df_f = df.copy()

if year != "Toutes":
    df_f = df_f[df_f["Année"] == year]

if categorie != "Toutes":
    df_f = df_f[df_f["Categories"] == categorie]

if souscat != "Toutes":
    df_f = df_f[df_f["Sous-categories"] == souscat]

if visa != "Tous":
    df_f = df_f[df_f["Visa"] == visa]

if statut != "Tous":
    col_map = {
        "Envoyé": "Dossier envoye",
        "Accepté": "Dossier accepte",
        "Refusé": "Dossier refuse",
        "Annulé": "Dossier Annule",
        "RFE": "RFE"
    }
    df_f = df_f[df_f[col_map[statut]]]

# =====================================================
# KPI
# =====================================================
st.markdown("---")
st.subheader("📈 Indicateurs clés")

def to_float(v):
    try:
        return float(v or 0)
    except:
        return 0.0

hon = df_f.get("Montant honoraires (US $)", 0).apply(to_float).sum()
frais = df_f.get("Autres frais (US $)", 0).apply(to_float).sum()
total_facture = hon + frais

total_encaisse = 0.0
for i in range(1, 5):
    total_encaisse += df_f.get(f"Acompte {i}", 0).apply(to_float).sum()

solde = total_facture - total_encaisse

k1, k2, k3, k4, k5, k6, k7 = st.columns(7)

k1.metric("Dossiers", len(df_f))
k2.metric("Acceptés", df_f["Dossier accepte"].sum())
k3.metric("Refusés", df_f["Dossier refuse"].sum())
k4.metric("Annulés", df_f["Dossier Annule"].sum())
k5.metric("Total facturé", f"${total_facture:,.2f}")
k6.metric("Total encaissé", f"${total_encaisse:,.2f}")
k7.metric("Solde dû", f"${solde:,.2f}")

# =====================================================
# GRAPHIQUES CLASSIQUES
# =====================================================
st.markdown("---")
st.subheader("📊 Analyses générales")

t1, t2, t3, t4, t5 = st.tabs([
    "Histogramme mensuel",
    "Courbes multi-années",
    "Répartition catégories",
    "Heatmap activité",
    "Revenus par catégorie"
])

with t1:
    st.plotly_chart(monthly_hist(df_f), use_container_width=True)

with t2:
    st.plotly_chart(multi_year_line(df_f), use_container_width=True)

with t3:
    st.plotly_chart(category_donut(df_f), use_container_width=True)

with t4:
    st.plotly_chart(heatmap_month(df_f), use_container_width=True)

with t5:
    st.plotly_chart(category_bars(df_f), use_container_width=True)

# =====================================================
# ANALYSES ESCROW
# =====================================================
st.markdown("---")
st.subheader("🔐 Analyses Escrow")

e1, e2, e3 = st.tabs([
    "Répartition",
    "Ancienneté",
    "Évolution"
])

with e1:
    st.plotly_chart(
        escrow_state_donut(df_f),
        use_container_width=True
    )

with e2:
    st.plotly_chart(
        escrow_aging_bar(df_f),
        use_container_width=True
    )

with e3:
    fig = escrow_monthly_line(df_f)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Pas encore assez de données pour afficher l’évolution.")

# =====================================================
# TABLEAU FINAL
# =====================================================
st.markdown("---")
st.subheader("📋 Dossiers filtrés")

cols = [
    "Dossier N", "Nom", "Date",
    "Categories", "Sous-categories", "Visa",
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4",
    "Escrow", "Escrow_a_reclamer", "Escrow_reclame",
    "Dossier envoye", "Dossier accepte", "Dossier refuse", "Dossier Annule"
]

cols = [c for c in cols if c in df_f.columns]

st.dataframe(
    df_f.sort_values(["Date", "Dossier N"], ascending=[False, True])[cols],
    use_container_width=True,
    height=420
)