# pages/00_Dashboard.py
import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Dashboard",
    layout="wide"
)

render_sidebar()
st.title("Dashboard - Vue globale")

# -------------------------------------------------
# LOAD DATABASE
# -------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier disponible.")
    st.stop()

df = pd.DataFrame(clients)

# -------------------------------------------------
# NORMALISATION SAFE
# -------------------------------------------------
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
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

df["Dossier N"] = df["Dossier N"].astype(str)

# -------------------------------------------------
# KPI CALCULS
# -------------------------------------------------
total_dossiers = len(df)
total_honoraires = df["Montant honoraires (US $)"].sum()
total_frais = df["Autres frais (US $)"].sum()
total_facture = total_honoraires + total_frais

total_encaisse = (
    df["Acompte 1"].sum()
    + df["Acompte 2"].sum()
    + df["Acompte 3"].sum()
    + df["Acompte 4"].sum()
)

solde_du = total_facture - total_encaisse

# -------------------------------------------------
# KPI DISPLAY (STREAMLIT NATIF)
# -------------------------------------------------
st.subheader("Indicateurs clés")

c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("Dossiers", total_dossiers)
c2.metric("Honoraires", f"${total_honoraires:,.2f}")
c3.metric("Frais", f"${total_frais:,.2f}")
c4.metric("Total facturé", f"${total_facture:,.2f}")
c5.metric("Total encaissé", f"${total_encaisse:,.2f}")
c6.metric("Solde dû", f"${solde_du:,.2f}")

# -------------------------------------------------
# TABLE
# -------------------------------------------------
st.markdown("---")
st.subheader("Liste des dossiers")

st.dataframe(
    df.sort_values("Dossier N"),
    use_container_width=True,
    height=500
)