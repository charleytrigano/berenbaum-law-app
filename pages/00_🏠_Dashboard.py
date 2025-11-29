import streamlit as st
import json
from utils.dropbox_utils import load_json_from_dropbox

st.set_page_config(page_title="📊 Tableau de bord – Berenbaum Law App", layout="wide")

st.title("📊 Tableau de bord – Berenbaum Law App")
st.write("Bienvenue dans l'application professionnelle de gestion des dossiers.")

# -----------------------------
# 1. Charger la base depuis Dropbox
# -----------------------------
db = load_json_from_dropbox("/Apps/berenbaum-law/database.json")

if db is None:
    st.error("❌ Impossible de charger la base depuis Dropbox.")
    st.stop()

st.success("Base de données chargée depuis Dropbox ✔")

# -----------------------------
# 2. DEBUG (à garder provisoirement)
# -----------------------------
with st.expander("🛠️ DEBUG — Contenu brut de la base"):
    st.json(db)

# -----------------------------
# 3. Sécurité : s'assurer que les clés existent
# -----------------------------
clients = db.get("clients", [])
visa = db.get("visa", [])
escrow = db.get("escrow", [])
compta = db.get("compta", [])

# -----------------------------
# 4. Statistiques principales
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("📁 Clients actifs", len(clients))
col2.metric("🛂 Dossiers Visa", len(visa))
col3.metric("💵 Mouvements Escrow", len(escrow))

# Total escrow
total_escrow = 0
for entry in escrow:
    amount = entry.get("Montant ($)") or entry.get("Amount ($)") or 0
    try:
        total_escrow += float(amount)
    except:
        pass

col4.metric("💰 Total Escrow ($)", f"${total_escrow:,.2f}")

# -----------------------------
# 5. Aperçu des dossiers clients
# -----------------------------
st.subheader("🗂️ Aperçu des dossiers")

if len(clients) == 0:
    st.info("Aucun dossier client enregistré.")
else:
    # Afficher un tableau compact
    preview = [
        {
            "N° dossier": c.get("Dossier N"),
            "Nom": c.get("Nom"),
            "Visa": c.get("Visa"),
            "Montant": c.get("Montant honoraires (US $)")
        }
        for c in clients[:15]
    ]
    st.table(preview)
