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
st.title("📊 Analyses statistiques – Tableau de bord avancé")

# ---------------------------------------------------------
# CHARGEMENT BASE
# ---------------------------------------------------------
db = load_database()
clients_raw = db.get("clients", [])

if not clients_raw:
    st.error("Aucun dossier trouvé dans la base.")
    st.stop()

df = pd.DataFrame(clients_raw)

# ---------------------------------------------------------
# NORMALISATION MINIMALE
# ---------------------------------------------------------
def normalize_bool(x):
    if isinstance(x, bool):
        return x
    if x is None:
        return False
    s = str(x).strip().lower()
    return s in ["true", "1", "1.0", "yes", "oui", "y", "vrai"]


# Dates
df["Date"] = pd.to_datetime(df.get("Date"), errors="coerce")
df["Année"] = df["Date"].dt.year
df["Mois"] = df["Date"].dt.to_period("M").astype(str)

# Numériques
for col in [
    "Montant honoraires (US $)",
    "Autres frais (US $)",
    "Acompte 1",
    "Acompte 2",
    "Acompte 3",
    "Acompte 4",
]:
    if col not in df.columns:
        df[col] = 0.0
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

# Statuts (adapter aux noms du JSON)
for col in [
    "Dossier_envoye",
    "Dossier accepte",
    "Dossier refuse",
    "Dossier Annule",
    "RFE",
    "Escrow",
]:
    if col not in df.columns:
        df[col] = False
    df[col] = df[col].apply(normalize_bool)

# Colonnes texte de base
for col in ["Categories", "Sous-categories", "Visa"]:
    if col not in df.columns:
        df[col] = ""

# ---------------------------------------------------------
# CALCULS FINANCIERS (FACTURE / ENCAISSÉ / SOLDE)
# ---------------------------------------------------------
df["Total facturé"] = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
df["Total encaissé"] = (
    df["Acompte 1"] + df["Acompte 2"] + df["Acompte 3"] + df["Acompte 4"]
)
df["Solde"] = df["Total facturé"] - df["Total encaissé"]

# ---------------------------------------------------------
# 🎛️ FILTRES
# ---------------------------------------------------------
st.subheader("🎛️ Filtres")

fil1, fil2, fil3, fil4, fil5 = st.columns(5)

# Année
annees = sorted([a for a in df["Année"].dropna().unique().tolist()])
annee_sel = fil1.multiselect(
    "Année",
    options=annees,
    default=annees if annees else [],
)

# Catégorie
cat_options = sorted([c for c in df["Categories"].dropna().unique().tolist() if c != ""])
cat = fil2.selectbox("Catégorie", ["Toutes"] + cat_options)

# Sous-catégorie (dépend de la catégorie)
if cat != "Toutes":
    sous_options = (
        df[df["Categories"] == cat]["Sous-categories"].dropna().unique().tolist()
    )
else:
    sous_options = df["Sous-categories"].dropna().unique().tolist()

sous = fil3.selectbox("Sous-catégorie", ["Toutes"] + sorted(sous_options))

# Visa (dépend de la sous-catégorie si filtrée)
if sous != "Toutes":
    visa_options = (
        df[df["Sous-categories"] == sous]["Visa"].dropna().unique().tolist()
    )
else:
    visa_options = df["Visa"].dropna().unique().tolist()

visa_sel = fil4.selectbox("Visa", ["Tous"] + sorted(visa_options))

# Statut
statut_options = ["Tous", "Envoyé", "Accepté", "Refusé", "Annulé", "RFE"]
statut_sel = fil5.selectbox("Statut dossier", statut_options)

# Filtre “dossiers non soldés”
only_non_soldes = st.checkbox(
    "Afficher uniquement les dossiers non soldés (solde > 0)", value=False
)

# ---------------------------------------------------------
# APPLICATION DES FILTRES
# ---------------------------------------------------------
df_filt = df.copy()

# Année
if annee_sel:
    df_filt = df_filt[df_filt["Année"].isin(annee_sel)]

