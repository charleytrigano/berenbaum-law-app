import streamlit as st
import pandas as pd
from components.database import load_database

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Tableau de bord – Berenbaum Law",
    page_icon="📁",
    layout="wide"
)

# ---------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------
try:
    db = load_database()
    st.success("Base de données chargée depuis Dropbox ✔")
except Exception as e:
    st.error(f"Erreur lors du chargement de Dropbox : {e}")
    db = {"clients": [], "visa": [], "escrow": [], "compta": []}


# ---------------------------------------------------
# STYLES
# ---------------------------------------------------
def kpi_card(title, value, color):
    st.markdown(f"""
        <div style="
            background:{color};
            padding:20px;
            border-radius:10px;
            text-align:center;
            color:white;
            font-size:22px;
            font-weight:700;">
            {value}<br>
            <span style="font-size:15px; font-weight:400;">{title}</span>
        </div>
    """, unsafe_allow_html=True)


st.title("📊 Tableau de bord – Berenbaum Law App")
st.write("Bienvenue dans l'application professionnelle de gestion des dossiers.")


# ---------------------------------------------------
# KPI CALCULATIONS
# ---------------------------------------------------
clients = db.get("clients", [])
visa = db.get("visa", [])
escrow = db.get("escrow", [])
compta = db.get("compta", [])

nb_clients = len(clients)
nb_visa = len(visa)
nb_escrow = len(escrow)

escrow_total = sum(float(x.get("montant", 0)) for x in escrow)


# ---------------------------------------------------
# KPI DISPLAY
# ---------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
with col1:
    kpi_card("Clients actifs", nb_clients, "#1E88E5")
with col2:
    kpi_card("Dossiers Visa", nb_visa, "#6A1B9A")
with col3:
    kpi_card("Mouvements Escrow", nb_escrow, "#00897B")
with col4:
    kpi_card("Total Escrow ($)", f"${escrow_total:,.2f}", "#E65100")


# ---------------------------------------------------
# APERÇU DES DONNÉES
# ---------------------------------------------------
st.markdown("### 🗂️ Aperçu des dossiers")

if nb_clients > 0:
    df_preview = pd.DataFrame(clients)

    # Sélection des colonnes clés si elles existent
    columns_to_show = [col for col in ["Dossier N", "Nom", "Date", "Catégories", "Visa"] if col in df_preview.columns]

    st.dataframe(
        df_preview[columns_to_show],
        use_container_width=True,
        height=350
    )
else:
    st.info("Aucun client pour le moment.")
