import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database  # ✔ correct import

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Berenbaum Law App",
    page_icon="📁",
    layout="wide"
)

st.title("📊 Tableau de bord – Berenbaum Law App")
st.write("Bienvenue dans l'application professionnelle de gestion des dossiers.")

# ---------------------------------------------------
# LOAD DATABASE (Dropbox)
# ---------------------------------------------------
try:
    db = load_database()
    st.success("Base de données chargée depuis Dropbox ✔")
except Exception as e:
    st.error(f"Erreur lors du chargement de Dropbox : {e}")
    db = {"clients": [], "visa": [], "escrow": [], "compta": []}

# ---------------------------------------------------
# DEBUG (temporaire)
# ---------------------------------------------------
with st.expander("🛠️ DEBUG — Contenu brut de la base"):
    st.write(db)

# ---------------------------------------------------
# EXTRACTION DES TABLES
# ---------------------------------------------------
clients = db.get("clients", [])
visa = db.get("visa", [])
escrow = db.get("escrow", [])
compta = db.get("compta", [])

# ---------------------------------------------------
# KPIs
# ---------------------------------------------------
st.subheader("📌 Indicateurs principaux")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Clients actifs", len(clients))
col2.metric("Dossiers Visa", len(visa))
col3.metric("Mouvements Escrow", len(escrow))

# Total Escrow sécurisé
total_escrow = 0
for e in escrow:
    try:
        total_escrow += float(e.get("Montant", 0))
    except:
        pass

col4.metric("Total Escrow ($)", f"${total_escrow:,.2f}")

# ---------------------------------------------------
# APERÇU DES CLIENTS
# ---------------------------------------------------
st.markdown("---")
st.subheader("🗂️ Aperçu des dossiers")

if not clients:
    st.info("Aucun dossier client enregistré.")
else:
    df = pd.DataFrame(clients)

    # Colonnes utiles
    cols = [c for c in ["Dossier N", "Nom", "Catégories", "Visa", "Date envoi"] if c in df.columns]

    st.dataframe(df[cols], use_container_width=True, height=350)
