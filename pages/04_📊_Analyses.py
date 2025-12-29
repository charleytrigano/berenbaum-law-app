# pages/04_📊_Analyses.py
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
    top_visa,  # bonus (non bloquant)
)

# ---------------------------------------------------------
# SIDEBAR + CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="📊 Analyses", page_icon="📊", layout="wide")
render_sidebar()
st.title("📊 Analyses statistiques – Tableau de bord avancé")

# ---------------------------------------------------------
# LOAD DB
# ---------------------------------------------------------
db = load_database()
clients = pd.DataFrame(db.get("clients", []))

# Harmonisation colonnes statuts (protection)
rename_map = {
    "Dossier_envoye": "Dossier envoye",
    "Dossier Envoye": "Dossier envoye",
    "Dossier envoyé": "Dossier envoye",
}
clients.rename(columns=rename_map, inplace=True)

if clients.empty:
    st.error("Aucun dossier trouvé dans la base.")
    st.stop()

# ---------------------------------------------------------
# Normalisation dates + colonnes auxiliaires
# ---------------------------------------------------------
if "Date" not in clients.columns:
    clients["Date"] = None

clients["Date"] = pd.to_datetime(clients["Date"], errors="coerce")
clients["Année"] = clients["Date"].dt.year
clients["Mois"] = clients["Date"].dt.to_period("M").astype(str)

# Garantir colonnes bool clés
for col in [
    "Dossier envoye",
    "Dossier accepte",
    "Dossier refuse",
    "Dossier Annule",
    "RFE",
    "Escrow",
    "Escrow_a_reclamer",
    "Escrow_reclame",
]:
    if col not in clients.columns:
        clients[col] = False

def _bool(v):
    if isinstance(v, bool):
        return v
    if v is None:
        return False
    return str(v).strip().lower() in ["true", "1", "yes", "oui", "y", "vrai"]

for col in [
    "Dossier envoye",
    "Dossier accepte",
    "Dossier refuse",
    "Dossier Annule",
    "RFE",
    "Escrow",
    "Escrow_a_reclamer",
    "Escrow_reclame",
]:
    clients[col] = clients[col].apply(_bool)

# ---------------------------------------------------------
# FILTRES AVANCÉS
# ---------------------------------------------------------
st.subheader("🎛️ Filtres avancés")
col1, col2, col3, col4 = st.columns(4)

# Catégorie
if "Categories" not in clients.columns:
    clients["Categories"] = ""
categories = ["Tous"] + sorted([c for c in clients["Categories"].dropna().unique() if str(c).strip() != ""])
cat = col1.selectbox("Catégorie", categories)

# Sous-catégorie dépendante
if "Sous-categories" not in clients.columns:
    clients["Sous-categories"] = ""
if cat != "Tous":
    souscats = ["Tous"] + sorted(
        clients[clients["Categories"] == cat]["Sous-categories"].dropna().unique().tolist()
    )
else:
    souscats = ["Tous"] + sorted(clients["Sous-categories"].dropna().unique().tolist())
sous = col2.selectbox("Sous-catégorie", souscats)

# Visa dépendant
if "Visa" not in clients.columns:
    clients["Visa"] = ""
if sous != "Tous":
    visas = ["Tous"] + sorted(
        clients[clients["Sous-categories"] == sous]["Visa"].dropna().unique().tolist()
    )
else:
    visas = ["Tous"] + sorted(clients["Visa"].dropna().unique().tolist())
visa = col3.selectbox("Visa", visas)

# Statut dossier
statuts = ["Tous", "Envoyé", "Accepté", "Refusé", "Annulé", "RFE"]
statut = col4.selectbox("Statut du dossier", statuts)

# ---------------------------------------------------------
# APPLICATION DES FILTRES
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
        "RFE": "RFE",
    }
    df = df[df[mapping[statut]] == True]

# ---------------------------------------------------------
# COMPARAISONS TEMPORELLES
# ---------------------------------------------------------
st.subheader("📆 Comparaisons temporelles")
colT1, colT2 = st.columns(2)

