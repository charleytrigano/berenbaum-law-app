pages/00_🏠_Dashboard.py
import streamlit as st
import pandas as pd
from datetime import datetime
from utils.filters import (
    filter_by_category,
    filter_by_period,
)
from components.kpi_cards import display_kpi_row
from components.modal_dossier import show_dossier_modal
from backend.dropbox_utils import load_database


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")
st.title("🏠 Tableau de bord – Berenbaum Law")


# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = pd.DataFrame(db.get("clients", []))

if clients.empty:
    st.warning("Aucun dossier trouvé.")
    st.stop()

# Normalisation dates
clients["Date"] = pd.to_datetime(clients["Date"], errors="coerce")

# Normalisation booleans
def norm_bool(x):
    return True if str(x).lower() in ["true", "1", "yes"] else False

for col in ["Escrow", "Escrow_a_reclamer", "Escrow_reclame",
            "Dossier_envoye", "Dossier accepte", "Dossier refuse",
            "Dossier Annule", "RFE"]:
    if col not in clients.columns:
        clients[col] = False
    clients[col] = clients[col].apply(norm_bool)


# ---------------------------------------------------------
# KPI ROW
# ---------------------------------------------------------
kpi_data = {
    "total": len(clients),
    "envoyes": clients["Dossier_envoye"].sum(),
    "acceptes": clients["Dossier accepte"].sum(),
    "refuses": clients["Dossier refuse"].sum(),
    "escrow_en_cours": clients[clients["Escrow"] == True].shape[0],
    "escrow_a_reclamer": clients[clients["Escrow_a_reclamer"] == True].shape[0],
}

display_kpi_row(kpi_data)


# ---------------------------------------------------------
# FILTER SECTION
# ---------------------------------------------------------
st.subheader("🎛️ Filtres")

# --- Catégorie ---
categories = sorted([c for c in clients["Categories"].dropna().unique() if c])
selected_cat = st.selectbox("Catégorie", ["Toutes"] + categories)

filtered = filter_by_category(clients, selected_cat)

# --- Sous-catégorie ---
subcats = sorted([c for c in filtered["Sous-categories"].dropna().unique() if c])
selected_sub = st.selectbox("Sous-catégorie", ["Toutes"] + subcats)

if selected_sub != "Toutes":
    filtered = filtered[filtered["Sous-categories"] == selected_sub]

# --- Visa ---
visas = sorted([v for v in filtered["Visa"].dropna().unique() if v])
selected_visa = st.selectbox("Visa", ["Tous"] + visas)

if selected_visa != "Tous":
    filtered = filtered[filtered["Visa"] == selected_visa]


# ---------------------------------------------------------
# PERIOD FILTERS
# ---------------------------------------------------------
st.subheader("📅 Filtre temporel")

period_type = st.selectbox(
    "Type de période",
    ["Aucune", "Mois", "Trimestre", "Semestre", "Date à date", "Comparaison multi-années"]
)

if period_type != "Aucune":
    filtered = filter_by_period(filtered, period_type)


# ---------------------------------------------------------
# BUILD TABLE
# ---------------------------------------------------------
st.subheader("📋 Liste des dossiers")

def build_badge(row):
    if row["Escrow"]:
        return "💰 Escrow"
    if row["Dossier_envoye"]:
        return "📤 Envoyé"
    if row["Dossier accepte"]:
        return "🟢 Accepté"
    if row["Dossier refuse"]:
        return "🔴 Refusé"
    return "📁 Ouvert"


filtered["Badge"] = filtered.apply(build_badge, axis=1)


# Table affichée
display_columns = [
    "Dossier N",
    "Nom",
    "Categories",
    "Sous-categories",
    "Visa",
    "Date",
    "Badge",
    "Montant honoraires (US $)",
    "Acompte 1",
    "Acompte 2",
    "Acompte 3",
    "Acompte 4",
]

st.dataframe(filtered[display_columns], use_container_width=True)


# ---------------------------------------------------------
# MODAL BUTTONS — FIXED (no duplicate keys)
# ---------------------------------------------------------
st.subheader("👁️ Ouvrir un dossier")

for i, row in filtered.iterrows():
    st.button(
        f"Voir dossier {row['Dossier N']}",
        key=f"view_btn_{i}",              # UNIQUE KEY FIX
        on_click=lambda r=row: show_dossier_modal(r)
    )
