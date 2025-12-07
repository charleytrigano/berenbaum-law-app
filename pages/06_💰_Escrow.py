import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.set_page_config(page_title="Escrow", page_icon="💰", layout="wide")
st.title("💰 Gestion des Escrows")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)
df["Escrow"] = df.get("Escrow", False).apply(
    lambda x: True if x in [True, 1, "1"] else False
)
st.write("VALEUR ESCROW LUE PAR ESCROW.PY :", df[["Dossier N", "Escrow"]])


# ---------------------------------------------------------
# CORRECTION : conversion Escrow en bool strict
# ---------------------------------------------------------
def normalize_escrow(x):
    if isinstance(x, bool):
        return x
    if isinstance(x, (int, float)):
        return x == 1
    if isinstance(x, str):
        return x.strip().lower() in ["true", "1", "yes"]
    return False

df["Escrow"] = df.get("Escrow", False).apply(normalize_escrow)

# ---------------------------------------------------------
# TABLEAU PRINCIPAL
# ---------------------------------------------------------
st.subheader("📌 Escrow en cours")
escrow_cours = df[df["Escrow"] == True]
st.dataframe(escrow_cours, use_container_width=True)
