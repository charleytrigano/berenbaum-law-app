import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

st.set_page_config(page_title="Liste des dossiers", page_icon="📁", layout="wide")
st.title("📁 Liste des dossiers")

# ---------------------------------------------------------
# 🔹 Chargement base
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)

# ---------------------------------------------------------
# 🔹 Normalisation colonnes manquantes
# ---------------------------------------------------------
REQUIRED_BOOL_COLS = [
    "Dossier envoye",
    "Dossier accepte",
    "Dossier refuse",
    "Dossier Annule",
    "Escrow",
]

for col in REQUIRED_BOOL_COLS:
    if col not in df.columns:
        df[col] = False

def normalize_bool(x):
    if isinstance(x, bool):
        return x
    if str(x).lower() in ["true", "1", "1.0", "yes", "oui"]:
        return True
    return False

for col in REQUIRED_BOOL_COLS:
    df[col] = df[col].apply(normalize_bool)

# ---------------------------------------------------------
# 🔹 Badges graphiques
# ---------------------------------------------------------
def badge(row):

    envoye = row.get("Dossier envoye", False)
    accepte = row.get("Dossier accepte", False)
    refuse = row.get("Dossier refuse", False)
    annule = row.get("Dossier Annule", False)
    escrow = row.get("Escrow", False)

    if annule:
        return "❌ Annulé"
    if refuse:
        return "⛔ Refusé"
    if accepte:
        return "✅ Accepté"
    if envoye:
        return "📤 Envoyé"
    if escrow:
        return "💰 Escrow en cours"

    return "📝 En cours"

df["Statut"] = df.apply(badge, axis=1)

# ---------------------------------------------------------
# 🔹 Affichage tableau principal
# ---------------------------------------------------------
colonnes_affichage = [
    "Dossier N",
    "Nom",
    "Date",
    "Categories",
    "Visa",
    "Statut",
]

df = df[colonnes_affichage]

st.dataframe(df, use_container_width=True)
