# 00_🏠_Dashboard.py
import streamlit as st
import pandas as pd
from datetime import datetime
from utils.filters import (
    filter_by_category,
    filter_by_period,
    build_period_options,
)
from components.kpi_cards import display_kpi_row
from components.modal_dossier import show_dossier_modal
from backend.dropbox_utils import load_database

st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")
st.title("🏠 Tableau de bord – Berenbaum Law")


# ---------------------------------------------------------
# 🔹 LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = pd.DataFrame(db.get("clients", []))

if clients.empty:
    st.warning("Aucun dossier trouvé.")
    st.stop()

# Normalisation
clients["Date"] = pd.to_datetime(clients["Date"], errors="coerce")

for col in ["Escrow", "Escrow_a_reclamer", "Escrow_reclame", "Dossier_envoye"]:
    if col not in clients.columns:
        clients[col] = False
    clients[col] = clients[col].apply(lambda x: True if str(x).lower() in ["true", "1"] else False)


# ---------------------------------------------------------
# 🔹 KPI ROW
# ---------------------------------------------------------
collected = {
    "total": len(clients),
    "envoyes": clients["Dossier_envoye"].sum(),
    "acceptes": clients["Dossier accepte"].sum() if "Dossier accepte" in clients else 0,
    "refuses": clients["Dossier refuse"].sum() if "Dossier refuse" in clients else 0,
    "escrow_en_cours": clients[clients["Escrow"] == True].shape[0],
    "escrow_a_reclamer": clients[clients["Escrow_a_reclamer"] == True].shape[0],
}

display_kpi_row(collected)


# ---------------------------------------------------------
# 🔹 FILTERS
# ---------------------------------------------------------
st.subheader("🎛️ Filtres")

categories = sorted(clients["Categories"].dropna().unique())
selected_cat = st.selectbox("Catégorie", ["Toutes"] + categories)

filtered = filter_by_category(clients, selected_cat)

# Sous-catégories
subcats = sorted(filtered["Sous-categories"].dropna().unique())
selected_sub = st.selectbox("Sous-catégorie", ["Toutes"] + subcats)

if selected_sub != "Toutes":
    filtered = filtered[filtered["Sous-categories"] == selected_sub]

# Visas
visas = sorted(filtered["Visa"].dropna().unique())
selected_visa = st.selectbox("Visa", ["Tous"] + visas)

if selected_visa != "Tous":
    filtered = filtered[filtered["Visa"] == selected_visa]

# ---------------------------------------------------------
# 🔹 PERIOD FILTER (Années / Date à date / Mois / Trimestre / Semestre)
# ---------------------------------------------------------
st.subheader("📅 Filtre temporel")

period_type = st.selectbox("Type de période", ["Aucune", "Mois", "Trimestre", "Semestre", "Date à date", "Comparaison multi-années"])

if period_type != "Aucune":
    filtered = filter_by_period(filtered, period_type)


# ---------------------------------------------------------
# 🔹 TABLE — DOSSIERS LIST
# ---------------------------------------------------------
st.subheader("📋 Liste des dossiers")

def badge(row):
    if row["Dossier_envoye"]:
        return "📤 Envoyé"
    if row["Escrow"]:
        return "💰 Escrow"
    return "🗂️ Ouvert"

filtered["Badge"] = filtered.apply(badge, axis=1)

display_df = filtered[[
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
]]

# Bouton modal
for i, row in filtered.iterrows():
    st.button(f"👁️ Voir dossier {row['Dossier N']}", key=f"btn_{row['Dossier N']}",
              on_click=lambda r=row: show_dossier_modal(r))

st.dataframe(display_df, use_container_width=True)
