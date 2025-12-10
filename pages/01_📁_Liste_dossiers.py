import streamlit as st
from utils.sidebar import render_sidebar
render_sidebar()
import pandas as pd
from backend.dropbox_utils import load_database




st.set_page_config(page_title="Liste des dossiers", page_icon="📁", layout="wide")
st.title("📁 Liste des dossiers")

# ---------------------------------------------------------
# 🔹 Chargement base
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)

# ---------------------------------------------------------
# 🔹 Normalisation colonnes manquantes
# ---------------------------------------------------------
REQUIRED_BOOL_COLS = [
    "Dossier envoye",
    "Dossier accepte",
    "Dossier refuse",
    "Dossier Annule",
    "Escrow",
    "Escrow_a_reclamer",
    "Escrow_reclame",
]

for col in REQUIRED_BOOL_COLS:
    if col not in df.columns:
        df[col] = False


def normalize_bool(x):
    if isinstance(x, bool):
        return x
    if str(x).lower() in ["true", "1", "1.0", "yes", "oui"]:
        return True
    return False


for col in REQUIRED_BOOL_COLS:
    df[col] = df[col].apply(normalize_bool)

# ---------------------------------------------------------
# 🔹 Colonnes dates
# ---------------------------------------------------------
DATE_COLS = ["Date", "Date envoi", "Date acceptation", "Date refus"]

for col in DATE_COLS:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

# ---------------------------------------------------------
# 🔹 Badges graphiques
# ---------------------------------------------------------
def badge(row):

    if row.get("Dossier Annule", False):
        return "❌ Annulé"
    if row.get("Dossier refuse", False):
        return "⛔ Refusé"
    if row.get("Dossier accepte", False):
        return "✅ Accepté"
    if row.get("Dossier envoye", False):
        return "📤 Envoyé"
    if row.get("Escrow", False):
        return "💰 Escrow"

    return "📝 En cours"


df["Statut"] = df.apply(badge, axis=1)

# ---------------------------------------------------------
# 🔎 FILTRES
# ---------------------------------------------------------
st.sidebar.header("🔍 Filtres")

# Année
years = sorted(df["Date"].dropna().dt.year.unique())
year_filter = st.sidebar.multiselect("Filtrer par année", years)

# Visa
visa_filter = st.sidebar.multiselect(
    "Filtrer par visa", sorted(df["Visa"].dropna().unique())
)

# Catégories
cat_filter = st.sidebar.multiselect(
    "Filtrer par catégorie", sorted(df["Categories"].dropna().unique())
)

# Statut
status_filter = st.sidebar.multiselect(
    "Filtrer par statut", ["📝 En cours", "📤 Envoyé", "✅ Accepté", "⛔ Refusé", "❌ Annulé", "💰 Escrow"]
)

# Escrow
escrow_filter = st.sidebar.selectbox(
    "Filtrer Escrow", ["Tous", "En cours", "À réclamer", "Réclamé"]
)

# Appliquer filtres
filtered = df.copy()

if year_filter:
    filtered = filtered[filtered["Date"].dt.year.isin(year_filter)]

if visa_filter:
    filtered = filtered[filtered["Visa"].isin(visa_filter)]

if cat_filter:
    filtered = filtered[filtered["Categories"].isin(cat_filter)]

if status_filter:
    filtered = filtered[filtered["Statut"].isin(status_filter)]

if escrow_filter == "En cours":
    filtered = filtered[filtered["Escrow"] == True]
elif escrow_filter == "À réclamer":
    filtered = filtered[filtered["Escrow_a_reclamer"] == True]
elif escrow_filter == "Réclamé":
    filtered = filtered[filtered["Escrow_reclame"] == True]

# ---------------------------------------------------------
# 📊 KPIs
# ---------------------------------------------------------
st.subheader("📊 Indicateurs clés")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total dossiers", len(df))
col2.metric("Envoyés", df["Dossier envoye"].sum())
col3.metric("Acceptés", df["Dossier accepte"].sum())
col4.metric("Refusés", df["Dossier refuse"].sum())

col5, col6, col7 = st.columns(3)

col5.metric("Annulés", df["Dossier Annule"].sum())
col6.metric("Escrow en cours", df["Escrow"].sum())
col7.metric("Escrow à réclamer", df["Escrow_a_reclamer"].sum())

# ---------------------------------------------------------
# 🔹 TABLEAU FINAL
# ---------------------------------------------------------
st.subheader("📄 Liste des dossiers")

colonnes_affichage = [
    "Dossier N",
    "Nom",
    "Date",
    "Categories",
    "Visa",
    "Statut",
]

st.dataframe(filtered[colonnes_affichage], use_container_width=True)
