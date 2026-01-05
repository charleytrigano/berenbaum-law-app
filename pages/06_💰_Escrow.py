import streamlit as st
import pandas as pd
from datetime import datetime

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database

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
escrow_history = db.get("escrow_history", [])

if not clients:
    st.error("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients).copy()
df["Dossier N"] = df["Dossier N"].astype(str)

# =====================================================
# UTILS
# =====================================================
def to_float(v):
    try:
        return float(v or 0)
    except Exception:
        return 0.0

def is_true(v):
    return str(v).strip().lower() in ["true", "1", "yes", "oui"]

# =====================================================
# CALCUL MONTANT ESCROW (LOGIQUE VALIDÉE)
# Tant que dossier NON accepté / refusé / annulé :
# 👉 TOUS les acomptes sont en escrow
# =====================================================
def escrow_amount(row):
    if (
        is_true(row.get("Dossier accepte"))
        or is_true(row.get("Dossier refuse"))
        or is_true(row.get("Dossier Annule"))
    ):
        return 0.0

    total = 0.0
    for i in range(1, 5):
        total += to_float(row.get(f"Acompte {i}", 0))
    return total

df["Escrow Montant"] = df.apply(escrow_amount, axis=1)

# =====================================================
# ONGLET
# =====================================================
tab1, tab2 = st.tabs([
    "📋 Dossiers en Escrow",
    "🕓 Historique Escrow"
])

# =====================================================
# TAB 1 — LISTE ESCROW
# =====================================================
with tab1:

    escrow_df = df[df["Escrow Montant"] > 0].copy()

    st.subheader("📋 Dossiers avec montants en Escrow")

    if escrow_df.empty:
        st.info("Aucun dossier actuellement en escrow.")
    else:
        display_cols = [
            "Dossier N", "Nom", "Visa",
            "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4",
            "Escrow Montant",
            "Dossier accepte", "Dossier refuse", "Dossier Annule",
        ]
        cols = [c for c in display_cols if c in escrow_df.columns]

        st.dataframe(
            escrow_df[cols].sort_values("Dossier N"),
            use_container_width=True
        )

    # KPI
    st.markdown("---")
    st.subheader("📊 KPI Escrow")

    k1, k2 = st.columns(2)
    k1.metric("Dossiers en Escrow", len(escrow_df))
    k2.metric(
        "Montant total en Escrow",
        f"${escrow_df['Escrow Montant'].sum():,.2f}"
    )

    # =================================================
    # ACTIONS ESCROW
    # =================================================
    st.markdown("---")
    st.subheader("🔁 Actions Escrow")

    dossier_action = st.selectbox(
        "Sélectionner un dossier",
        escrow_df["Dossier N"].tolist() if not escrow_df.empty else []
    )

    if dossier_action:
        row = escrow_df[escrow_df["Dossier N"] == dossier_action].iloc[0]
        idx = df[df["Dossier N"] == dossier_action].index[0]
        montant = row["Escrow Montant"]

        if st.button("📤 Passer en Escrow à réclamer"):
            df.loc[idx, "Escrow"] = False
            df.loc[idx, "Escrow_a_reclamer"] = True
            df.loc[idx, "Escrow_reclame"] = False

            escrow_history.append({
                "Dossier N": dossier_action,
                "Action": "Escrow → À réclamer",
                "Montant": montant,
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            db["clients"] = df.to_dict(orient="records")
            db["escrow_history"] = escrow_history
            save_database(db)

            st.success("✔ Escrow passé à réclamer")
            st.rerun()

        if is_true(row.get("Escrow_a_reclamer")):
            if st.button("✅ Marquer comme Escrow réclamé"):
                df.loc[idx, "Escrow"] = False
                df.loc[idx, "Escrow_a_reclamer"] = False
                df.loc[idx, "Escrow_reclame"] = True

                escrow_history.append({
                    "Dossier N": dossier_action,
                    "Action": "Escrow réclamé",
                    "Montant": montant,
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

                db["clients"] = df.to_dict(orient="records")
                db["escrow_history"] = escrow_history
                save_database(db)

                st.success("✔ Escrow marqué comme réclamé")
                st.rerun()

# =====================================================
# TAB 2 — HISTORIQUE ESCROW
# =====================================================
with tab2:

    st.subheader("🕓 Historique des escrows")

    hist_df = pd.DataFrame(escrow_history)

    if hist_df.empty:
        st.info("Aucun historique escrow pour le moment.")
    else:
        st.dataframe(
            hist_df.sort_values("Date", ascending=False),
            use_container_width=True
        )

        st.download_button(
            "⬇️ Exporter l’historique Escrow (CSV)",
            data=hist_df.to_csv(index=False),
            file_name="historique_escrow.csv",
            mime="text/csv"
        )