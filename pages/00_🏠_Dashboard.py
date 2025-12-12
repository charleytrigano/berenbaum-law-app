import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database

# ---------------------------------------------------------
# CONFIG — TOUJOURS EN PREMIER
# ---------------------------------------------------------
st.set_page_config(
    page_title="🏠 Dashboard",
    page_icon="🏠",
    layout="wide"
)

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
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
# 🔑 Dossier ID (clé métier fiable)
# ---------------------------------------------------------
if "Dossier ID" not in clients.columns:
    clients["Dossier ID"] = clients["Dossier N"].astype(str)
    db["clients"] = clients.to_dict(orient="records")
    save_database(db)

clients["Dossier ID"] = clients["Dossier ID"].astype(str)

# ---------------------------------------------------------
# NORMALISATION BOOL
# ---------------------------------------------------------
def to_bool(v):
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in ["true", "1", "yes", "oui"]

BOOL_COLS = [
    "Dossier envoye",
    "Dossier accepte",
    "Dossier refuse",
    "Dossier Annule",
    "RFE",
    "Escrow",
]

for col in BOOL_COLS:
    if col not in clients.columns:
        clients[col] = False
    clients[col] = clients[col].apply(to_bool)

# ---------------------------------------------------------
# NORMALISATION NUMÉRIQUE
# ---------------------------------------------------------
NUM_COLS = [
    "Montant honoraires (US $)",
    "Autres frais (US $)",
    "Acompte 1",
    "Acompte 2",
    "Acompte 3",
    "Acompte 4",
]

for col in NUM_COLS:
    if col not in clients.columns:
        clients[col] = 0.0
    clients[col] = pd.to_numeric(clients[col], errors="coerce").fillna(0.0)

# ---------------------------------------------------------
# 🎛️ FILTRES
# ---------------------------------------------------------
st.subheader("🎛️ Filtres")

f1, f2, f3, f4 = st.columns(4)

# Catégorie
categories = ["Tous"] + sorted(c for c in clients["Categories"].dropna().unique() if c)
cat = f1.selectbox("Catégorie", categories)

# Sous-catégorie dépendante
if cat != "Tous":
    souscats = ["Tous"] + sorted(
        clients[clients["Categories"] == cat]["Sous-categories"].dropna().unique()
    )
else:
    souscats = ["Tous"] + sorted(clients["Sous-categories"].dropna().unique())

sous = f2.selectbox("Sous-catégorie", souscats)

# Visa
if sous != "Tous":
    visas = ["Tous"] + sorted(
        clients[clients["Sous-categories"] == sous]["Visa"].dropna().unique()
    )
else:
    visas = ["Tous"] + sorted(clients["Visa"].dropna().unique())

visa = f3.selectbox("Visa", visas)

# Statut
statuts = ["Tous", "Envoyé", "Accepté", "Refusé", "Annulé", "RFE"]
statut = f4.selectbox("Statut", statuts)

# ---------------------------------------------------------
# 🔍 APPLICATION FILTRES
# ---------------------------------------------------------
df = clients.copy()

if cat != "Tous":
    df = df[df["Categories"] == cat]

if sous != "Tous":
    df = df[df["Sous-categories"] == sous]

if visa != "Tous":
    df = df[df["Visa"] == visa]

if statut != "Tous":
    mapping = {
        "Envoyé": "Dossier envoye",
        "Accepté": "Dossier accepte",
        "Refusé": "Dossier refuse",
        "Annulé": "Dossier Annule",
        "RFE": "RFE",
    }
    df = df[df[mapping[statut]]]

# ---------------------------------------------------------
# 🧮 CALCUL KPI
# ---------------------------------------------------------
nb_dossiers = df["Dossier ID"].nunique()

honoraires = df["Montant honoraires (US $)"].sum()
autres_frais = df["Autres frais (US $)"].sum()
total_facture = honoraires + autres_frais

total_encaisse = (
    df["Acompte 1"]
    + df["Acompte 2"]
    + df["Acompte 3"]
    + df["Acompte 4"]
).sum()

solde_du = total_facture - total_encaisse

# ---------------------------------------------------------
# 📊 KPI
# ---------------------------------------------------------
st.subheader("📊 Indicateurs financiers")

k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("📁 Dossiers", nb_dossiers)
k2.metric("💼 Honoraires ($)", f"{honoraires:,.0f}")
k3.metric("🧾 Autres frais ($)", f"{autres_frais:,.0f}")
k4.metric("📄 Total facturé ($)", f"{total_facture:,.0f}")
k5.metric("💰 Total encaissé ($)", f"{total_encaisse:,.0f}")
k6.metric("⚠️ Solde dû ($)", f"{solde_du:,.0f}")

# ---------------------------------------------------------
# 📋 TABLEAU
# ---------------------------------------------------------
st.subheader("📋 Dossiers filtrés")

st.dataframe(
    df[
        [
            "Dossier N",
            "Nom",
            "Categories",
            "Sous-categories",
            "Visa",
            "Montant honoraires (US $)",
            "Autres frais (US $)",
            "Acompte 1",
            "Acompte 2",
            "Acompte 3",
            "Acompte 4",
            "Dossier envoye",
            "Dossier accepte",
            "Dossier refuse",
            "Escrow",
        ]
    ],
    use_container_width=True,
)
