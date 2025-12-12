import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_databasedef kpi_small(title, value):
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
# CONFIG & SIDEBAR
# ---------------------------------------------------------
st.set_page_config(page_title="🏠 Dashboard", page_icon="🏠", layout="wide")
render_sidebar()
st.title("🏠 Dashboard — Berenbaum Law App")

# ---------------------------------------------------------
# LOAD DATABASE
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

clients["Date"] = pd.to_datetime(clients["Date"], errors="coerce")

for col in [
    "Dossier envoye",
    "Dossier accepte",
    "Dossier refuse",
    "Dossier Annule",
    "RFE",
    "Escrow",
    "Escrow_a_reclamer",
    "Escrow_reclame",
]:
    if col not in clients.columns:
        clients[col] = False
    clients[col] = clients[col].astype(bool)

for col in [
    "Montant honoraires (US $)",
    "Autres frais (US $)",
    "Acompte 1",
    "Acompte 2",
    "Acompte 3",
    "Acompte 4",
]:
    if col not in clients.columns:
        clients[col] = 0.0
    clients[col] = pd.to_numeric(clients[col], errors="coerce").fillna(0.0)

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

# ---------------------------------------------------------
# FILTRES
# ---------------------------------------------------------
st.subheader("🎛️ Filtres")

c1, c2, c3, c4 = st.columns(4)

categories = ["Tous"] + sorted(clients["Categories"].dropna().unique())
cat = c1.selectbox("Catégorie", categories)

if cat != "Tous":
    df = clients[clients["Categories"] == cat]
else:
    df = clients.copy()

souscats = ["Tous"] + sorted(df["Sous-categories"].dropna().unique())
sous = c2.selectbox("Sous-catégorie", souscats)

if sous != "Tous":
    df = df[df["Sous-categories"] == sous]

visas = ["Tous"] + sorted(df["Visa"].dropna().unique())
visa = c3.selectbox("Visa", visas)

if visa != "Tous":
    df = df[df["Visa"] == visa]

statuts = ["Tous", "Envoyé", "Accepté", "Refusé", "Annulé", "RFE"]
statut = c4.selectbox("Statut", statuts)

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
st.subheader("📊 Indicateurs clés")

k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("📁 Dossiers", len(df))
k2.metric("💰 Honoraires", f"${df['Montant honoraires (US $)'].sum():,.2f}")
k3.metric("➕ Autres frais", f"${df['Autres frais (US $)'].sum():,.2f}")
k4.metric("🧾 Total facturé", f"${df['Total facturé'].sum():,.2f}")
k5.metric("💵 Total encaissé", f"${df['Total encaissé'].sum():,.2f}")
k6.metric("⚠️ Solde dû", f"${df['Solde dû'].sum():,.2f}")

# ---------------------------------------------------------
# KPI ESCROW (LOGIQUE CERTIFIÉE)
# ---------------------------------------------------------
st.subheader("💰 Escrow — Vue globale")

escrow_actif = df[
    (df["Escrow"] == True)
    & (df["Escrow_a_reclamer"] == False)
    & (df["Escrow_reclame"] == False)
]

escrow_a_reclamer = df[df["Escrow_a_reclamer"] == True]
escrow_reclame = df[df["Escrow_reclame"] == True]

e1, e2, e3 = st.columns(3)

e1.metric(
    "🟡 Escrow actif",
    f"${escrow_actif['Acompte 1'].sum():,.2f}",
    help="Acompte 1 uniquement",
)
e2.metric(
    "🟠 Escrow à réclamer",
    f"${escrow_a_reclamer['Acompte 1'].sum():,.2f}",
)
e3.metric(
    "🟢 Escrow réclamé",
    f"${escrow_reclame['Acompte 1'].sum():,.2f}",
)

# ---------------------------------------------------------
# TABLEAU FINAL
# ---------------------------------------------------------
st.subheader("📋 Dossiers")

cols = [
    "Dossier N",
    "Nom",
    "Date",
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
    df[cols].sort_values("Dossier N"),
    use_container_width=True,
    height=500,
)
