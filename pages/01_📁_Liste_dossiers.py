import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database
from utils.dossier_hierarchy import add_hierarchy_columns

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="📁 Liste des dossiers", page_icon="📁", layout="wide")
render_sidebar()
st.title("📁 Liste complète des dossiers")

# ---------------------------------------------------------
# LOAD
# ---------------------------------------------------------
db = load_database()
df = pd.DataFrame(db.get("clients", []))

if df.empty:
    st.stop()

df["Dossier N"] = df["Dossier N"].astype(str)
df = add_hierarchy_columns(df)

# ---------------------------------------------------------
# FILTRES SIDEBAR
# ---------------------------------------------------------
st.subheader("🎛️ Filtres")

c1, c2, c3, c4 = st.columns(4)

annees = sorted(pd.to_datetime(df["Date"], errors="coerce").dt.year.dropna().unique())
annee = c1.multiselect("Année", annees, default=annees)

cat = c2.selectbox("Catégorie", ["Tous"] + sorted(df["Categories"].dropna().unique()))
sous = c3.selectbox("Sous-catégorie", ["Tous"] + sorted(df["Sous-categories"].dropna().unique()))
visa = c4.selectbox("Visa", ["Tous"] + sorted(df["Visa"].dropna().unique()))

if annee:
    df = df[pd.to_datetime(df["Date"], errors="coerce").dt.year.isin(annee)]
if cat != "Tous":
    df = df[df["Categories"] == cat]
if sous != "Tous":
    df = df[df["Sous-categories"] == sous]
if visa != "Tous":
    df = df[df["Visa"] == visa]

# ---------------------------------------------------------
# TABLEAU
# ---------------------------------------------------------
st.subheader("📋 Dossiers")

cols = [
    "Dossier N", "Nom", "Categories", "Sous-categories", "Visa",
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4",
    "Escrow", "Escrow_a_reclamer", "Escrow_reclame",
]

st.dataframe(
    df.sort_values(["Dossier Parent", "Dossier Index"])[cols],
    use_container_width=True,
    height=600
)