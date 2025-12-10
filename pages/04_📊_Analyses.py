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
# ⚙️ CONFIG PAGE
# ---------------------------------------------------------
st.set_page_config(page_title="📊 Analyses", page_icon="📊", layout="wide")
st.title("📊 Analyses statistiques – Tableau de bord avancé")

# ---------------------------------------------------------
# 📥 CHARGEMENT BASE
# ---------------------------------------------------------
db = load_database()
clients = pd.DataFrame(db.get("clients", []))
# 🔧 Harmonisation des noms de colonnes
rename_map = {
    "Dossier_envoye": "Dossier envoye",
    "Dossier Envoye": "Dossier envoye",
    "Dossier envoyé": "Dossier envoye",
}

clients.rename(columns=rename_map, inplace=True)

# Si la colonne est manquante → la créer par sécurité
if "Dossier envoye" not in clients.columns:
    clients["Dossier envoye"] = False


if clients.empty:
    st.error("Aucun dossier trouvé dans la base.")
    st.stop()

# ---------------------------------------------------------
# 🧹 Normalisation dates & colonnes
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

# Statut dossier
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
# 📆 FILTRES TEMPORELS
# ---------------------------------------------------------
st.subheader("📆 Comparaisons temporelles")

colT1, colT2 = st.columns(2)

periode_type = colT1.selectbox(
    "Type de période",
    ["Mois", "Trimestre", "Semestre", "Année", "Date à date"]
)

# Sélection d'années (2 à 5)
years = sorted(df["Année"].dropna().unique())
selected_years = colT2.multiselect(
    "Comparer jusqu’à 5 années",
    years,
    default=years[-2:] if len(years) >= 2 else years
)

# ---------------------------------------------------------
# 🔢 KPI PREMIUM (luxury gold cards)
# ---------------------------------------------------------
st.subheader("📈 Indicateurs clés")

colK1, colK2, colK3 = st.columns(3)
colK4, colK5, colK6 = st.columns(3)

kpi_card("Total dossiers filtrés", len(df), "📁")
kpi_card("Chiffre d’affaires (Filtré)", int(df["Montant honoraires (US $)"].sum()), "💰")
kpi_card("Dossiers envoyés", int(df.get("Dossier envoye", 0).sum()), "📤")


kpi_card("Dossiers acceptés", int(df["Dossier accepte"].sum()), "✅")
kpi_card("Dossiers refusés", int(df["Dossier refuse"].sum()), "❌")
kpi_card("Dossiers en Escrow", int(df["Escrow"].sum()), "💼")

# ---------------------------------------------------------
# 📊 GRAPHIQUES PREMIUM
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
    st.plotly_chart(monthly_hist(df), use_container_width=True)

with tab2:
    st.plotly_chart(multi_year_line(df), use_container_width=True)

with tab3:
    st.plotly_chart(category_donut(df), use_container_width=True)

with tab4:
    st.plotly_chart(heatmap_month(df), use_container_width=True)

with tab5:
    st.plotly_chart(category_bars(df), use_container_width=True)

# ---------------------------------------------------------
# 📋 TABLEAU FINAL DES DOSSIERS
# ---------------------------------------------------------
st.subheader("📋 Détails des dossiers filtrés")

df_display = df[[
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
# ==========================================================
# 🎨 KPI CARD – Version premium stable (ne fuite JAMAIS en brut)
# ==========================================================

def kpi_card(label, value, icon):

    html = f"""
    <div style="
        background: rgba(255, 255, 255, 0.06);
        padding: 14px 18px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 0 8px rgba(255,255,255,0.05);
        text-align: left;
        min-height: 95px;
    ">
        <div style="font-size: 26px; margin-bottom: 4px;">
            {icon}
        </div>

        <div style="
            font-size: 15px;
            font-weight: 500;
            color: #D8B86A;
            margin-bottom: 6px;
            white-space: nowrap;
        ">
            {label}
        </div>

        <div style="
            font-size: 28px;
            font-weight: 700;
            color: #FFD777;
        ">
            {value:,}
        </div>
    </div>
    """

    # 👉 Ce mode d'affichage est le SEUL correct :
    st.markdown(html, unsafe_allow_html=True)
