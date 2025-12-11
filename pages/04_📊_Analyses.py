import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database
from components.kpi_cards import kpi_card
from components.analysis_charts import (
    monthly_hist, multi_year_line, category_donut,
    heatmap_month, category_bars
)
from utils.sidebar import render_sidebar

# ---------------------------------------------------------
# 🎨 SIDEBAR PREMIUM (Logo + Navigation)
# ---------------------------------------------------------
render_sidebar()

# ---------------------------------------------------------
# ⚙️ CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="📊 Analyses", page_icon="📊", layout="wide")
st.title("📊 Analyses statistiques – Tableau de bord avancé")

# ---------------------------------------------------------
# 📥 CHARGEMENT BASE
# ---------------------------------------------------------
db = load_database()
clients = pd.DataFrame(db.get("clients", []))

if clients.empty:
    st.error("Aucun dossier trouvé.")
    st.stop()

# ---------------------------------------------------------
# 🧹 NORMALISATION DES COLONNES
# ---------------------------------------------------------
rename_statuts = {
    "Dossier accepté": "Dossier accepte",
    "Dossier Accepté": "Dossier accepte",
    "Dossier refuse": "Dossier refuse",
    "Dossier refusé": "Dossier refuse",
    "Dossier Refusé": "Dossier refuse",
    "Dossier annulé": "Dossier Annule",
    "Dossier Annulé": "Dossier Annule"
}

clients.rename(columns=rename_statuts, inplace=True)

# Colonnes à sécuriser
statut_cols = ["Dossier envoye", "Dossier accepte", "Dossier refuse", "Dossier Annule", "RFE"]

for col in statut_cols:
    if col not in clients.columns:
        clients[col] = False
    clients[col] = clients[col].apply(lambda x: str(x).lower() in ["true", "1", "yes", "oui"])

# Dates
clients["Date"] = pd.to_datetime(clients["Date"], errors="coerce")
clients["Année"] = clients["Date"].dt.year
clients["Mois"] = clients["Date"].dt.to_period("M").astype(str)

# ---------------------------------------------------------
# 🎛️ FILTRES AVANCÉS
# ---------------------------------------------------------
st.subheader("🎛️ Filtres avancés")

col1, col2, col3, col4 = st.columns(4)

# Catégories
categories = ["Tous"] + sorted([c for c in clients["Categories"].dropna().unique() if c != ""])
cat = col1.selectbox("Catégorie", categories)

# Sous-catégories dépendantes
if cat != "Tous":
    souscats = ["Tous"] + sorted(clients[clients["Categories"] == cat]["Sous-categories"].dropna().unique())
else:
    souscats = ["Tous"] + sorted(clients["Sous-categories"].dropna().unique())

sous = col2.selectbox("Sous-catégorie", souscats)

# Visa dépendant
if sous != "Tous":
    visas = ["Tous"] + sorted(clients[clients["Sous-categories"] == sous]["Visa"].dropna().unique())
else:
    visas = ["Tous"] + sorted(clients["Visa"].dropna().unique())

visa = col3.selectbox("Visa", visas)

# Statut
statuts = ["Tous", "Envoyé", "Accepté", "Refusé", "Annulé", "RFE"]
statut = col4.selectbox("Statut du dossier", statuts)

# ---------------------------------------------------------
# 🔍 APPLICATION DES FILTRES
# ---------------------------------------------------------
df = clients.copy()

if cat != "Tous":
    df = df[df["Categories"] == cat]

if sous != "Tous":
    df = df[df["Sous-categories"] == sous]

if visa != "Tous":
    df = df[df["Visa"] == visa]

# Filtre statut
mapping = {
    "Envoyé": "Dossier envoye",
    "Accepté": "Dossier accepte",
    "Refusé": "Dossier refuse",
    "Annulé": "Dossier Annule",
    "RFE": "RFE"
}

if statut != "Tous":
    df = df[df[mapping[statut]] == True]

# ---------------------------------------------------------
# 📆 COMPARAISONS TEMPORELLES
# ---------------------------------------------------------
st.subheader("📆 Comparaisons temporelles")

colT1, colT2 = st.columns(2)

periode_type = colT1.selectbox(
    "Type de période",
    ["Mois", "Trimestre", "Semestre", "Année"]
)

years = sorted(df["Année"].dropna().unique())
selected_years = colT2.multiselect(
    "Comparer jusqu’à 5 années",
    years,
    default=years[-2:] if len(years) >= 2 else years
)

# Filtrage temporel final
df_grouped = df[df["Année"].isin(selected_years)]

# ---------------------------------------------------------
# 📈 KPI
# ---------------------------------------------------------
st.subheader("📈 Indicateurs clés")

c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1: kpi_card("Total dossiers filtrés", len(df_grouped), "📁")
with c2: kpi_card("Chiffre d’affaires", int(df_grouped["Montant honoraires (US $)"].sum()), "💰")
with c3: kpi_card("Dossiers envoyés", int(df_grouped["Dossier envoye"].sum()), "📤")
with c4: kpi_card("Acceptés", int(df_grouped["Dossier accepte"].sum()), "✅")
with c5: kpi_card("Refusés", int(df_grouped["Dossier refuse"].sum()), "❌")
with c6: kpi_card("Escrow", int(df_grouped["Escrow"].sum()), "💼")

# ---------------------------------------------------------
# 📊 GRAPHES
# ---------------------------------------------------------
st.subheader("📊 Graphiques interactifs")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅 Histogramme mensuel",
    "📈 Courbes multi-années",
    "🎯 Répartition catégories",
    "🔥 Heatmap activité",
    "📊 Revenus par catégories"
])

with tab1:
    st.plotly_chart(monthly_hist(df_grouped), use_container_width=True)

with tab2:
    st.plotly_chart(multi_year_line(df_grouped), use_container_width=True)

with tab3:
    st.plotly_chart(category_donut(df_grouped), use_container_width=True)

with tab4:
    st.plotly_chart(heatmap_month(df_grouped), use_container_width=True)

with tab5:
    st.plotly_chart(category_bars(df_grouped), use_container_width=True)

# ---------------------------------------------------------
# 📋 TABLEAU FINAL
# ---------------------------------------------------------
st.subheader("📋 Dossiers filtrés")

show_cols = [
    "Dossier N", "Nom", "Date", "Categories", "Sous-categories",
    "Visa", "Montant honoraires (US $)", "Dossier envoye",
    "Dossier accepte", "Dossier refuse", "Escrow"
]

st.dataframe(df_grouped[show_cols], height=400, use_container_width=True)
