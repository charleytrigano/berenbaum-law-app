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
    category_bars
)

# ---------------------------------------------------------
# 🎨 SIDEBAR PREMIUM
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

# Harmonisation colonnes booléennes
rename_map = {
    "Dossier_envoye": "Dossier envoye",
    "Dossier Envoye": "Dossier envoye",
    "Dossier envoyé": "Dossier envoye",
}
clients.rename(columns=rename_map, inplace=True)

if "Dossier envoye" not in clients.columns:
    clients["Dossier envoye"] = False

if clients.empty:
    st.error("Aucun dossier trouvé.")
    st.stop()

# ---------------------------------------------------------
# 🧹 NORMALISATION
# ---------------------------------------------------------
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
    souscats = ["Tous"] + sorted(
        clients[clients["Categories"] == cat]["Sous-categories"].dropna().unique()
    )
else:
    souscats = ["Tous"] + sorted(clients["Sous-categories"].dropna().unique())

sous = col2.selectbox("Sous-catégorie", souscats)

# Visa dépendant
if sous != "Tous":
    visas = ["Tous"] + sorted(
        clients[clients["Sous-categories"] == sous]["Visa"].dropna().unique()
    )
else:
    visas = ["Tous"] + sorted(clients["Visa"].dropna().unique())

visa = col3.selectbox("Visa", visas)

# Statuts
statuts = ["Tous", "Envoyé", "Accepté", "Refusé", "Annulé", "RFE"]
statut = col4.selectbox("Statut du dossier", statuts)

# ---------------------------------------------------------
# 🔍 APPLICATION FILTRES
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

periode_type = colT1.selectbox(
    "Type de période", ["Mois", "Trimestre", "Semestre", "Année", "Date à date"]
)

years = sorted(df["Année"].dropna().unique())
selected_years = colT2.multiselect(
    "Comparer jusqu’à 5 années",
    years,
    default=years[-2:] if len(years) >= 2 else years
)

# Groupement multi-années
df_grouped = (
    df.groupby(["Année", df["Date"].dt.month])["Montant honoraires (US $)"]
    .sum()
    .reset_index()
)
df_grouped.rename(columns={"Date": "Mois"}, inplace=True)

# ---------------------------------------------------------
# 🔢 KPI PREMIUM
# ---------------------------------------------------------
st.subheader("📈 Indicateurs clés")

colA, colB, colC, colD, colE, colF = st.columns(6)

with colA:
    kpi_card("Total dossiers filtrés", len(df), "📁")
with colB:
    kpi_card("CA filtré", int(df["Montant honoraires (US $)"].sum()), "💰")
with colC:
    kpi_card("Dossiers envoyés", int(df["Dossier envoye"].sum()), "📤")
with colD:
    kpi_card("Acceptés", int(df["Dossier accepte"].sum()), "✅")
with colE:
    kpi_card("Refusés", int(df["Dossier refuse"].sum()), "❌")
with colF:
    kpi_card("Escrow actifs", int(df["Escrow"].sum()), "💼")

# ---------------------------------------------------------
# 📊 GRAPHIQUES
# ---------------------------------------------------------
st.subheader("📊 Graphiques interactifs")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📅 Histogramme mensuel", "📈 Multi-années",
     "🎯 Répartition catégories", "🔥 Heatmap", "📊 Revenus par catégories"]
)

with tab1:
    # ✅ FIX : monthly_hist doit recevoir df, PAS df_grouped
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
# 📋 TABLEAU FINAL
# ---------------------------------------------------------
st.subheader("📋 Détails des dossiers filtrés")

cols = [
    "Dossier N", "Nom", "Date", "Categories", "Sous-categories", "Visa",
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Dossier envoye", "Dossier accepte", "Dossier refuse",
    "Escrow"
]

st.dataframe(df[cols], height=450, use_container_width=True)

st.markdown("### 🌟 Tableau de bord premium — Berenbaum Law App")
