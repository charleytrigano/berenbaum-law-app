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
clients = db.get("clients", [])

if not clients:
    st.info("Aucun dossier.")
    st.stop()

df = pd.DataFrame(clients)
df["Dossier N"] = df["Dossier N"].astype(str)

# Montant escrow = Acompte 1 UNIQUEMENT
df["Montant Escrow"] = df["Acompte 1"].fillna(0).astype(float)

# ---------------------------------------------------------
# FILTRES D'ÉTATS (EXCLUSIFS)
# ---------------------------------------------------------
df_actif = df[df["Escrow"] == True]
df_reclamer = df[df["Escrow_a_reclamer"] == True]
df_reclame = df[df["Escrow_reclame"] == True]

# ---------------------------------------------------------
# KPI GLOBAL
# ---------------------------------------------------------
st.subheader("📊 Indicateurs Escrow")

k1, k2, k3 = st.columns(3)

k1.metric(
    "Escrow actifs",
    len(df_actif),
    f"${df_actif['Montant Escrow'].sum():,.2f}",
)

k2.metric(
    "Escrow à réclamer",
    len(df_reclamer),
    f"${df_reclamer['Montant Escrow'].sum():,.2f}",
)

k3.metric(
    "Escrow réclamés",
    len(df_reclame),
    f"${df_reclame['Montant Escrow'].sum():,.2f}",
)

st.markdown("---")

# ---------------------------------------------------------
# ONGLET PAR ÉTAT
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "💼 Escrow actif",
    "📤 Escrow à réclamer",
    "✅ Escrow réclamé",
])

# =========================================================
# TAB 1 — ESCROW ACTIF
# =========================================================
with tab1:
    st.subheader("💼 Escrow actif")

    total = df_actif["Montant Escrow"].sum()
    st.info(f"💰 Total escrow actif : ${total:,.2f}")

    if df_actif.empty:
        st.info("Aucun escrow actif.")
    else:
        for i, row in df_actif.iterrows():
            st.markdown(f"### Dossier {row['Dossier N']} — ${row['Montant Escrow']:,.2f}")
            st.write(row["Nom"])

            if st.button(
                "➡️ Passer à « Escrow à réclamer »",
                key=f"to_reclamer_{row['Dossier N']}"
            ):
                df.loc[i, "Escrow"] = False
                df.loc[i, "Escrow_a_reclamer"] = True
                df.loc[i, "Escrow_reclame"] = False

                db["clients"] = df.to_dict(orient="records")
                save_database(db)
                st.success("Escrow déplacé vers « à réclamer ».")
                st.rerun()

    if not df_actif.empty:
        if st.button("📄 Export PDF — Escrow actif"):
            export_escrow_pdf(df_actif, "escrow_actif.pdf")
            st.success("PDF généré.")

# =========================================================
# TAB 2 — ESCROW À RÉCLAMER
# =========================================================
with tab2:
    st.subheader("📤 Escrow à réclamer")

    total = df_reclamer["Montant Escrow"].sum()
    st.warning(f"💰 Total escrow à réclamer : ${total:,.2f}")

    if df_reclamer.empty:
        st.info("Aucun escrow à réclamer.")
    else:
        for i, row in df_reclamer.iterrows():
            st.markdown(f"### Dossier {row['Dossier N']} — ${row['Montant Escrow']:,.2f}")
            st.write(row["Nom"])

            if st.button(
                "✅ Marquer comme réclamé",
                key=f"to_reclame_{row['Dossier N']}"
            ):
                df.loc[i, "Escrow"] = False
                df.loc[i, "Escrow_a_reclamer"] = False
                df.loc[i, "Escrow_reclame"] = True

                db["clients"] = df.to_dict(orient="records")
                save_database(db)
                st.success("Escrow marqué comme réclamé.")
                st.rerun()

    if not df_reclamer.empty:
        if st.button("📄 Export PDF — Escrow à réclamer"):
            export_escrow_pdf(df_reclamer, "escrow_a_reclamer.pdf")
            st.success("PDF généré.")

# =========================================================
# TAB 3 — ESCROW RÉCLAMÉ
# =========================================================
with tab3:
    st.subheader("✅ Escrow réclamé")

    total = df_reclame["Montant Escrow"].sum()
    st.success(f"💰 Total escrow réclamé : ${total:,.2f}")

    if df_reclame.empty:
        st.info("Aucun escrow réclamé.")
    else:
        st.dataframe(
            df_reclame[
                ["Dossier N", "Nom", "Montant Escrow"]
            ],
            use_container_width=True
        )

    if not df_reclame.empty:
        if st.button("📄 Export PDF — Escrow réclamé"):
            export_escrow_pdf(df_reclame, "escrow_reclame.pdf")
            st.success("PDF généré.")