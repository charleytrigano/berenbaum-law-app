import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database
from utils.escrow_history import log_escrow_history

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(page_title="💰 Escrow", page_icon="💰", layout="wide")
render_sidebar()
st.title("💰 Gestion des Escrows")

# =====================================================
# LOAD DATABASE
# =====================================================
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.info("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients).copy()
df["Dossier N"] = df["Dossier N"].astype(str)

# =====================================================
# OUTILS
# =====================================================
def to_float(v):
    try:
        return float(v or 0)
    except Exception:
        return 0.0


def total_acomptes(row):
    total = 0.0
    for i in range(1, 5):
        total += to_float(row.get(f"Acompte {i}", 0))
    return total


# =====================================================
# LOGIQUE ESCROW OFFICIELLE
# =====================================================
def get_escrow_state(row):
    if row.get("Escrow_reclame"):
        return "reclame"
    if row.get("Escrow_a_reclamer"):
        return "a_reclamer"
    if row.get("Escrow"):
        return "actif"
    return None


# =====================================================
# FILTRAGE PAR ÉTAT
# =====================================================
etat = st.radio(
    "Afficher les dossiers :",
    ["Escrow actif", "Escrow à réclamer", "Escrow réclamé"],
    horizontal=True,
)

if etat == "Escrow actif":
    view = df[df["Escrow"] == True]
elif etat == "Escrow à réclamer":
    view = df[df["Escrow_a_reclamer"] == True]
else:
    view = df[df["Escrow_reclame"] == True]

if view.empty:
    st.info("Aucun dossier dans cet état.")
    st.stop()

# =====================================================
# TABLEAU PRINCIPAL
# =====================================================
rows = []

for _, r in view.iterrows():
    rows.append({
        "Dossier N": r["Dossier N"],
        "Nom": r.get("Nom", ""),
        "Visa": r.get("Visa", ""),
        "Montant Escrow": total_acomptes(r),
    })

table = pd.DataFrame(rows)

st.dataframe(table, use_container_width=True)

total_escrow = table["Montant Escrow"].sum()
st.metric("💼 Total Escrow", f"${total_escrow:,.2f}")

# =====================================================
# ACTION SUR UN DOSSIER
# =====================================================
st.markdown("---")
st.subheader("⚙️ Action sur un dossier")

dossier_sel = st.selectbox(
    "Sélectionner un dossier",
    table["Dossier N"].tolist()
)

row = df[df["Dossier N"] == dossier_sel].iloc[0]
idx = row.name

montant = total_acomptes(row)
etat_actuel = get_escrow_state(row)

st.info(f"État actuel : **{etat_actuel}** — Montant : ${montant:,.2f}")

# =====================================================
# TRANSITIONS AUTORISÉES
# =====================================================
if etat_actuel == "actif":
    if st.button("➡️ Passer en Escrow à réclamer"):
        log_escrow_history(
            db,
            row,
            "actif",
            "a_reclamer",
            montant,
            "Changement statut dossier",
        )
        df.loc[idx, "Escrow"] = False
        df.loc[idx, "Escrow_a_reclamer"] = True
        save_database(db)
        st.rerun()

elif etat_actuel == "a_reclamer":
    if st.button("✅ Marquer comme Escrow réclamé"):
        log_escrow_history(
            db,
            row,
            "a_reclamer",
            "reclame",
            montant,
            "Réclamation manuelle",
        )
        df.loc[idx, "Escrow_a_reclamer"] = False
        df.loc[idx, "Escrow_reclame"] = True
        save_database(db)
        st.rerun()

elif etat_actuel == "reclame":
    st.success("Escrow déjà réclamé. Aucune action possible.")