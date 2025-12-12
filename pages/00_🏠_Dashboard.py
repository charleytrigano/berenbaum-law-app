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
# UTILS KPI COMPACT
# ---------------------------------------------------------
def kpi_small(title, value):
    st.markdown(
        f"""
        <div style="
            background:#111;
            border:1px solid #333;
            border-radius:10px;
            padding:10px 12px;
            text-align:center;
        ">
            <div style="
                font-size:13px;
                color:#D8B86A;
                margin-bottom:4px;
                font-weight:500;
            ">
                {title}
            </div>
            <div style="
                font-size:20px;
                font-weight:700;
                color:#FFD777;
                line-height:1.2;
            ">
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
clients = pd.DataFrame(db.get("clients", []))

if clients.empty:
    st.warning("Aucun dossier trouvé.")
    st.stop()

# ---------------------------------------------------------
# NORMALISATION
# ---------------------------------------------------------
clients["Dossier N"] = clients["Dossier N"].astype(str)

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
BOOL_COLS = [
    "Dossier envoye",
    "Dossier accepte",
    "Dossier refuse",
    "Dossier Annule",
    "RFE",
    "Escrow",
    "Escrow_a_reclamer",
    "Escrow_reclame",
]

for c in BOOL_COLS:
    clients[c] = clients.get(c, False).astype(bool)

# ---------------------------------------------------------
# FILTRES
# ---------------------------------------------------------
st.subheader("🎛️ Filtres")

f1, f2, f3, f4 = st.columns(4)

cat = f1.selectbox(
    "Catégorie",
    ["Toutes"] + sorted(clients["Categories"].dropna().unique().tolist()),
)

if cat != "Toutes":
    df = clients[clients["Categories"] == cat]
else:
    df = clients.copy()

souscat = f2.selectbox(
    "Sous-catégorie",
    ["Toutes"] + sorted(df["Sous-categories"].dropna().unique().tolist()),
)

if souscat != "Toutes":
    df = df[df["Sous-categories"] == souscat]

visa = f3.selectbox(
    "Visa",
    ["Tous"] + sorted(df["Visa"].dropna().unique().tolist()),
)

if visa != "Tous":
    df = df[df["Visa"] == visa]

statut = f4.selectbox(
    "Statut",
    ["Tous", "Envoyé", "Accepté", "Refusé", "Annulé", "RFE"],
)

if statut != "Tous":
    mapping = {
        "Envoyé": "Dossier envoye",
        "Accepté": "Dossier accepte",
        "Refusé": "Dossier refuse",
        "Annulé": "Dossier Annule",
        "RFE": "RFE",
    }
    df = df[df[mapping[statut]] == True]

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
# KPI ESCROW GLOBAL
# ---------------------------------------------------------
st.subheader("💰 Escrow – Vue globale")

escrow_actif = df[df["Escrow"] == True]
escrow_a_reclamer = df[df["Escrow_a_reclamer"] == True]
escrow_reclame = df[df["Escrow_reclame"] == True]

e1, e2, e3 = st.columns(3)

kpi_small("🟡 Escrow actif", f"${escrow_actif['Acompte 1'].sum():,.0f}")
kpi_small("🟠 Escrow à réclamer", f"${escrow_a_reclamer['Acompte 1'].sum():,.0f}")
kpi_small("🟢 Escrow réclamé", f"${escrow_reclame['Acompte 1'].sum():,.0f}")

# ---------------------------------------------------------
# TABLEAU DOSSIERS
# ---------------------------------------------------------
st.subheader("📋 Liste des dossiers")

cols_display = [
    "Dossier N",
    "Nom",
    "Categories",
    "Sous-categories",
    "Visa",
    "Montant honoraires (US $)",
    "Autres frais (US $)",
    "Total facturé",
    "Total encaissé",
    "Solde dû",
    "Dossier envoye",
    "Dossier accepte",
    "Dossier refuse",
    "Dossier Annule",
    "RFE",
]

st.dataframe(
    df[cols_display].sort_values("Dossier N"),
    use_container_width=True,
    height=450,
)

st.markdown("— Dashboard opérationnel & certifié")
