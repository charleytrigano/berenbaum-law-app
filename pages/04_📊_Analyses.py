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

# ---------------------------------------------------------
# CONFIG & SIDEBAR
# ---------------------------------------------------------
st.set_page_config(page_title="📊 Analyses", page_icon="📊", layout="wide")
render_sidebar()
st.title("📊 Analyses & Statistiques")

# ---------------------------------------------------------
# CHARGEMENT BASE
# ---------------------------------------------------------
db = load_database()
clients_raw = db.get("clients", [])

if not clients_raw:
    st.warning("Aucun dossier trouvé dans la base.")
    st.stop()

df = pd.DataFrame(clients_raw)

# ---------------------------------------------------------
# NORMALISATION COLONNES
# ---------------------------------------------------------

# Harmonisation possible des alias de statuts
rename_map = {
    "Dossier_envoye": "Dossier envoye",
    "Dossier Envoye": "Dossier envoye",
    "Dossier envoyé": "Dossier envoye",
    "Dossier_accepte": "Dossier accepte",
    "Dossier accepté": "Dossier accepte",
    "Dossier refuse": "Dossier refuse",
    "Dossier_refuse": "Dossier refuse",
    "Dossier refusé": "Dossier refuse",
    "Dossier annulé": "Dossier Annule",
    "Dossier_annule": "Dossier Annule",
}

df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

# Garantir les colonnes booléennes
for col in [
    "Dossier envoye",
    "Dossier accepte",
    "Dossier refuse",
    "Dossier Annule",
    "RFE",
    "Escrow",
]:
    if col not in df.columns:
        df[col] = False

def to_bool(x):
    if isinstance(x, bool):
        return x
    if x is None:
        return False
    s = str(x).strip().lower()
    return s in ["true", "1", "1.0", "yes", "oui", "y", "vrai"]

for col in ["Dossier envoye", "Dossier accepte", "Dossier refuse", "Dossier Annule", "RFE", "Escrow"]:
    df[col] = df[col].apply(to_bool)

# Dates & temps
df["Date"] = pd.to_datetime(df.get("Date"), errors="coerce")
df["Année"] = df["Date"].dt.year
df["Mois"] = df["Date"].dt.to_period("M").astype(str)

# Numérique
for col in ["Montant honoraires (US $)", "Autres frais (US $)"]:
    df[col] = pd.to_numeric(df.get(col, 0), errors="coerce").fillna(0)

for i in range(1, 5):
    col_ac = f"Acompte {i}"
    if col_ac in df.columns:
        df[col_ac] = pd.to_numeric(df[col_ac], errors="coerce").fillna(0.0)
    else:
        df[col_ac] = 0.0

# ---------------------------------------------------------
# FILTRES
# ---------------------------------------------------------
st.subheader("🎛️ Filtres")

col_f1, col_f2, col_f3, col_f4 = st.columns(4)

# Catégorie
categories = ["Tous"] + sorted(
    [c for c in df["Categories"].dropna().unique().tolist() if c != ""]
)
filtre_cat = col_f1.selectbox("Catégorie", categories)

# Sous-catégorie (dépendante de la catégorie)
if filtre_cat != "Tous":
    souscats = ["Tous"] + sorted(
        df[df["Categories"] == filtre_cat]["Sous-categories"].dropna().unique().tolist()
    )
else:
    souscats = ["Tous"] + sorted(
        [s for s in df["Sous-categories"].dropna().unique().tolist() if s != ""]
    )
filtre_souscat = col_f2.selectbox("Sous-catégorie", souscats)

# Visa (dépendant de la sous-catégorie si filtrée)
if filtre_souscat != "Tous":
    visas = ["Tous"] + sorted(
        df[df["Sous-categories"] == filtre_souscat]["Visa"].dropna().unique().tolist()
    )
else:
    visas = ["Tous"] + sorted(
        [v for v in df["Visa"].dropna().unique().tolist() if v != ""]
    )
filtre_visa = col_f3.selectbox("Visa", visas)

# Statut
statuts = ["Tous", "Envoyé", "Accepté", "Refusé", "Annulé", "RFE"]
filtre_statut = col_f4.selectbox("Statut du dossier", statuts)

# ---------------------------------------------------------
# APPLICATION DES FILTRES
# ---------------------------------------------------------
df_filtre = df.copy()

if filtre_cat != "Tous":
    df_filtre = df_filtre[df_filtre["Categories"] == filtre_cat]

if filtre_souscat != "Tous":
    df_filtre = df_filtre[df_filtre["Sous-categories"] == filtre_souscat]

if filtre_visa != "Tous":
    df_filtre = df_filtre[df_filtre["Visa"] == filtre_visa]

if filtre_statut != "Tous":
    mapping_statut = {
        "Envoyé": "Dossier envoye",
        "Accepté": "Dossier accepte",
        "Refusé": "Dossier refuse",
        "Annulé": "Dossier Annule",
        "RFE": "RFE",
    }
    col_statut = mapping_statut[filtre_statut]
    df_filtre = df_filtre[df_filtre[col_statut] == True]

# ---------------------------------------------------------
# KPI
# ---------------------------------------------------------
st.subheader("📈 Indicateurs clés")

k1, k2, k3, k4, k5, k6 = st.columns(6)

with k1:
    kpi_card("Dossiers filtrés", len(df_filtre), "📁")

with k2:
    kpi_card(
        "CA honoraires (US $)",
        float(df_filtre["Montant honoraires (US $)"].sum()),
        "💰",
    )

with k3:
    kpi_card(
        "Autres frais (US $)",
        float(df_filtre["Autres frais (US $)"].sum()),
        "💵",
    )

with k4:
    kpi_card("Dossiers envoyés", int(df_filtre["Dossier envoye"].sum()), "📤")

with k5:
    kpi_card("Dossiers acceptés", int(df_filtre["Dossier accepte"].sum()), "✅")

with k6:
    kpi_card("Dossiers refusés", int(df_filtre["Dossier refuse"].sum()), "❌")

# ---------------------------------------------------------
# GRAPHIQUES
# ---------------------------------------------------------
st.subheader("📊 Graphiques interactifs")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📅 Histogramme mensuel",
        "📈 Courbes multi-années",
        "🎯 Répartition catégories",
        "🔥 Heatmap activité",
        "📊 Revenus par catégories",
    ]
)

with tab1:
    st.plotly_chart(monthly_hist(df_filtre), use_container_width=True)

with tab2:
    st.plotly_chart(multi_year_line(df_filtre), use_container_width=True)

with tab3:
    st.plotly_chart(category_donut(df_filtre), use_container_width=True)

with tab4:
    st.plotly_chart(heatmap_month(df_filtre), use_container_width=True)

with tab5:
    st.plotly_chart(category_bars(df_filtre), use_container_width=True)

# ---------------------------------------------------------
# TABLEAU DES DOSSIERS FILTRÉS
# ---------------------------------------------------------
st.subheader("📋 Détails des dossiers filtrés")

cols_display = [
    "Dossier N",
    "Nom",
    "Date",
    "Categories",
    "Sous-categories",
    "Visa",
    "Montant honoraires (US $)",
    "Autres frais (US $)",
    "Dossier envoye",
    "Dossier accepte",
    "Dossier refuse",
    "Dossier Annule",
    "RFE",
    "Escrow",
]

cols_display = [c for c in cols_display if c in df_filtre.columns]

st.dataframe(
    df_filtre[cols_display].sort_values("Date", ascending=False),
    use_container_width=True,
    height=450,
)
