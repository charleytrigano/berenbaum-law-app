import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database
from components.kpi_cards import kpi_card

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="🏠 Dashboard", page_icon="🏠", layout="wide")
render_sidebar()
st.title("🏠 Dashboard – Berenbaum Law App")

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
db = load_database()
clients = pd.DataFrame(db.get("clients", []))

if clients.empty:
    st.warning("Aucun dossier trouvé.")
    st.stop()

# ---------------------------------------------------------
# NORMALISATION
# ---------------------------------------------------------
for col in [
    "Montant honoraires (US $)",
    "Autres frais (US $)",
    "Acompte 1",
    "Acompte 2",
    "Acompte 3",
    "Acompte 4",
]:
    clients[col] = pd.to_numeric(clients.get(col, 0), errors="coerce").fillna(0)

clients["Total facturé"] = (
    clients["Montant honoraires (US $)"] + clients["Autres frais (US $)"]
)

clients["Total encaissé"] = (
    clients["Acompte 1"]
    + clients["Acompte 2"]
    + clients["Acompte 3"]
    + clients["Acompte 4"]
)

clients["Solde dû"] = clients["Total facturé"] - clients["Total encaissé"]

# Booléens
for col in [
    "Escrow",
    "Escrow_a_reclamer",
    "Escrow_reclame",
    "Dossier envoye",
    "Dossier accepte",
    "Dossier refuse",
    "Dossier Annule",
    "RFE",
]:
    clients[col] = clients.get(col, False).astype(bool)

# ---------------------------------------------------------
# KPI — UNE SEULE LIGNE
# ---------------------------------------------------------
st.subheader("📊 Indicateurs clés")

k1, k2, k3, k4, k5, k6, k7 = st.columns(7)

with k1:
    kpi_card(
        "Nombre de dossiers",
        len(clients),
        "📁",
        help_text="Nombre total de dossiers (principaux + sous-dossiers)"
    )

with k2:
    kpi_card(
        "Honoraires",
        f"${clients['Montant honoraires (US $)'].sum():,.0f}",
        "💼",
        help_text="Somme totale des honoraires facturés"
    )

with k3:
    kpi_card(
        "Autres frais",
        f"${clients['Autres frais (US $)'].sum():,.0f}",
        "🧾",
        help_text="Frais annexes facturés"
    )

with k4:
    kpi_card(
        "Total facturé",
        f"${clients['Total facturé'].sum():,.0f}",
        "💰",
        help_text="Honoraires + autres frais"
    )

with k5:
    kpi_card(
        "Total encaissé",
        f"${clients['Total encaissé'].sum():,.0f}",
        "🏦",
        help_text="Somme des acomptes encaissés"
    )

with k6:
    kpi_card(
        "Solde dû",
        f"${clients['Solde dû'].sum():,.0f}",
        "⚠️",
        help_text="Montant restant à encaisser"
    )

with k7:
    kpi_card(
        "Escrow",
        f"${clients.loc[clients['Escrow'], 'Acompte 1'].sum():,.0f}",
        "🔒",
        help_text="Montant total actuellement en escrow (Acompte 1 uniquement)"
    )

# ---------------------------------------------------------
# TABLEAU DOSSIERS
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📋 Liste des dossiers")

cols_display = [
    "Dossier N",
    "Nom",
    "Categories",
    "Sous-categories",
    "Visa",
    "Total facturé",
    "Total encaissé",
    "Solde dû",
    "Escrow",
    "Escrow_a_reclamer",
    "Escrow_reclame",
]

st.dataframe(
    clients[cols_display]
    .sort_values("Dossier N"),
    use_container_width=True,
    height=500
)