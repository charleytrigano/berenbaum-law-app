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

df = pd.DataFrame(clients)
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
    return sum(to_float(row.get(f"Acompte {i}", 0)) for i in range(1, 5))

def last_escrow_date(dossier_n):
    events = [
        e for e in escrow_history
        if str(e.get("Dossier N")) == str(dossier_n)
        and e.get("Etat") == "Escrow_a_reclamer"
    ]
    if not events:
        return None
    dates = [pd.to_datetime(e["Date"]) for e in events if e.get("Date")]
    return max(dates) if dates else None

# =====================================================
# CONSTRUCTION TABLE ESCROW À RÉCLAMER
# =====================================================
rows = []

today = pd.Timestamp.today()

for _, r in df.iterrows():
    if not r.get("Escrow_a_reclamer"):
        continue

    montant = total_acomptes(r)
    date_ref = last_escrow_date(r["Dossier N"])
    if date_ref:
        days = (today - date_ref).days
    else:
        days = None

    rows.append({
        "Dossier N": r["Dossier N"],
        "Nom": r.get("Nom", ""),
        "Visa": r.get("Visa", ""),
        "Montant escrow": montant,
        "Date à réclamer": date_ref.date() if date_ref else "",
        "Ancienneté (jours)": days,
    })

escrow_df = pd.DataFrame(rows)

# =====================================================
# KPI ANCIENNETÉ
# =====================================================
st.subheader("📊 KPI Escrow à réclamer")

c1, c2, c3, c4 = st.columns(4)

total = escrow_df["Montant escrow"].sum() if not escrow_df.empty else 0
c1.metric("Total Escrow à réclamer", f"${total:,.2f}")
c2.metric("> 30 jours", f"${escrow_df[escrow_df['Ancienneté (jours)'] > 30]['Montant escrow'].sum():,.2f}")
c3.metric("> 60 jours", f"${escrow_df[escrow_df['Ancienneté (jours)'] > 60]['Montant escrow'].sum():,.2f}")
c4.metric("> 90 jours", f"${escrow_df[escrow_df['Ancienneté (jours)'] > 90]['Montant escrow'].sum():,.2f}")

# =====================================================
# TABLEAU DÉTAILLÉ
# =====================================================
st.markdown("---")
st.subheader("📋 Détails des escrows à réclamer")

if escrow_df.empty:
    st.info("Aucun escrow à réclamer.")
else:
    st.dataframe(
        escrow_df.sort_values("Ancienneté (jours)", ascending=False),
        use_container_width=True
    )

# =====================================================
# PRÉPARATION ALERTES (VISUEL)
# =====================================================
st.markdown("---")
st.subheader("🚨 Alertes visuelles")

late_60 = escrow_df[escrow_df["Ancienneté (jours)"] >= 60]

if not late_60.empty:
    st.error(f"⚠️ {len(late_60)} dossier(s) avec escrow > 60 jours")
else:
    st.success("✔ Aucun escrow critique (> 60 jours)")