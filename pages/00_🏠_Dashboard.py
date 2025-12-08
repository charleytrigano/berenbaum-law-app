import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")
st.title("🏠 Dashboard — Berenbaum Law App")

# ---------------------------------------------------------
# 🔹 Chargement de la base
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier trouvé dans la base.")
    st.stop()

df = pd.DataFrame(clients)

# ---------------------------------------------------------
# 🔹 Colonnes obligatoires
# ---------------------------------------------------------
REQUIRED_BOOL_COLS = [
    "Dossier envoye",
    "Dossier accepte",
    "Dossier refuse",
    "Dossier Annule",
    "Escrow",
    "Escrow_a_reclamer",
    "Escrow_reclame",
]

for col in REQUIRED_BOOL_COLS:
    if col not in df.columns:
        df[col] = False

# Normalisation booléens
def normalize_bool(x):
    if isinstance(x, bool):
        return x
    if str(x).lower() in ["true", "1", "1.0", "yes", "oui"]:
        return True
    return False

for col in REQUIRED_BOOL_COLS:
    df[col] = df[col].apply(normalize_bool)

# ---------------------------------------------------------
# 🔹 Colonnes dates
# ---------------------------------------------------------
DATE_COLS = ["Date", "Date envoi", "Date acceptation", "Date refus"]

for col in DATE_COLS:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

# ---------------------------------------------------------
# 📊 KPIs
# ---------------------------------------------------------
st.subheader("📊 Indicateurs clés")

total_dossiers = len(df)
dossiers_envoyes = df["Dossier envoye"].sum()
dossiers_acceptes = df["Dossier accepte"].sum()
dossiers_refuses = df["Dossier refuse"].sum()
dossiers_annules = df["Dossier Annule"].sum()

escrow_en_cours = df["Escrow"].sum()
escrow_a_reclamer = df["Escrow_a_reclamer"].sum()
escrow_reclame = df["Escrow_reclame"].sum()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total dossiers", total_dossiers)
k2.metric("Envoyés", dossiers_envoyes)
k3.metric("Acceptés", dossiers_acceptes)
k4.metric("Refusés", dossiers_refuses)

k5, k6, k7 = st.columns(3)
k5.metric("Annulés", dossiers_annules)
k6.metric("Escrow en cours", escrow_en_cours)
k7.metric("Escrow à réclamer", escrow_a_reclamer)

# ---------------------------------------------------------
# 📄 Tableau des derniers dossiers
# ---------------------------------------------------------
st.subheader("📄 Aperçu des derniers dossiers")

affichage_cols = ["Dossier N", "Nom", "Date", "Visa", "Dossier envoye", "Dossier accepte", "Escrow"]

existing_cols = [c for c in affichage_cols if c in df.columns]

st.dataframe(df[existing_cols].sort_values("Date", ascending=False), use_container_width=True)
