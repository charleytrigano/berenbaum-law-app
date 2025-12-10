import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database
from utils.sidebar import render_sidebar

# ---------------------------------------------------------
# Sidebar (Logo + Navigation)
# ---------------------------------------------------------
render_sidebar()

st.set_page_config(page_title="💰 Escrow", page_icon="💰", layout="wide")
st.title("💰 Escrow – Suivi des fonds placés")

# ---------------------------------------------------------
# Charger la base de données
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
df = pd.DataFrame(clients)

if df.empty:
    st.warning("Aucun dossier trouvé.")
    st.stop()

# ---------------------------------------------------------
# Normalisation colonnes
# ---------------------------------------------------------
def normalize_bool(x):
    if isinstance(x, bool):
        return x
    if str(x).lower() in ["1", "true", "yes", "oui"]:
        return True
    return False

for col in ["Escrow", "Acompte 1", "Date Acompte 1"]:
    if col not in df.columns:
        df[col] = None

df["Escrow"] = df["Escrow"].apply(normalize_bool)
df["Acompte 1"] = pd.to_numeric(df["Acompte 1"], errors="coerce").fillna(0)

# ---------------------------------------------------------
# Filtrer : dossiers en Escrow actif
# ---------------------------------------------------------
df_escrow = df[df["Escrow"] == True].copy()

if df_escrow.empty:
    st.info("Aucun dossier actuellement en Escrow.")
    st.stop()

# ---------------------------------------------------------
# Calcul du montant placé en Escrow
# (TOUJOURS = Acompte 1)
# ---------------------------------------------------------
df_escrow["Montant Escrow"] = df_escrow["Acompte 1"]

# Extraction date si disponible
df_escrow["Date Escrow"] = df_escrow["Date Acompte 1"].replace("None", "")

# ---------------------------------------------------------
# Affichage tableau
# ---------------------------------------------------------
st.subheader("📄 Dossiers actuellement en Escrow")

df_display = df_escrow[[
    "Dossier N",
    "Nom",
    "Visa",
    "Montant Escrow",
    "Date Escrow"
]]

st.dataframe(df_display, use_container_width=True)

# ---------------------------------------------------------
# Total des fonds en Escrow
# ---------------------------------------------------------
total = df_escrow["Montant Escrow"].sum()

st.markdown(f"""
### 💵 Total en Escrow :  
# **${total:,.2f}**
""")
