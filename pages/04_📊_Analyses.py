import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database
from utils.sidebar import render_sidebar
from components.kpi_cards import kpi_card
from components.analysis_charts import (
    monthly_hist,
    multi_year_line,
    category_donut,
    heatmap_month,
    category_bars,
)

# ---------------------------------------------------------
# 🎨 SIDEBAR PREMIUM (Logo + Navigation)
# ---------------------------------------------------------
render_sidebar()

# ---------------------------------------------------------
# ⚙️ CONFIG PAGE
# ---------------------------------------------------------
st.set_page_config(page_title="📊 Analyses", page_icon="📊", layout="wide")
st.title("📊 Analyses statistiques — Dashboard complet & intelligent")

# ---------------------------------------------------------
# 📥 CHARGEMENT BASE
# ---------------------------------------------------------
db = load_database()
clients = pd.DataFrame(db.get("clients", []))

# Harmoniser les noms de colonnes
rename_map = {
    "Dossier_envoye": "Dossier envoye",
    "Dossier envoyé": "Dossier envoye",
    "Dossier Envoye": "Dossier envoye",
}
clients.rename(columns=rename_map, inplace=True)

if "Dossier envoye" not in clients.columns:
    clients["Dossier envoye"] = False

if clients.empty:
    st.error("Aucun dossier trouvé.")
    st.stop()

# ---------------------------------------------------------
# 🧹 Nettoyage dates & colonnes
# ---------------------------------------------------------
clients["Date"] = pd.to_datetime(clients["Date"], errors="coerce")
clients["Année"] = clients["Date"].dt.year
clients["Mois"] = clients["Date"].dt.to_period("M").astype(str)

# ---------------------------------------------------------
# 🎛️ FILTRES AVANCÉS
# ---------------------------------------------------------
st.subheader("🎛️ Filtres avancés")

col1, col2, col3, col4 = st.columns(4)

# Catégorie
categories_list = ["Tous"] + sorted([c for c in clients["Categories"].dropna().unique() if c != ""])
cat = col1.selectbox("Catégorie", categories_list)

# Sous-catégorie dépendante
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
# 🔍 APPLICATION DES FILTRES GÉNÉRAUX
# ---------------------------------------------------------
df = clients.copy()

if cat != "Tous":
    df = df[df["Categories"] == cat]

if sous != "Tous":
    df = df[df["Sous-categories"] == sous]

if visa != "Tous":
    df = df[df["Visa"] == visa]

if statut != "Tous":
    mapping = {
        "Envoyé": "Dossier envoye",
        "Accepté": "Dossier accepte",
        "Refusé": "Dossier refuse",
        "Annulé": "Dossier Annule",
        "RFE": "RFE"
    }
    df = df[df[mapping[statut]] == True]

# ---------------------------------------------------------
# 📆 COMPARAISONS TEMPORELLES
# ---------------------------------------------------------
st.subheader("📆 Comparaisons temporelles")

colT1, colT2 = st.columns(2)

periode_type = colT1.selectbox("Type de période", ["Mois", "Trimestre", "Semestre", "Année", "Date à date"])

years = sorted(df["Année"].dropna().unique())
selected_years = colT2.multiselect(
    "Comparer jusqu’à 5 années",
    years,
    default=years[-2:] if len(years) >= 2 else years
)

# ---------------------------------------------------------
# 🕒 APPLICATION DU FILTRE TEMPOREL — SYNCHRO TOTALE
# ---------------------------------------------------------
df_time_filtered = df.copy()

# Filtrer par années sélectionnées
if len(selected_years) > 0:
    df_time_filtered = df_time_filtered[df_time_filtered["Année"].isin(selected_years)]

# Groupement multi-année pour les courbes
df_grouped = (
    df_time_filtered
    .groupby(["Année", "Mois"])["Montant honoraires (US $)"]
    .sum()
    .reset_index()
)

# ---------------------------------------------------------
# 🔢 KPI PREMIUM — parfaitement synchronisés
# ---------------------------------------------------------
st.subheader("📈 Indicateurs clés")

colK1, colK2, colK3, colK4, colK5, colK6 = st.columns(6)

kpi_card("Total dossiers filtrés", len(df_time_filtered), "📁")
kpi_card("Chiffre d’affaires (Filtré)", int(df_time_filtered["Montant honoraires (US $)"].sum()), "💰")
kpi_card("Dossiers envoyés", int(df_time_filtered["Dossier envoye"].sum()), "📤")
kpi_card("Dossiers acceptés", int(df_time_filtered["Dossier accepte"].sum()), "✅")
kpi_card("Dossiers refusés", int(df_time_filtered["Dossier refuse"].sum()), "❌")
kpi_card("Dossiers en Escrow", int(df_time_filtered["Escrow"].sum()), "💼")

# ---------------------------------------------------------
# 📊 GRAPHIQUES — cohérents avec les filtres
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
    st.plotly_chart(monthly_hist(df_time_filtered), use_container_width=True)

with tab2:
    st.plotly_chart(multi_year_line(df_grouped), use_container_width=True)

with tab3:
    st.plotly_chart(category_donut(df_time_filtered), use_container_width=True)

with tab4:
    st.plotly_chart(heatmap_month(df_time_filtered), use_container_width=True)

with tab5:
    st.plotly_chart(category_bars(df_time_filtered), use_container_width=True)

# ---------------------------------------------------------
# 📋 TABLEAU DÉTAILLÉ
# ---------------------------------------------------------
st.subheader("📋 Détails des dossiers filtrés")

df_display = df_time_filtered[[
    "Dossier N", "Nom", "Date",
    "Categories", "Sous-categories", "Visa",
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Dossier envoye", "Dossier accepte", "Dossier refuse",
    "Escrow"
]]

st.dataframe(df_display, height=400, use_container_width=True)

# ---------------------------------------------------------
# FIN
# ---------------------------------------------------------
st.markdown("### 🌟 Tableau de bord premium — Berenbaum Law App")
