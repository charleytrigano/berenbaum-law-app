import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database

# =========================================================
# CONFIG PAGE
# =========================================================
st.set_page_config(
    page_title="🏠 Dashboard – Berenbaum Law App",
    page_icon="🏠",
    layout="wide"
)

render_sidebar()
st.title("🏠 Tableau de bord – Berenbaum Law App")

# =========================================================
# LOAD DATABASE
# =========================================================
db = load_database()
clients = pd.DataFrame(db.get("clients", []))

if clients.empty:
    st.warning("Aucun dossier trouvé.")
    st.stop()

# =========================================================
# NORMALISATION DOSSIER N (support 12937 / 12937-1 / 12937-2)
# =========================================================
clients["Dossier N"] = clients["Dossier N"].astype(str)
clients["Dossier Parent"] = clients["Dossier N"].str.split("-").str[0]

# =========================================================
# NORMALISATION NUMÉRIQUE
# =========================================================
num_cols = [
    "Montant honoraires (US $)",
    "Autres frais (US $)",
    "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4"
]

for col in num_cols:
    if col not in clients.columns:
        clients[col] = 0.0
    clients[col] = pd.to_numeric(clients[col], errors="coerce").fillna(0.0)

# =========================================================
# NORMALISATION STATUTS
# =========================================================
bool_cols = [
    "Dossier envoye",
    "Dossier accepte",
    "Dossier refuse",
    "Dossier Annule",
    "RFE",
    "Escrow",
    "Escrow_a_reclamer",
    "Escrow_reclame",
]

for col in bool_cols:
    if col not in clients.columns:
        clients[col] = False
    clients[col] = clients[col].astype(bool)

# =========================================================
# FILTRES
# =========================================================
st.subheader("🎛️ Filtres")

colF1, colF2, colF3, colF4 = st.columns(4)

clients["Date"] = pd.to_datetime(clients["Date"], errors="coerce")

annees = sorted(clients["Date"].dropna().dt.year.unique().tolist())
annee = colF1.selectbox("Année", ["Toutes"] + annees)

categories = ["Toutes"] + sorted(clients["Categories"].dropna().unique().tolist())
categorie = colF2.selectbox("Catégorie", categories)

if categorie != "Toutes":
    souscats = ["Toutes"] + sorted(
        clients[clients["Categories"] == categorie]["Sous-categories"]
        .dropna().unique().tolist()
    )
else:
    souscats = ["Toutes"] + sorted(
        clients["Sous-categories"].dropna().unique().tolist()
    )

souscat = colF3.selectbox("Sous-catégorie", souscats)

visas = ["Tous"] + sorted(clients["Visa"].dropna().unique().tolist())
visa = colF4.selectbox("Visa", visas)

# =========================================================
# APPLICATION DES FILTRES
# =========================================================
df = clients.copy()

if annee != "Toutes":
    df = df[df["Date"].dt.year == annee]

if categorie != "Toutes":
    df = df[df["Categories"] == categorie]

if souscat != "Toutes":
    df = df[df["Sous-categories"] == souscat]

if visa != "Tous":
    df = df[df["Visa"] == visa]

# =========================================================
# KPI FINANCIERS CERTIFIÉS
# =========================================================
st.subheader("📊 Indicateurs clés")

total_dossiers = len(df)

total_honoraires = df["Montant honoraires (US $)"].sum()
total_frais = df["Autres frais (US $)"].sum()
total_facture = total_honoraires + total_frais

total_encaisse = (
    df["Acompte 1"] +
    df["Acompte 2"] +
    df["Acompte 3"] +
    df["Acompte 4"]
).sum()

solde_du = total_facture - total_encaisse

colK1, colK2, colK3, colK4, colK5, colK6 = st.columns(6)

colK1.metric("📁 Dossiers", total_dossiers)
colK2.metric("💼 Honoraires", f"${total_honoraires:,.0f}")
colK3.metric("💸 Autres frais", f"${total_frais:,.0f}")
colK4.metric("📄 Total facturé", f"${total_facture:,.0f}")
colK5.metric("💰 Encaissé", f"${total_encaisse:,.0f}")
colK6.metric("⚠️ Solde dû", f"${solde_du:,.0f}")

# =========================================================
# TABLEAU DES DOSSIERS
# =========================================================
st.subheader("📋 Liste des dossiers")

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
    "Dossier envoye",
    "Dossier accepte",
    "Dossier refuse",
    "Dossier Annule",
    "Escrow",
    "Escrow_a_reclamer",
    "Escrow_reclame",
]

cols_display = [c for c in cols_display if c in df.columns]

st.dataframe(
    df[cols_display].sort_values("Dossier Parent"),
    use_container_width=True,
    height=520
)