periode_type = colT1.selectbox(
    "Type de période",
    ["Mois", "Trimestre", "Semestre", "Année", "Date à date"]
)

years_all = sorted([int(y) for y in df["Année"].dropna().unique().tolist() if pd.notna(y)])
selected_years = colT2.multiselect(
    "Comparer jusqu’à 5 années",
    years_all,
    default=years_all[-2:] if len(years_all) >= 2 else years_all,
    max_selections=5,
)

# ---------------------------------------------------------
# KPI
# ---------------------------------------------------------
st.subheader("📈 Indicateurs clés")

# Colonnes montants
if "Montant honoraires (US $)" not in df.columns:
    df["Montant honoraires (US $)"] = 0.0
if "Autres frais (US $)" not in df.columns:
    df["Autres frais (US $)"] = 0.0
if "Acompte 1" not in df.columns:
    df["Acompte 1"] = 0.0

df["Montant honoraires (US $)"] = pd.to_numeric(df["Montant honoraires (US $)"], errors="coerce").fillna(0.0)
df["Autres frais (US $)"] = pd.to_numeric(df["Autres frais (US $)"], errors="coerce").fillna(0.0)
df["Acompte 1"] = pd.to_numeric(df["Acompte 1"], errors="coerce").fillna(0.0)

colK1, colK2, colK3, colK4, colK5, colK6 = st.columns(6)

with colK1:
    kpi_card("Total dossiers filtrés", len(df), "📁")
with colK2:
    kpi_card("Chiffre d’affaires (Filtré)", int(df["Montant honoraires (US $)"].sum()), "💰")
with colK3:
    kpi_card("Dossiers envoyés", int(df["Dossier envoye"].sum()), "📤")
with colK4:
    kpi_card("Dossiers acceptés", int(df["Dossier accepte"].sum()), "✅")
with colK5:
    kpi_card("Dossiers refusés", int(df["Dossier refuse"].sum()), "❌")
with colK6:
    kpi_card("Dossiers annulés", int(df["Dossier Annule"].sum()), "🛑")

# KPI Escrow (Acompte 1 uniquement si un des états escrow est vrai)
escrow_mask = (df["Escrow"] | df["Escrow_a_reclamer"] | df["Escrow_reclame"])
escrow_total = float(df.loc[escrow_mask, "Acompte 1"].sum())
st.info(f"💼 Total Escrow (Acompte 1 uniquement) : **${escrow_total:,.2f}**")

# ---------------------------------------------------------
# GRAPHIQUES
# ---------------------------------------------------------
st.subheader("📊 Graphiques interactifs")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📅 Histogramme (période)",
    "📈 Courbes multi-années",
    "🎯 Répartition catégories",
    "🔥 Heatmap activité",
    "📊 Revenus par catégories",
    "🛂 Top Visas (bonus)",
])

with tab1:
    st.plotly_chart(monthly_hist(df, period_type=periode_type), use_container_width=True)

with tab2:
    # IMPORTANT : on passe df (avec Date), pas un df groupé
    st.plotly_chart(multi_year_line(df, years=selected_years), use_container_width=True)

with tab3:
    st.plotly_chart(category_donut(df), use_container_width=True)

with tab4:
    st.plotly_chart(heatmap_month(df), use_container_width=True)

with tab5:
    st.plotly_chart(category_bars(df), use_container_width=True)

with tab6:
    st.plotly_chart(top_visa(df, top_n=12), use_container_width=True)

# ---------------------------------------------------------
# TABLEAU FINAL
# ---------------------------------------------------------
st.subheader("📋 Détails des dossiers filtrés")

wanted = [
    "Dossier N", "Nom", "Date",
    "Categories", "Sous-categories", "Visa",
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Dossier envoye", "Dossier accepte", "Dossier refuse", "Dossier Annule", "RFE",
    "Escrow", "Escrow_a_reclamer", "Escrow_reclame",
]
cols = [c for c in wanted if c in df.columns]

st.dataframe(df[cols].copy(), height=420, use_container_width=True)

st.markdown("### 🌟 Tableau de bord premium — Berenbaum Law App")
