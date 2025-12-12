import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="🏠 Dashboard", page_icon="🏠", layout="wide")
render_sidebar()
st.title("🏠 Dashboard – Vue globale")

# ---------------------------------------------------------
# KPI COMPACT
# ---------------------------------------------------------
def kpi_small(title, value):
    st.markdown(
        f"""
        <div style="
            background:#111;
            border:1px solid #333;
            border-radius:10px;
            padding:10px;
            text-align:center;
        ">
            <div style="font-size:13px;color:#D8B86A;font-weight:500;">
                {title}
            </div>
            <div style="font-size:20px;font-weight:700;color:#FFD777;">
                {value}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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

NUM_COLS = [
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4"
]

for c in NUM_COLS:
    df[c] = pd.to_numeric(df.get(c, 0), errors="coerce").fillna(0)

df["Total facturé"] = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
df["Total encaissé"] = df["Acompte 1"] + df["Acompte 2"] + df["Acompte 3"] + df["Acompte 4"]
df["Solde dû"] = df["Total facturé"] - df["Total encaissé"]

BOOL_COLS = [
    "Dossier envoye", "Dossier accepte", "Dossier refuse",
    "Dossier Annule", "RFE",
    "Escrow", "Escrow_a_reclamer", "Escrow_reclame"
]
for c in BOOL_COLS:
    df[c] = df.get(c, False).astype(bool)

# ---------------------------------------------------------
# FILTRES
# ---------------------------------------------------------
st.subheader("🎛️ Filtres")

f1, f2, f3, f4 = st.columns(4)

cat = f1.selectbox("Catégorie", ["Toutes"] + sorted(df["Categories"].dropna().unique()))
if cat != "Toutes":
    df = df[df["Categories"] == cat]

sous = f2.selectbox("Sous-catégorie", ["Toutes"] + sorted(df["Sous-categories"].dropna().unique()))
if sous != "Toutes":
    df = df[df["Sous-categories"] == sous]

visa = f3.selectbox("Visa", ["Tous"] + sorted(df["Visa"].dropna().unique()))
if visa != "Tous":
    df = df[df["Visa"] == visa]

statut = f4.selectbox("Statut", ["Tous", "Envoyé", "Accepté", "Refusé", "Annulé", "RFE"])
if statut != "Tous":
    map_statut = {
        "Envoyé": "Dossier envoye",
        "Accepté": "Dossier accepte",
        "Refusé": "Dossier refuse",
        "Annulé": "Dossier Annule",
        "RFE": "RFE"
    }
    df = df[df[map_statut[statut]]]

# ---------------------------------------------------------
# KPI FINANCIERS
# ---------------------------------------------------------
st.subheader("📊 Indicateurs financiers")

k1, k2, k3, k4, k5, k6 = st.columns(6)

kpi_small("📁 Dossiers", len(df))
kpi_small("💰 Honoraires", f"${df['Montant honoraires (US $)'].sum():,.0f}")
kpi_small("➕ Autres frais", f"${df['Autres frais (US $)'].sum():,.0f}")
kpi_small("🧾 Total facturé", f"${df['Total facturé'].sum():,.0f}")
kpi_small("💵 Total encaissé", f"${df['Total encaissé'].sum():,.0f}")
kpi_small("⚠️ Solde dû", f"${df['Solde dû'].sum():,.0f}")

# ---------------------------------------------------------
# KPI ESCROW
# ---------------------------------------------------------
st.subheader("💰 Escrow – Synthèse")

e1, e2, e3 = st.columns(3)
kpi_small("🟡 Escrow actif", f"${df[df['Escrow']]['Acompte 1'].sum():,.0f}")
kpi_small("🟠 Escrow à réclamer", f"${df[df['Escrow_a_reclamer']]['Acompte 1'].sum():,.0f}")
kpi_small("🟢 Escrow réclamé", f"${df[df['Escrow_reclame']]['Acompte 1'].sum():,.0f}")

# ---------------------------------------------------------
# TABLEAU COMPLET DOSSIERS
# ---------------------------------------------------------
st.subheader("📋 Dossiers & paiements")

cols = [
    "Dossier N", "Nom", "Categories", "Sous-categories", "Visa",
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Acompte 1", "Date Acompte 1", "Mode Acompte 1",
    "Acompte 2", "Date Acompte 2", "Mode Acompte 2",
    "Acompte 3", "Date Acompte 3", "Mode Acompte 3",
    "Acompte 4", "Date Acompte 4", "Mode Acompte 4",
    "Total encaissé", "Solde dû",
    "Dossier envoye", "Dossier accepte", "Dossier refuse", "Dossier Annule", "RFE"
]

# Sécurité colonnes
for c in cols:
    if c not in df.columns:
        df[c] = ""

st.dataframe(
    df[cols].sort_values("Dossier N"),
    use_container_width=True,
    height=520
)

st.markdown("— Dashboard certifié & complet")