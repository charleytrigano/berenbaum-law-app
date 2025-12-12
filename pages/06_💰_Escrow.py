import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="💰 Escrow", page_icon="💰", layout="wide")
render_sidebar()
st.title("💰 Gestion des Escrows")

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def normalize_bool(v):
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in ["true", "1", "yes", "oui"]

def to_float(v):
    try:
        return float(v)
    except:
        return 0.0

# ---------------------------------------------------------
# LOAD DB
# ---------------------------------------------------------
db = load_database()
df = pd.DataFrame(db.get("clients", []))

if df.empty:
    st.info("Aucun dossier.")
    st.stop()

# Normalisation colonnes
for col in ["Escrow", "Escrow_a_reclamer", "Escrow_reclame"]:
    if col not in df.columns:
        df[col] = False
    df[col] = df[col].apply(normalize_bool)

df["Acompte 1"] = df["Acompte 1"].apply(to_float)
df["Date"] = pd.to_datetime(df.get("Date"), errors="coerce")

# Montant escrow = Acompte 1 UNIQUEMENT
df["Montant Escrow"] = df["Acompte 1"]

# ---------------------------------------------------------
# KPI
# ---------------------------------------------------------
total_actif = df[df["Escrow"]]["Montant Escrow"].sum()
total_a_reclamer = df[df["Escrow_a_reclamer"]]["Montant Escrow"].sum()
total_reclame = df[df["Escrow_reclame"]]["Montant Escrow"].sum()

c1, c2, c3 = st.columns(3)
c1.metric("💼 Escrow actif", f"${total_actif:,.2f}")
c2.metric("⏳ Escrow à réclamer", f"${total_a_reclamer:,.2f}")
c3.metric("✅ Escrow réclamé", f"${total_reclame:,.2f}")

if total_a_reclamer > 0:
    st.warning("⚠️ Des escrows sont en attente de réclamation.")

st.divider()

# =========================================================
# 1️⃣ ESCROW ACTIF → BOUTON PASSER À RÉCLAMER
# =========================================================
st.subheader("💼 Escrows actifs")

df_actif = df[df["Escrow"]].copy()

if df_actif.empty:
    st.success("Aucun escrow actif.")
else:
    for i, r in df_actif.iterrows():
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([1, 2.5, 1.5, 2])

            c1.markdown(f"**#{int(r['Dossier N'])}**")
            c2.markdown(f"**{r['Nom']}**")
            c3.markdown(f"💵 ${r['Montant Escrow']:,.2f}")

            if c4.button(
                "➡️ Passer en escrow à réclamer",
                key=f"to_reclamer_{r['Dossier N']}",
                use_container_width=True
            ):
                idx = df.index[i]
                df.loc[idx, ["Escrow", "Escrow_a_reclamer", "Escrow_reclame"]] = [False, True, False]
                db["clients"] = df.drop(columns=["Montant Escrow"], errors="ignore").to_dict("records")
                save_database(db)
                st.rerun()

st.divider()

# =========================================================
# 2️⃣ ESCROW À RÉCLAMER → BOUTON PASSER À RÉCLAMÉ
# =========================================================
st.subheader("⏳ Escrows à réclamer")

df_reclamer = df[df["Escrow_a_reclamer"]].copy()
df_reclamer["Ancienneté (jours)"] = (pd.Timestamp.today() - df_reclamer["Date"]).dt.days

if df_reclamer.empty:
    st.success("Aucun escrow à réclamer.")
else:
    for i, r in df_reclamer.iterrows():
        with st.container(border=True):
            c1, c2, c3, c4, c5 = st.columns([1, 2.2, 1.3, 1.3, 2])

            c1.markdown(f"**#{int(r['Dossier N'])}**")
            c2.markdown(f"**{r['Nom']}**")
            c3.markdown(f"💵 ${r['Montant Escrow']:,.2f}")
            c4.markdown(f"⏱️ {int(r['Ancienneté (jours)'])} j")

            if c5.button(
                "✅ Marquer comme réclamé",
                key=f"to_reclame_{r['Dossier N']}",
                type="primary",
                use_container_width=True
            ):
                idx = df.index[i]
                df.loc[idx, ["Escrow", "Escrow_a_reclamer", "Escrow_reclame"]] = [False, False, True]
                db["clients"] = df.drop(columns=["Montant Escrow"], errors="ignore").to_dict("records")
                save_database(db)
                st.rerun()

st.divider()

# =========================================================
# 3️⃣ ESCROW RÉCLAMÉ (LECTURE SEULE)
# =========================================================
st.subheader("✅ Escrows réclamés")

df_done = df[df["Escrow_reclame"]].copy()

if df_done.empty:
    st.info("Aucun escrow réclamé.")
else:
    st.dataframe(
        df_done[["Dossier N", "Nom", "Date", "Acompte 1", "Montant Escrow"]],
        use_container_width=True
    )

    st.download_button(
        "⬇️ Export escrows réclamés (CSV)",
        df_done.to_csv(index=False).encode("utf-8"),
        "escrow_reclame.csv",
        "text/csv",
    )

st.caption("Règle stricte : Montant Escrow = Acompte 1 uniquement.")
