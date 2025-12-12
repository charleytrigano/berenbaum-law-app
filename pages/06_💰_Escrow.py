import streamlit as st
import pandas as pd
from datetime import datetime

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database

# ---------------------------------------------------------
# CONFIG PAGE
# ---------------------------------------------------------
st.set_page_config(page_title="💰 Escrow", page_icon="💰", layout="wide")
render_sidebar()
st.title("💰 Gestion des Escrows")

# ---------------------------------------------------------
# CHARGEMENT BASE
# ---------------------------------------------------------
db = load_database()
clients = pd.DataFrame(db.get("clients", []))

if clients.empty:
    st.info("Aucun dossier trouvé.")
    st.stop()

# ---------------------------------------------------------
# NORMALISATION
# ---------------------------------------------------------
clients["Acompte 1"] = pd.to_numeric(clients.get("Acompte 1"), errors="coerce").fillna(0)
clients["Date"] = pd.to_datetime(clients.get("Date"), errors="coerce")

for col in ["Escrow", "Escrow_a_reclamer", "Escrow_reclame"]:
    if col not in clients.columns:
        clients[col] = False
    clients[col] = clients[col].astype(bool)

# ---------------------------------------------------------
# RÈGLE MÉTIER ESCROW
# 👉 Montant escrow = Acompte 1 UNIQUEMENT
# ---------------------------------------------------------
clients["Montant Escrow"] = clients.apply(
    lambda r: r["Acompte 1"] if r["Escrow"] else 0,
    axis=1
)

# ---------------------------------------------------------
# KPI GLOBAUX
# ---------------------------------------------------------
col1, col2, col3 = st.columns(3)

total_escrow = clients[clients["Escrow"] == True]["Montant Escrow"].sum()
total_a_reclamer = clients[clients["Escrow_a_reclamer"] == True]["Montant Escrow"].sum()
total_reclame = clients[clients["Escrow_reclame"] == True]["Montant Escrow"].sum()

col1.metric("💼 Escrow actif", f"${total_escrow:,.2f}")
col2.metric("⏳ Escrow à réclamer", f"${total_a_reclamer:,.2f}")
col3.metric("✅ Escrow réclamé", f"${total_reclame:,.2f}")

# ---------------------------------------------------------
# ALERTE AUTOMATIQUE
# ---------------------------------------------------------
if total_a_reclamer > 0:
    nb = len(clients[clients["Escrow_a_reclamer"] == True])
    st.warning(
        f"⚠️ {nb} dossier(s) avec "
        f"${total_a_reclamer:,.2f} d'escrow à réclamer"
    )

# ---------------------------------------------------------
# ONGLET ESCROW ACTIFS
# ---------------------------------------------------------
st.subheader("💼 Escrows actifs")

df_active = clients[clients["Escrow"] == True].copy()

st.dataframe(
    df_active[
        [
            "Dossier N",
            "Nom",
            "Date",
            "Acompte 1",
            "Montant Escrow",
            "Escrow_a_reclamer",
            "Escrow_reclame",
        ]
    ],
    use_container_width=True,
)

# ---------------------------------------------------------
# ONGLET ESCROW À RÉCLAMER (ANCIENNETÉ)
# ---------------------------------------------------------
st.subheader("⏳ Escrows à réclamer – ancienneté")

df_ar = clients[clients["Escrow_a_reclamer"] == True].copy()

if not df_ar.empty:
    df_ar["Ancienneté (jours)"] = (
        pd.Timestamp.today() - df_ar["Date"]
    ).dt.days

    st.dataframe(
        df_ar[
            [
                "Dossier N",
                "Nom",
                "Date",
                "Montant Escrow",
                "Ancienneté (jours)",
            ]
        ].sort_values("Ancienneté (jours)", ascending=False),
        use_container_width=True,
    )

    # EXPORT CSV
    csv = df_ar.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Export Escrows à réclamer (CSV)",
        csv,
        "escrow_a_reclamer.csv",
        "text/csv",
    )
else:
    st.success("✔ Aucun escrow en attente de réclamation.")

# ---------------------------------------------------------
# ONGLET ESCROW RÉCLAMÉS
# ---------------------------------------------------------
st.subheader("✅ Escrows réclamés")

df_done = clients[clients["Escrow_reclame"] == True].copy()

st.dataframe(
    df_done[
        [
            "Dossier N",
            "Nom",
            "Date",
            "Montant Escrow",
        ]
    ],
    use_container_width=True,
)

# ---------------------------------------------------------
# FIN
# ---------------------------------------------------------
st.markdown("### ✔ Escrow = Acompte 1 (règle métier validée)")
