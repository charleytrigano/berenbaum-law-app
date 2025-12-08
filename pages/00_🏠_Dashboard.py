import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")
st.title("🏠 Dashboard — Berenbaum Law App")

# ---------------------------------------------------------
# 🔹 Chargement DB
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier trouvé dans la base.")
    st.stop()

df = pd.DataFrame(clients)

# ---------------------------------------------------------
# 🔹 Normalisation colonnes
# ---------------------------------------------------------
BOOL_COLS = [
    "Dossier envoye",
    "Dossier accepte",
    "Dossier refuse",
    "Dossier Annule",
    "Escrow",
    "Escrow_a_reclamer",
    "Escrow_reclame",
]

for col in BOOL_COLS:
    if col not in df.columns:
        df[col] = False

def normalize_bool(x):
    if isinstance(x, bool):
        return x
    if str(x).lower() in ["1", "true", "yes", "oui"]:
        return True
    return False

for col in BOOL_COLS:
    df[col] = df[col].apply(normalize_bool)

# Dates
if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
else:
    df["Date"] = pd.NaT

df["Année"] = df["Date"].dt.year.fillna(0).astype(int)

# ---------------------------------------------------------
# 🔹 SIDEBAR — Filtres
# ---------------------------------------------------------
st.sidebar.header("🔍 Filtres")

annee_list = sorted(df["Année"].unique())
annee = st.sidebar.selectbox("Année :", ["Toutes"] + [str(a) for a in annee_list if a != 0])

categories = df.get("Categories", pd.Series([""])).fillna("")
categorie = st.sidebar.selectbox("Catégorie :", ["Toutes"] + sorted(categories.unique()))

statut = st.sidebar.selectbox("Statut :", [
    "Tous",
    "Envoyé",
    "Accepté",
    "Refusé",
    "Annulé",
    "Escrow en cours",
    "Escrow à réclamer",
    "Escrow réclamé",
])

# ---------------------------------------------------------
# 🔹 Application des filtres
# ---------------------------------------------------------
df_filtered = df.copy()

if annee != "Toutes":
    df_filtered = df_filtered[df_filtered["Année"] == int(annee)]

if categorie != "Toutes":
    df_filtered = df_filtered[df_filtered["Categories"] == categorie]

if statut == "Envoyé":
    df_filtered = df_filtered[df_filtered["Dossier envoye"]]
elif statut == "Accepté":
    df_filtered = df_filtered[df_filtered["Dossier accepte"]]
elif statut == "Refusé":
    df_filtered = df_filtered[df_filtered["Dossier refuse"]]
elif statut == "Annulé":
    df_filtered = df_filtered[df_filtered["Dossier Annule"]]
elif statut == "Escrow en cours":
    df_filtered = df_filtered[df_filtered["Escrow"]]
elif statut == "Escrow à réclamer":
    df_filtered = df_filtered[df_filtered["Escrow_a_reclamer"]]
elif statut == "Escrow réclamé":
    df_filtered = df_filtered[df_filtered["Escrow_reclame"]]

# ---------------------------------------------------------
# 🔹 KPIs
# ---------------------------------------------------------
st.subheader("📊 Indicateurs clés")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total dossiers", len(df_filtered))
k2.metric("Envoyés", df_filtered["Dossier envoye"].sum())
k3.metric("Acceptés", df_filtered["Dossier accepte"].sum())
k4.metric("Refusés", df_filtered["Dossier refuse"].sum())

k5, k6, k7, k8 = st.columns(4)
k5.metric("Annulés", df_filtered["Dossier Annule"].sum())
k6.metric("Escrow en cours", df_filtered["Escrow"].sum())
k7.metric("Escrow à réclamer", df_filtered["Escrow_a_reclamer"].sum())
k8.metric("Escrow réclamé", df_filtered["Escrow_reclame"].sum())

# Finances
if "Montant honoraires (US $)" in df_filtered.columns:
    honoraires = df_filtered["Montant honoraires (US $)"].fillna(0).sum()
else:
    honoraires = 0

if "Autres frais (US $)" in df_filtered.columns:
    frais = df_filtered["Autres frais (US $)"].fillna(0).sum()
else:
    frais = 0

if "Acompte 1" in df_filtered.columns:
    paiements = df_filtered[["Acompte 1","Acompte 2","Acompte 3","Acompte 4"]].fillna(0).sum().sum()
else:
    paiements = 0

solde = honoraires + frais - paiements

st.subheader("💰 Finances")

f1, f2, f3 = st.columns(3)
f1.metric("Total facturé", f"${honoraires + frais:,.2f}")
f2.metric("Paiements reçus", f"${paiements:,.2f}")
f3.metric("Solde restant", f"${solde:,.2f}")

# ---------------------------------------------------------
# 🔹 Tableau
# ---------------------------------------------------------
st.subheader("📄 Liste des dossiers filtrés")

cols = ["Dossier N", "Nom", "Date", "Visa", "Categories", "Dossier envoye", "Escrow"]
exist = [c for c in cols if c in df_filtered.columns]

st.dataframe(df_filtered[exist].sort_values("Date", ascending=False), use_container_width=True)
