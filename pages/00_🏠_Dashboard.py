import streamlit as st
import pandas as pd

from backend.dropbox_utils import load_database
from utils.sidebar import render_sidebar
from utils.dossier_utils import parse_dossier_number
from components.kpi_cards import kpi_card

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="🏠 Dashboard – Berenbaum Law App",
    page_icon="🏠",
    layout="wide"
)

render_sidebar()
st.title("🏠 Dashboard – Vue globale des dossiers")

# =========================================================
# CHARGEMENT BASE
# =========================================================
db = load_database()
clients_raw = db.get("clients", [])

if not clients_raw:
    st.warning("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients_raw)

# =========================================================
# NORMALISATION DOSSIER N (parent / index)
# =========================================================
df["Dossier Parent"], df["Dossier Index"] = zip(
    *df["Dossier N"].apply(parse_dossier_number)
)

df["Dossier Parent"] = df["Dossier Parent"].astype(int)
df["Dossier Index"] = df["Dossier Index"].astype(int)

# =========================================================
# NORMALISATION NUMÉRIQUE
# =========================================================
for col in [
    "Montant honoraires (US $)",
    "Autres frais (US $)",
    "Acompte 1",
    "Acompte 2",
    "Acompte 3",
    "Acompte 4",
]:
    df[col] = pd.to_numeric(df.get(col, 0), errors="coerce").fillna(0.0)

df["Total facturé"] = (
    df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
)

df["Total encaissé"] = (
    df["Acompte 1"] + df["Acompte 2"] + df["Acompte 3"] + df["Acompte 4"]
)

df["Solde dû"] = df["Total facturé"] - df["Total encaissé"]

# =========================================================
# KPI – EN LIGNE
# =========================================================
st.subheader("📊 Indicateurs clés")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    kpi_card(
        "Nombre de dossiers",
        len(df),
        "📁",
        help_text="Dossiers principaux + sous-dossiers"
    )

with col2:
    kpi_card(
        "Honoraires",
        f"${df['Montant honoraires (US $)'].sum():,.0f}",
        "💰",
        help_text="Total des honoraires"
    )

with col3:
    kpi_card(
        "Autres frais",
        f"${df['Autres frais (US $)'].sum():,.0f}",
        "🧾",
        help_text="Frais additionnels"
    )

with col4:
    kpi_card(
        "Total facturé",
        f"${df['Total facturé'].sum():,.0f}",
        "📄",
        help_text="Honoraires + frais"
    )

with col5:
    kpi_card(
        "Total encaissé",
        f"${df['Total encaissé'].sum():,.0f}",
        "💳",
        help_text="Somme des acomptes"
    )

with col6:
    kpi_card(
        "Solde dû",
        f"${df['Solde dû'].sum():,.0f}",
        "⚠️",
        help_text="Facturé – encaissé"
    )

# =========================================================
# FILTRES
# =========================================================
st.subheader("🎛️ Filtres")

f1, f2, f3, f4 = st.columns(4)

categories = ["Tous"] + sorted(df["Categories"].dropna().unique().tolist())
cat = f1.selectbox("Catégorie", categories)

if cat != "Tous":
    df = df[df["Categories"] == cat]

souscats = ["Tous"] + sorted(df["Sous-categories"].dropna().unique().tolist())
sous = f2.selectbox("Sous-catégorie", souscats)

if sous != "Tous":
    df = df[df["Sous-categories"] == sous]

visas = ["Tous"] + sorted(df["Visa"].dropna().unique().tolist())
visa = f3.selectbox("Visa", visas)

if visa != "Tous":
    df = df[df["Visa"] == visa]

statuts = [
    "Tous",
    "Envoyé",
    "Accepté",
    "Refusé",
    "Annulé",
    "RFE"
]
statut = f4.selectbox("Statut", statuts)

if statut != "Tous":
    mapping = {
        "Envoyé": "Dossier envoye",
        "Accepté": "Dossier accepte",
        "Refusé": "Dossier refuse",
        "Annulé": "Dossier Annule",
        "RFE": "RFE",
    }
    df = df[df[mapping[statut]] == True]

# =========================================================
# TABLEAU DOSSIERS (TRI GARANTI)
# =========================================================
st.subheader("📋 Liste des dossiers")

df_display = (
    df.sort_values(["Dossier Parent", "Dossier Index"])
    .reset_index(drop=True)
)

cols = [
    "Dossier N",
    "Nom",
    "Categories",
    "Sous-categories",
    "Visa",
    "Total facturé",
    "Total encaissé",
    "Solde dû",
    "Dossier envoye",
    "Dossier accepte",
    "Dossier refuse",
    "Dossier Annule",
]

st.dataframe(
    df_display[cols],
    use_container_width=True,
    height=520
)

st.markdown("—")
st.caption("Berenbaum Law App · Dashboard principal")