# Catégorie
if cat != "Toutes":
    df_filt = df_filt[df_filt["Categories"] == cat]

# Sous-catégorie
if sous != "Toutes":
    df_filt = df_filt[df_filt["Sous-categories"] == sous]

# Visa
if visa_sel != "Tous":
    df_filt = df_filt[df_filt["Visa"] == visa_sel]

# Statut logique
if statut_sel != "Tous":
    mapping = {
        "Envoyé": "Dossier_envoye",
        "Accepté": "Dossier accepte",
        "Refusé": "Dossier refuse",
        "Annulé": "Dossier Annule",
        "RFE": "RFE",
    }
    col_statut = mapping.get(statut_sel)
    if col_statut:
        df_filt = df_filt[df_filt[col_statut] == True]

# Dossiers non soldés
if only_non_soldes:
    df_filt = df_filt[df_filt["Solde"] > 0.01]

# Sécurité si plus rien
if df_filt.empty:
    st.warning("Aucun dossier ne correspond aux filtres sélectionnés.")
    st.stop()

# ---------------------------------------------------------
# 📆 COMPARAISONS TEMPORELLES (GRAPHIQUES)
# ---------------------------------------------------------
st.subheader("📆 Comparaisons temporelles")

colT1, colT2 = st.columns(2)

periode_type = colT1.selectbox(
    "Type de période (pour lecture des graphiques)",
    ["Mois", "Trimestre", "Semestre", "Année"],
)

years_available = sorted(df_filt["Année"].dropna().unique().tolist())
years_selected = colT2.multiselect(
    "Années à comparer",
    options=years_available,
    default=years_available[-2:] if len(years_available) >= 2 else years_available,
)

# Pour les courbes multi-années, on restreint aux années sélectionnées
if years_selected:
    df_for_lines = df_filt[df_filt["Année"].isin(years_selected)]
else:
    df_for_lines = df_filt

# ---------------------------------------------------------
# 🔢 KPI
# ---------------------------------------------------------
st.subheader("📈 Indicateurs clés")

kcol1, kcol2, kcol3, kcol4, kcol5, kcol6 = st.columns(6)

with kcol1:
    kpi_card("Dossiers filtrés", len(df_filt), "📁")

with kcol2:
    kpi_card(
        "CA honoraires (filtré)",
        f"{int(df_filt['Montant honoraires (US $)'].sum()):,}".replace(",", " "),
        "💰",
    )

with kcol3:
    kpi_card("Dossiers envoyés", int(df_filt["Dossier_envoye"].sum()), "📤")

with kcol4:
    kpi_card("Dossiers acceptés", int(df_filt["Dossier accepte"].sum()), "✅")

with kcol5:
    kpi_card("Dossiers refusés", int(df_filt["Dossier refuse"].sum()), "❌")

with kcol6:
    kpi_card("Dossiers en Escrow", int(df_filt["Escrow"].sum()), "💼")

# ---------------------------------------------------------
# 📊 GRAPHIQUES
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
    st.plotly_chart(monthly_hist(df_filt), use_container_width=True)

with tab2:
    st.plotly_chart(multi_year_line(df_for_lines), use_container_width=True)

with tab3:
    st.plotly_chart(category_donut(df_filt), use_container_width=True)

with tab4:
    st.plotly_chart(heatmap_month(df_filt), use_container_width=True)

with tab5:
    st.plotly_chart(category_bars(df_filt), use_container_width=True)

# ---------------------------------------------------------
# 📋 TABLEAU DÉTAILLÉ
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
    "Acompte 1",
    "Acompte 2",
    "Acompte 3",
    "Acompte 4",
    "Total facturé",
    "Total encaissé",
    "Solde",
    "Dossier_envoye",
    "Dossier accepte",
    "Dossier refuse",
    "Dossier Annule",
    "Escrow",
]

cols_present = [c for c in cols_display if c in df_filt.columns]

df_show = df_filt[cols_present].copy()

st.dataframe(df_show, use_container_width=True, height=450)
