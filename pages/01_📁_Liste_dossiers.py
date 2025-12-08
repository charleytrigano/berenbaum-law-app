import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

st.set_page_config(page_title="Liste des dossiers", page_icon="📁", layout="wide")
st.title("📁 Liste des dossiers")

# ---------------------------------------------------------
# 🔹 Charger la base JSON
# ---------------------------------------------------------
db = load_database()
df = pd.DataFrame(db.get("clients", []))

if df.empty:
    st.warning("Aucun dossier trouvé.")
    st.stop()

# ---------------------------------------------------------
# 🔹 Nettoyage des dates
# ---------------------------------------------------------
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# ---------------------------------------------------------
# 🔹 Barre de recherche
# ---------------------------------------------------------
st.subheader("🔍 Recherche")

search = st.text_input("Rechercher par nom / visa / numéro", "")

if search.strip():
    df = df[
        df["Nom"].str.contains(search, case=False, na=False)
        | df["Visa"].str.contains(search, case=False, na=False)
        | df["Dossier N"].astype(str).str.contains(search)
    ]

# ---------------------------------------------------------
# 🔹 Filtres avancés
# ---------------------------------------------------------
st.subheader("🎛️ Filtres")

col1, col2, col3, col4 = st.columns(4)

# Catégorie
cats = ["Tous"] + sorted(df["Categories"].dropna().unique().tolist())
f_cat = col1.selectbox("Catégorie", cats)

# Sous-catégorie
ss = ["Tous"] + sorted(df["Sous-categories"].dropna().unique().tolist())
f_ss = col2.selectbox("Sous-catégorie", ss)

# Visa
visas = ["Tous"] + sorted(df["Visa"].dropna().unique().tolist())
f_visa = col3.selectbox("Visa", visas)

# Escrow
f_escrow = col4.selectbox("Escrow", ["Tous", "En cours", "À réclamer", "Réclamé"])

# Appliquer filtres
if f_cat != "Tous":
    df = df[df["Categories"] == f_cat]

if f_ss != "Tous":
    df = df[df["Sous-categories"] == f_ss]

if f_visa != "Tous":
    df = df[df["Visa"] == f_visa]

if f_escrow == "En cours":
    df = df[df["Escrow"] == True]
elif f_escrow == "À réclamer":
    df = df[df["Escrow_a_reclamer"] == True]
elif f_escrow == "Réclamé":
    df = df[df["Escrow_reclame"] == True]

# ---------------------------------------------------------
# 🔹 Statut visuel
# ---------------------------------------------------------
def badge(row):
    if row["Dossier envoye"]:
        return "🟦 Envoyé"
    if row["Dossier accepte"]:
        return "🟩 Accepté"
    if row["Dossier refuse"]:
        return "🟥 Refusé"
    if row["Dossier Annule"]:
        return "🟧 Annulé"
    return "⬜ En cours"

df["Statut"] = df.apply(badge, axis=1)

# ---------------------------------------------------------
# 🔹 Escrow : affichage compact
# ---------------------------------------------------------
def escrow_status(row):
    if row["Escrow"]:
        return "🟡 En cours"
    if row["Escrow_a_reclamer"]:
        return "🟠 À réclamer"
    if row["Escrow_reclame"]:
        return "🟢 Réclamé"
    return ""

df["Escrow ▶"] = df.apply(escrow_status, axis=1)

# ---------------------------------------------------------
# 🔹 Tableau
# ---------------------------------------------------------
st.subheader("📋 Résultats")

show_cols = [
    "Dossier N",
    "Nom",
    "Date",
    "Categories",
    "Sous-categories",
    "Visa",
    "Statut",
    "Escrow ▶",
]

st.dataframe(df[show_cols], use_container_width=True)

# ---------------------------------------------------------
# 🔹 Sélection d’un dossier pour modification
# ---------------------------------------------------------
st.markdown("---")
st.subheader("✏️ Modifier un dossier")

liste = df["Dossier N"].astype(int).tolist()
choix = st.selectbox("Choisir un dossier :", liste)

if st.button("Ouvrir dans Modifier"):
    st.switch_page("pages/03_✏️_Modifier_dossier.py")

