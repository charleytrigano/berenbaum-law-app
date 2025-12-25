# pages/00_🏠_Dashboard.py
import streamlit as st
import pandas as pd
from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database
from components.kpi_cards import kpi_card

# ---------------------------------------------------------
# ⚙️ CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(page_title="🏠 Dashboard", page_icon="🏠", layout="wide")
render_sidebar()
st.title("🏠 Dashboard – Vue globale")

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
# 🧹 Nettoyage et normalisation
# ---------------------------------------------------------
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Année"] = df["Date"].dt.year
df["Mois"] = df["Date"].dt.to_period("M").astype(str)
df["Dossier N"] = df["Dossier N"].astype(str)

# Pour éviter les NaN
for col in [
    "Categories", "Sous-categories", "Visa",
    "Dossier envoye", "Dossier accepte", "Dossier refuse",
    "Escrow", "Escrow_a_reclamer", "Escrow_reclame"
]:
    if col not in df.columns:
        df[col] = ""

# ---------------------------------------------------------
# 🎛️ Filtres globaux
# ---------------------------------------------------------
st.subheader("🎛️ Filtres de recherche")

col1, col2, col3, col4 = st.columns(4)

categories = ["Tous"] + sorted(df["Categories"].dropna().unique())
cat = col1.selectbox("Catégorie", categories)

if cat != "Tous":
    souscats = ["Tous"] + sorted(df[df["Categories"] == cat]["Sous-categories"].dropna().unique())
else:
    souscats = ["Tous"] + sorted(df["Sous-categories"].dropna().unique())

sous = col2.selectbox("Sous-catégorie", souscats)

if sous != "Tous":
    visas = ["Tous"] + sorted(df[df["Sous-categories"] == sous]["Visa"].dropna().unique())
else:
    visas = ["Tous"] + sorted(df["Visa"].dropna().unique())

visa = col3.selectbox("Visa", visas)

statuts = ["Tous", "Envoyé", "Accepté", "Refusé", "Annulé", "RFE"]
statut = col4.selectbox("Statut du dossier", statuts)

# Application filtres
filtered = df.copy()
if cat != "Tous":
    filtered = filtered[filtered["Categories"] == cat]
if sous != "Tous":
    filtered = filtered[filtered["Sous-categories"] == sous]
if visa != "Tous":
    filtered = filtered[filtered["Visa"] == visa]
if statut != "Tous":
    mapping = {
        "Envoyé": "Dossier envoye",
        "Accepté": "Dossier accepte",
        "Refusé": "Dossier refuse",
        "Annulé": "Dossier Annule",
        "RFE": "RFE",
    }
    col = mapping[statut]
    filtered = filtered[filtered[col] == True]

# ---------------------------------------------------------
# 📊 KPI principaux
# ---------------------------------------------------------
st.subheader("📈 Indicateurs clés")

kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)

total_dossiers = len(filtered)
total_honoraires = filtered["Montant honoraires (US $)"].sum()
total_frais = filtered["Autres frais (US $)"].sum()
total_facture = total_honoraires + total_frais
total_encaisse = (
    filtered["Acompte 1"].sum()
    + filtered["Acompte 2"].sum()
    + filtered["Acompte 3"].sum()
    + filtered["Acompte 4"].sum()
)
solde_du = total_facture - total_encaisse
montant_escrow = filtered.loc[filtered["Escrow"] == True, "Acompte 1"].sum()

with kpi_col1:
    kpi_card("Nombre de dossiers", total_dossiers, "📁")
with kpi_col2:
    kpi_card("Honoraires", f"${total_honoraires:,.2f}", "💼")
with kpi_col3:
    kpi_card("Autres frais", f"${total_frais:,.2f}", "💸")
with kpi_col4:
    kpi_card("Total facturé", f"${total_facture:,.2f}", "🧾")
with kpi_col5:
    kpi_card("Total encaissé", f"${total_encaisse:,.2f}", "💰")
with kpi_col6:
    kpi_card("Solde dû", f"${solde_du:,.2f}", "⚖️")

st.markdown("---")

# ---------------------------------------------------------
# 💰 KPI Escrow global
# ---------------------------------------------------------
st.subheader("💰 Escrow global")

colE1, colE2, colE3 = st.columns(3)
escrow_actifs = filtered[filtered["Escrow"] == True]
escrow_a_reclamer = filtered[filtered["Escrow_a_reclamer"] == True]
escrow_reclames = filtered[filtered["Escrow_reclame"] == True]

colE1.metric("Escrows actifs", len(escrow_actifs), delta=f"${escrow_actifs['Acompte 1'].sum():,.2f}")
colE2.metric("Escrows à réclamer", len(escrow_a_reclamer), delta=f"${escrow_a_reclamer['Acompte 1'].sum():,.2f}")
colE3.metric("Escrows réclamés", len(escrow_reclames), delta=f"${escrow_reclames['Acompte 1'].sum():,.2f}")

st.markdown("---")

# ---------------------------------------------------------
# 📋 TABLEAU DES DOSSIERS
# ---------------------------------------------------------
st.subheader("📋 Dossiers filtrés")

cols_display = [
    "Dossier N", "Nom", "Date", "Categories", "Sous-categories", "Visa",
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4",
    "Escrow", "Dossier envoye", "Dossier accepte", "Dossier refuse",
]

st.dataframe(
    filtered[cols_display].sort_values("Dossier N"),
    use_container_width=True,
    height=500
)

st.markdown("### 🌟 Tableau de bord – Berenbaum Law App")