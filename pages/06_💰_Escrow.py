import streamlit as st
import pandas as pd
from datetime import datetime

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="💰 Escrow", page_icon="💰", layout="wide")
render_sidebar()
st.title("💰 Gestion des Escrows")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = pd.DataFrame(db.get("clients", []))

if clients.empty:
    st.info("Aucun dossier.")
    st.stop()

# ---------------------------------------------------------
# NORMALISATION
# ---------------------------------------------------------
def to_bool(v):
    return str(v).lower() in ["true", "1", "yes", "oui"]

for col in ["Escrow", "Escrow_a_reclamer", "Escrow_reclame"]:
    if col not in clients.columns:
        clients[col] = False
    clients[col] = clients[col].apply(to_bool)

clients["Acompte 1"] = pd.to_numeric(clients.get("Acompte 1", 0), errors="coerce").fillna(0)

clients["Date"] = pd.to_datetime(clients["Date"], errors="coerce")

# ---------------------------------------------------------
# SEGMENTATION DES ETATS
# ---------------------------------------------------------
escrow_actif = clients[
    (clients["Escrow"] == True) &
    (clients["Escrow_a_reclamer"] == False) &
    (clients["Escrow_reclame"] == False)
]

escrow_a_reclamer = clients[
    (clients["Escrow_a_reclamer"] == True)
]

escrow_reclame = clients[
    (clients["Escrow_reclame"] == True)
]

# ---------------------------------------------------------
# KPI
# ---------------------------------------------------------
def kpi_block(label, df):
    col1, col2 = st.columns(2)
    col1.metric("📁 Dossiers", len(df))
    col2.metric("💰 Montant Escrow", f"${df['Acompte 1'].sum():,.2f}")

# ---------------------------------------------------------
# ONGLET
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "🟡 Escrow actif",
    "🟠 Escrow à réclamer",
    "🟢 Escrow réclamé"
])

# =========================================================
# ESCROW ACTIF
# =========================================================
with tab1:
    st.subheader("🟡 Escrow actif")
    kpi_block("Escrow actif", escrow_actif)

    for idx, row in escrow_actif.iterrows():
        with st.expander(f"Dossier {row['Dossier N']} — {row['Nom']}"):
            st.write(f"💰 Montant Escrow : **${row['Acompte 1']:,.2f}**")

            if st.button(
                "➡️ Passer en Escrow à réclamer",
                key=f"to_reclamer_{idx}"
            ):
                clients.loc[idx, "Escrow"] = False
                clients.loc[idx, "Escrow_a_reclamer"] = True
                clients.loc[idx, "Escrow_reclame"] = False

                db["clients"] = clients.to_dict(orient="records")
                save_database(db)
                st.success("Escrow passé à réclamer.")
                st.rerun()

# =========================================================
# ESCROW A RECLAMER
# =========================================================
with tab2:
    st.subheader("🟠 Escrow à réclamer")
    kpi_block("Escrow à réclamer", escrow_a_reclamer)

    for idx, row in escrow_a_reclamer.iterrows():
        days = (datetime.now() - row["Date"]).days if pd.notna(row["Date"]) else "—"

        with st.expander(f"Dossier {row['Dossier N']} — {row['Nom']}"):
            st.write(f"💰 Montant Escrow : **${row['Acompte 1']:,.2f}**")
            st.write(f"🕓 Ancienneté : **{days} jours**")

            if st.button(
                "✅ Marquer comme Escrow réclamé",
                key=f"to_reclame_{idx}"
            ):
                clients.loc[idx, "Escrow"] = False
                clients.loc[idx, "Escrow_a_reclamer"] = False
                clients.loc[idx, "Escrow_reclame"] = True

                db["clients"] = clients.to_dict(orient="records")
                save_database(db)
                st.success("Escrow marqué comme réclamé.")
                st.rerun()

# =========================================================
# ESCROW RECLAME
# =========================================================
with tab3:
    st.subheader("🟢 Escrow réclamé")
    kpi_block("Escrow réclamé", escrow_reclame)

    st.dataframe(
        escrow_reclame[[
            "Dossier N", "Nom", "Acompte 1", "Date"
        ]],
        use_container_width=True
    )

    st.download_button(
        "⬇️ Export CSV Escrow réclamé",
        data=escrow_reclame.to_csv(index=False),
        file_name="escrow_reclame.csv",
        mime="text/csv"
    )
