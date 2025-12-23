import streamlit as st
import pandas as pd
from datetime import datetime

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
# NORMALISATION COLONNES & TYPES
# ---------------------------------------------------------

# Harmonisation des alias de statuts éventuels
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
df.rename(
    columns={k: v for k, v in rename_map.items() if k in df.columns},
    inplace=True,
)

# Colonnes booléennes à garantir
bool_cols = [
    "Dossier envoye",
    "Dossier accepte",
    "Dossier refuse",
    "Dossier Annule",
    "RFE",
    "Escrow",
]
for col in bool_cols:
    if col not in df.columns:
        df[col] = False


def to_bool(x):
    if isinstance(x, bool):
        return x
    if x is None:
        return False
    s = str(x).strip().lower()
    return s in ["true", "1", "1.0", "yes", "oui", "y", "vrai"]


for col in bool_cols:
    df[col] = df[col].apply(to_bool)

# Dates
df["Date"] = pd.to_datetime(df.get("Date"), errors="coerce")
df["Année"] = df["Date"].dt.year
df["Mois"] = df["Date"].dt.to_period("M").astype(str)

# Numérique
for col in ["Montant honoraires (US $)", "Autres frais (US $)"]:
    df[col] = pd.to_numeric(df.get(col, 0), errors="coerce").fillna(0.0)

for i in range(1, 5):
    col_ac = f"Acompte {i}"
    if col_ac in df.columns:
        df[col_ac] = pd.to_numeric(df[col_ac], errors="coerce").fillna(0.0)
    else:
        df[col_ac] = 0.0

# ---------------------------------------------------------
# FILTRES MÉTIERS (Cat / Sous-cat / Visa / Statut)
# ---------------------------------------------------------
st.subheader("🎛️ Filtres")

col_f1, col_f2, col_f3, col_f4 = st.columns(4)

# Catégorie
categories = ["Tous"] + sorted(
    [c for c in df.get("Categories", "").dropna().unique().tolist() if c != ""]
)
filtre_cat = col_f1.selectbox("Catégorie", categories)

# Sous-catégorie (dépend de la catégorie si filtrée)
if filtre_cat != "Tous":
    souscats = ["Tous"] + sorted(
        df[df["Categories"] == filtre_cat]["Sous-categories"]
        .dropna()
        .unique()
        .tolist()
    )
else:
    souscats = ["Tous"] + sorted(
        [s for s in df.get("Sous-categories", "").dropna().unique().tolist() if s != ""]
    )
filtre_souscat = col_f2.selectbox("Sous-catégorie", souscats)

# Visa (dépend de la sous-catégorie si filtrée)
if filtre_souscat != "Tous":
    visas = ["Tous"] + sorted(
        df[df["Sous-categories"] == filtre_souscat]["Visa"]
        .dropna()
        .unique()
        .tolist()
    )
else:
    visas = ["Tous"] + sorted(
        [v for v in df.get("Visa", "").dropna().unique().tolist() if v != ""]
    )
filtre_visa = col_f3.selectbox("Visa", visas)

# Statut
statuts = ["Tous", "Envoyé", "Accepté", "Refusé", "Annulé", "RFE"]
filtre_statut = col_f4.selectbox("Statut du dossier", statuts)

# Application des filtres métiers
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
# FILTRES TEMPORELS / COMPARAISONS
# ---------------------------------------------------------
st.subheader("📆 Comparaisons temporelles")

col_t1, col_t2, col_t3 = st.columns(3)

periode_type = col_t1.selectbox(
    "Type de période",
    ["Aucune", "Mois", "Trimestre", "Semestre", "Année", "Date à date"],
)

df_time = df_filtre.copy()

if not df_time.empty and df_time["Date"].notna().any():
    min_date = df_time["Date"].min().date()
    max_date = df_time["Date"].max().date()
else:
    # Valeurs par défaut si aucune date exploitable
    today = datetime.today().date()
    min_date = today
    max_date = today

if periode_type in ["Mois", "Trimestre", "Semestre", "Année"]:
    # Comparaison par années : on filtre sur 2 à 5 années
    years = sorted(df_time["Année"].dropna().unique().tolist())
    if years:
        default_years = years[-2:] if len(years) >= 2 else years
    else:
        default_years = []

    selected_years = col_t2.multiselect(
        "Années à comparer (2 à 5)",
        years,
        default=default_years,
    )

    if selected_years:
        df_time = df_time[df_time["Année"].isin(selected_years)]

elif periode_type == "Date à date":
    start_date = col_t2.date_input("Du", value=min_date)
    end_date = col_t3.date_input("Au", value=max_date)

    if start_date > end_date:
        st.error("La date de début est après la date de fin.")
    else:
        df_time = df_time[
            (df_time["Date"].dt.date >= start_date)
            & (df_time["Date"].dt.date <= end_date)
        ]

# Si "Aucune" → on ne touche pas df_time (il reste = df_filtre)

# ---------------------------------------------------------
# KPI (sur df_time = filtres + période)
# ---------------------------------------------------------
st.subheader("📈 Indicateurs clés")

k1, k2, k3, k4, k5, k6 = st.columns(6)

with k1:
    kpi_card("Dossiers filtrés", int(len(df_time)), "📁")

with k2:
    kpi_card(
        "CA honoraires (US $)",
        float(df_time["Montant honoraires (US $)"].sum()),
        "💰",
    )

with k3:
    kpi_card(
        "Autres frais (US $)",
        float(df_time["Autres frais (US $)"].sum()),
        "💵",
    )

with k4:
    kpi_card("Dossiers envoyés", int(df_time["Dossier envoye"].sum()), "📤")

with k5:
    kpi_card("Dossiers acceptés", int(df_time["Dossier accepte"].sum()), "✅")

with k6:
    kpi_card("Dossiers refusés", int(df_time["Dossier refuse"].sum()), "❌")

# ---------------------------------------------------------
# GRAPHIQUES (sur df_time)
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
    st.plotly_chart(monthly_hist(df_time), use_container_width=True)

with tab2:
    st.plotly_chart(multi_year_line(df_time), use_container_width=True)

with tab3:
    st.plotly_chart(category_donut(df_time), use_container_width=True)

with tab4:
    st.plotly_chart(heatmap_month(df_time), use_container_width=True)

with tab5:
    st.plotly_chart(category_bars(df_time), use_container_width=True)

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

cols_display = [c for c in cols_display if c in df_time.columns]

st.dataframe(
    df_time[cols_display].sort_values("Date", ascending=False),
    use_container_width=True,
    height=450,
)
