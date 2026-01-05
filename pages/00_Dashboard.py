import streamlit as st
import pandas as pd
from datetime import datetime

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(page_title="🏠 Dashboard", page_icon="🏠", layout="wide")
render_sidebar()
st.title("🏠 Dashboard — Vue globale")

# =====================================================
# LOAD DATABASE
# =====================================================
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier disponible.")
    st.stop()

df = pd.DataFrame(clients).copy()
df["Dossier N"] = df["Dossier N"].astype(str)

# =====================================================
# OUTILS
# =====================================================
def to_float(v):
    try:
        return float(v or 0)
    except Exception:
        return 0.0

def total_acomptes(row):
    return sum(to_float(row.get(f"Acompte {i}", 0)) for i in range(1, 5))

# =====================================================
# KPI FINANCIERS GLOBAUX
# =====================================================
honoraires = df["Montant honoraires (US $)"].apply(to_float).sum()
frais = df["Autres frais (US $)"].apply(to_float).sum()
total_facture = honoraires + frais

total_encaisse = 0.0
for i in range(1, 5):
    col = f"Acompte {i}"
    if col in df.columns:
        total_encaisse += df[col].apply(to_float).sum()

solde_du = total_facture - total_encaisse

# =====================================================
# KPI ESCROW — LOGIQUE SYNCHRONISÉE
# =====================================================
escrow_actif_total = 0.0
escrow_a_reclamer_total = 0.0

for _, r in df.iterrows():
    acomptes = total_acomptes(r)

    if r.get("Escrow_reclame"):
        continue

    # Tant que pas accepté / refusé / annulé → Escrow actif
    if not (r.get("Dossier accepte") or r.get("Dossier refuse") or r.get("Dossier Annule")):
        escrow_actif_total += acomptes
        continue

    # Dès qu’accepté / refusé / annulé → Escrow à réclamer
    if r.get("Escrow_a_reclamer"):
        escrow_a_reclamer_total += acomptes

# =====================================================
# KPI DOSSIERS
# =====================================================
total_dossiers = len(df)
dossiers_acceptes = df["Dossier accepte"].astype(bool).sum()
dossiers_refuses = df["Dossier refuse"].astype(bool).sum()
dossiers_annules = df["Dossier Annule"].astype(bool).sum()

# Soldes
df["Solde"] = df.apply(lambda r: to_float(r.get("Montant honoraires (US $)", 0))
                                   + to_float(r.get("Autres frais (US $)", 0))
                                   - total_acomptes(r), axis=1)

dossiers_soldes = (df["Solde"] <= 0).sum()
dossiers_non_soldes = (df["Solde"] > 0).sum()
dossiers_negatifs = (df["Solde"] < 0).sum()

# =====================================================
# AFFICHAGE KPI
# =====================================================
st.subheader("📊 Indicateurs clés")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Dossiers", total_dossiers)
k2.metric("Acceptés", dossiers_acceptes)
k3.metric("Refusés", dossiers_refuses)
k4.metric("Annulés", dossiers_annules)

k5, k6, k7 = st.columns(3)
k5.metric("Honoraires", f"${honoraires:,.2f}")
k6.metric("Total encaissé", f"${total_encaisse:,.2f}")
k7.metric("Solde dû", f"${solde_du:,.2f}")

k8, k9, k10 = st.columns(3)
k8.metric("Escrow actif", f"${escrow_actif_total:,.2f}")
k9.metric("Escrow à réclamer", f"${escrow_a_reclamer_total:,.2f}")
k10.metric("Escrow total", f"${escrow_actif_total + escrow_a_reclamer_total:,.2f}")

st.markdown("---")

# =====================================================
# TABLEAU SYNTHÈSE
# =====================================================
st.subheader("📋 Synthèse des dossiers")

cols = [
    "Dossier N", "Nom", "Visa",
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4",
    "Solde",
    "Escrow", "Escrow_a_reclamer", "Escrow_reclame",
    "Dossier accepte", "Dossier refuse", "Dossier Annule"
]

cols = [c for c in cols if c in df.columns]

st.dataframe(
    df[cols].sort_values("Dossier N"),
    use_container_width=True
)