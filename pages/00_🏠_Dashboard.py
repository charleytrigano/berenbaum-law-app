import os
import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import
load_database, save_database

st.write("ROOT FILES:", os.listdir("."))
st.write("UTILS DIR:", os.listdir("utils") if os.path.isdir("utils") else "NO utils/ folder")

from utils.sidebar import render_sidebar

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="🏠 Dashboard", page_icon="🏠", layout="wide")
render_sidebar()
st.title("🏠 Dashboard – Vue globale")

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
db = load_database()
df = pd.DataFrame(db.get("clients", []))

if df.empty:
    st.warning("Aucun dossier trouvé.")
    st.stop()

# ---------------------------------------------------------
# NORMALISATION
# ---------------------------------------------------------
df["Dossier N"] = df["Dossier N"].astype(str)
df = add_hierarchy_columns(df)

for col in [
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4"
]:
    df[col] = pd.to_numeric(df.get(col, 0), errors="coerce").fillna(0)

# ---------------------------------------------------------
# KPI
# ---------------------------------------------------------
total_dossiers = len(df)
total_honoraires = df["Montant honoraires (US $)"].sum()
total_frais = df["Autres frais (US $)"].sum()
total_facture = total_honoraires + total_frais
total_encaisse = (
    df["Acompte 1"].sum() +
    df["Acompte 2"].sum() +
    df["Acompte 3"].sum() +
    df["Acompte 4"].sum()
)
solde_du = total_facture - total_encaisse
escrow_total = df[df["Escrow"] == True]["Acompte 1"].sum()

st.subheader("📊 Indicateurs clés")

c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    kpi_card("Nombre de dossiers", total_dossiers, "📁")
with c2:
    kpi_card("Honoraires", f"${total_honoraires:,.0f}", "💼")
with c3:
    kpi_card("Autres frais", f"${total_frais:,.0f}", "🧾")
with c4:
    kpi_card("Total facturé", f"${total_facture:,.0f}", "💰")
with c5:
    kpi_card("Total encaissé", f"${total_encaisse:,.0f}", "🏦")
with c6:
    kpi_card("Montant en Escrow", f"${escrow_total:,.0f}", "🔒")

# ---------------------------------------------------------
# TABLEAU SYNTHÈSE
# ---------------------------------------------------------
st.subheader("📋 Liste des dossiers")

cols = [
    "Dossier N", "Nom", "Visa",
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4",
    "Escrow", "Escrow_a_reclamer", "Escrow_reclame"
]

st.dataframe(
    df.sort_values(["Dossier Parent", "Dossier Index"])[cols],
    use_container_width=True,
    height=450
)
