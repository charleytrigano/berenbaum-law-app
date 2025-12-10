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
# SIDEBAR
# ---------------------------------------------------------
render_sidebar()

st.set_page_config(page_title="📊 Analyses", page_icon="📊", layout="wide")
st.title("📊 Analyses statistiques – Tableau de bord avancé")


# ---------------------------------------------------------
# CHARGEMENT BASE
# ---------------------------------------------------------
db = load_database()
clients = pd.DataFrame(db.get("clients", []))

rename_map = {
    "Dossier_envoye": "Dossier envoye",
    "Dossier envoyé": "Dossier envoye",
}
clients.rename(columns=rename_map, inplace=True)

if "Dossier envoye" not in clients:
    clients["Dossier envoye"] = False

if clients.empty:
    st.warning("Aucun dossier trouvé.")
    st.stop()

clients["Date"] = pd.to_datetime(clients["Date"], errors="coerce")
clients["Année"] = clients["Date"].dt.year
clients["Mois"] = clients["Date"].dt.month


# ---------------------------------------------------------
# FILTRES AVANCES
# ---------------------------------------------------------
st.subheader("🎛️ Filtres avancés")

col1, col2, col3, col4 = st.columns(4)

categories = ["Tous"] + sorted([x for x in clients["Categories"].dropna().unique() if x != ""])
cat = col1.selectbox("Catégorie", categories)

if cat != "Tous":
    souscats = ["Tous"] + sorted(clients[clients["Categories"] == cat]["Sous-categories"].dropna().unique())
else:
    souscats = ["Tous"] + sorted(clients["Sous-categories"].dropna().unique())

sous = col2.selectbox("Sous-catégorie", souscats)

if sous != "Tous":
    visas = ["Tous"] + sorted(clients[clients["Sous-categories"] == sous]["Visa"].dropna().unique())
else:
    visas = ["Tous"] + sorted(clients["Visa"].dropna().unique())

visa = col3.selectbox("Visa", visas)


statuts = ["Tous", "Envoyé", "Accepté", "Refusé", "Annulé", "RFE"]
statut = col4.selectbox("Statut", statuts)


df = clients.copy()

if cat != "Tous": df = df[df["Categories"] == cat]
if sous != "Tous": df = df[df["Sous-categories"] == sous]
if visa != "Tous": df = df[df["Visa"] == visa]

mapping = {
    "Envoyé": "Dossier envoye",
    "Accepté": "Dossier accepte",
    "Refusé": "Dossier refuse",
    "Annulé": "Dossier Annule",
    "RFE": "RFE",
}
if statut != "Tous":
    df = df[df[mapping[statut]] == True]


# ---------------------------------------------------------
# FILTRES TEMPORELS
# ---------------------------------------------------------
st.subheader("📆 Comparaisons temporelles")

colA, colB = st.columns(2)

periode = colA.selectbox("Type de période", ["Mois", "Trimestre", "Semestre", "Année"])
years = sorted(df["Année"].dropna().unique())

selected_years = colB.multiselect(
    "Comparer plusieurs années",
    options=years,
    default=years[-2:] if len(years) >= 2 else years
)

# Groupement pour multi-année
df_grouped = (
    df[df["Année"].isin(selected_years)]
    .groupby(["Année", "Mois"])["Montant honoraires (US $)"]
    .sum()
    .reset_index()
)


# ---------------------------------------------------------
# KPI
# ---------------------------------------------------------
st.subheader("📈 Indicateurs clés")

colK1, colK2, colK3, colK4, colK5, colK6 = st.columns(6)

with colK1: kpi_card("Total dossiers filtrés", len(df), "📁")
with colK2: kpi_card("Chiffre d’affaires", int(df["Montant honoraires (US $)"].sum()), "💰")
with colK3: kpi_card("Envoyés", int(df["Dossier envoye"].sum()), "📤")
with colK4: kpi_card("Acceptés", int(df["Dossier accepte"].sum()), "✅")
with colK5: kpi_card("Refusés", int(df["Dossier refuse"].sum()), "❌")
with colK6: kpi_card("Escrow", int(df["Escrow"].sum()), "💼")


# ---------------------------------------------------------
# GRAPHIQUES
# ---------------------------------------------------------
st.subheader("📊 Graphiques interactifs")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅 Histogramme mensuel",
    "📈 Multi-années",
    "🎯 Catégories",
    "🔥 Heatmap",
    "📊 Revenus catégories"
])

with tab1:
    st.plotly_chart(monthly_hist(df), use_container_width=True)

with tab2:
    st.plotly_chart(multi_year_line(df_grouped), use_container_width=True)

with tab3:
    st.plotly_chart(category_donut(df), use_container_width=True)

with tab4:
    st.plotly_chart(heatmap_month(df), use_container_width=True)

with tab5:
    st.plotly_chart(category_bars(df), use_container_width=True)


# ---------------------------------------------------------
# TABLEAU
# ---------------------------------------------------------
st.subheader("📋 Dossiers filtrés")

st.dataframe(
    df[[
        "Dossier N", "Nom", "Date",
        "Categories", "Sous-categories", "Visa",
        "Montant honoraires (US $)", "Autres frais (US $)",
        "Dossier envoye", "Dossier accepte", "Dossier refuse",
        "Escrow"
    ]],
    use_container_width=True,
    height=350
)
