import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database
from utils.pdf_export import export_escrow_pdf

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
    st.info("Aucun dossier trouvé.")
    st.stop()

# ---------------------------------------------------------
# NORMALISATION
# ---------------------------------------------------------
for col in [
    "Escrow", "Escrow_a_reclamer", "Escrow_reclame"
]:
    if col not in clients.columns:
        clients[col] = False
    clients[col] = clients[col].astype(bool)

if "Acompte 1" not in clients.columns:
    clients["Acompte 1"] = 0.0

clients["Montant Escrow"] = clients["Acompte 1"].fillna(0.0)

# ---------------------------------------------------------
# ONGLET ESCROW
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "🟡 Escrow actif",
    "🟠 Escrow à réclamer",
    "🟢 Escrow réclamé",
])

# =========================================================
# 🟡 ESCROW ACTIF
# =========================================================
with tab1:
    df_actif = clients[clients["Escrow"] == True]

    st.subheader("🟡 Dossiers en Escrow actif")

    total = df_actif["Montant Escrow"].sum()
    st.metric("💰 Total Escrow actif", f"${total:,.2f}")

    if not df_actif.empty:
        for idx, row in df_actif.iterrows():
            with st.expander(f"Dossier {row['Dossier N']} — {row['Nom']}"):
                st.write(f"**Montant Escrow :** ${row['Montant Escrow']:,.2f}")

                if st.button(
                    "➡️ Passer en Escrow à réclamer",
                    key=f"to_reclamer_{idx}"
                ):
                    clients.loc[idx, "Escrow"] = False
                    clients.loc[idx, "Escrow_a_reclamer"] = True
                    clients.loc[idx, "Escrow_reclame"] = False

                    db["clients"] = clients.to_dict(orient="records")
                    save_database(db)
                    st.success("Dossier déplacé vers Escrow à réclamer.")
                    st.rerun()
    else:
        st.info("Aucun dossier en Escrow actif.")

    if not df_actif.empty:
        if st.button("📄 Export PDF — Escrow actif"):
            export_escrow_pdf(
                df_actif[["Dossier N", "Nom", "Montant Escrow"]],
                "escrow_actif.pdf"
            )
            st.success("PDF généré.")

# =========================================================
# 🟠 ESCROW À RÉCLAMER
# =========================================================
with tab2:
    df_reclamer = clients[clients["Escrow_a_reclamer"] == True]

    st.subheader("🟠 Escrows à réclamer")

    total = df_reclamer["Montant Escrow"].sum()
    st.metric("💰 Total à réclamer", f"${total:,.2f}")

    if not df_reclamer.empty:
        for idx, row in df_reclamer.iterrows():
            with st.expander(f"Dossier {row['Dossier N']} — {row['Nom']}"):
                st.write(f"**Montant à réclamer :** ${row['Montant Escrow']:,.2f}")

                if st.button(
                    "✔️ Marquer comme réclamé",
                    key=f"to_reclame_{idx}"
                ):
                    clients.loc[idx, "Escrow"] = False
                    clients.loc[idx, "Escrow_a_reclamer"] = False
                    clients.loc[idx, "Escrow_reclame"] = True

                    db["clients"] = clients.to_dict(orient="records")
                    save_database(db)
                    st.success("Dossier marqué comme Escrow réclamé.")
                    st.rerun()
    else:
        st.info("Aucun escrow à réclamer.")

    if not df_reclamer.empty:
        if st.button("📄 Export PDF — Escrow à réclamer"):
            export_escrow_pdf(
                df_reclamer[["Dossier N", "Nom", "Montant Escrow"]],
                "escrow_a_reclamer.pdf"
            )
            st.success("PDF généré.")

# =========================================================
# 🟢 ESCROW RÉCLAMÉ
# =========================================================
with tab3:
    df_reclame = clients[clients["Escrow_reclame"] == True]

    st.subheader("🟢 Escrows réclamés")

    total = df_reclame["Montant Escrow"].sum()
    st.metric("💰 Total réclamé", f"${total:,.2f}")

    if not df_reclame.empty:
        st.dataframe(
            df_reclame[
                ["Dossier N", "Nom", "Montant Escrow"]
            ],
            use_container_width=True
        )

        if st.button("📄 Export PDF — Escrow réclamé"):
            export_escrow_pdf(
                df_reclame[["Dossier N", "Nom", "Montant Escrow"]],
                "escrow_reclame.pdf"
            )
            st.success("PDF généré.")
    else:
        st.info("Aucun escrow réclamé.")