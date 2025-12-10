import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database
from utils.sidebar import render_sidebar

# ---------------------------------------------------------
# Sidebar avec logo
# ---------------------------------------------------------
render_sidebar()

# ---------------------------------------------------------
# Page config
# ---------------------------------------------------------
st.set_page_config(page_title="📁 Liste des dossiers", page_icon="📁", layout="wide")
st.title("📁 Liste des dossiers")

# ---------------------------------------------------------
# Charger DB
# ---------------------------------------------------------
db = load_database()
clients = pd.DataFrame(db.get("clients", []))

if clients.empty:
    st.warning("Aucun dossier trouvé.")
    st.stop()

# ---------------------------------------------------------
# Normalisation colonnes
# ---------------------------------------------------------
clients["Date"] = pd.to_datetime(clients["Date"], errors="coerce")
clients["Année"] = clients["Date"].dt.year

# Mapping des colonnes
rename_map = {
    "Dossier_envoye": "Dossier envoye",
    "Dossier envoyé": "Dossier envoye"
}
clients.rename(columns=rename_map, inplace=True)

# Si colonne manquante → créer
for col in ["Dossier envoye", "Dossier accepte", "Dossier refuse", "Dossier Annule", "RFE"]:
    if col not in clients.columns:
        clients[col] = False

# ---------------------------------------------------------
# 🎛️ FILTRES AVANCÉS (haut de page)
# ---------------------------------------------------------
st.subheader("🎛️ Filtres")

col1, col2, col3, col4, col5 = st.columns(5)

# 1️⃣ Année
annees = ["Toutes"] + sorted(clients["Année"].dropna().unique().tolist())
annee = col1.selectbox("Année", annees)

# 2️⃣ Catégorie
categories = ["Toutes"] + sorted([c for c in clients["Categories"].dropna().unique() if c != ""])
cat = col2.selectbox("Catégorie", categories)

# 3️⃣ Sous-catégorie dépendante
if cat != "Toutes":
    souscats = ["Toutes"] + sorted(clients[clients["Categories"] == cat]["Sous-categories"].dropna().unique())
else:
    souscats = ["Toutes"] + sorted(clients["Sous-categories"].dropna().unique())

sous = col3.selectbox("Sous-catégorie", souscats)

# 4️⃣ Visa dépendant
if sous != "Toutes":
    visas = ["Toutes"] + sorted(clients[clients["Sous-categories"] == sous]["Visa"].dropna().unique())
else:
    visas = ["Toutes"] + sorted(clients["Visa"].dropna().unique())

visa = col4.selectbox("Visa", visas)

# 5️⃣ Statut
statuts = ["Tous", "Envoyé", "Accepté", "Refusé", "Annulé", "RFE"]
statut = col5.selectbox("Statut", statuts)

# ---------------------------------------------------------
# 🔍 APPLICATION DES FILTRES
# ---------------------------------------------------------
df = clients.copy()

# Année
if annee != "Toutes":
    df = df[df["Année"] == annee]

# Catégorie
if cat != "Toutes":
    df = df[df["Categories"] == cat]

# Sous-catégorie
if sous != "Toutes":
    df = df[df["Sous-categories"] == sous]

# Visa
if visa != "Toutes":
    df = df[df["Visa"] == visa]

# Statut
if statut != "Tous":
    statut_map = {
        "Envoyé": "Dossier envoye",
        "Accepté": "Dossier accepte",
        "Refusé": "Dossier refuse",
        "Annulé": "Dossier Annule",
        "RFE": "RFE"
    }
    df = df[df[statut_map[statut]] == True]

# ---------------------------------------------------------
# Résultat
# ---------------------------------------------------------
st.markdown(f"### 📄 {len(df)} dossier(s) trouvé(s)")

df_display = df[[
    "Dossier N", "Nom", "Date",
    "Categories", "Sous-categories", "Visa",
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Dossier envoye", "Dossier accepte", "Dossier refuse",
    "Escrow"
]]

st.dataframe(df_display, use_container_width=True, height=600)
