import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="Fiche dossier", page_icon="📄", layout="wide")
st.title("📄 Fiche dossier – Vue complète")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.error("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)

# Nettoyage minimal
df["Dossier N"] = pd.to_numeric(df["Dossier N"], errors="coerce")
df = df.dropna(subset=["Dossier N"])
df["Dossier N"] = df["Dossier N"].astype(int)

nums = sorted(df["Dossier N"].unique())
selected = st.selectbox("Sélectionner un dossier :", nums)

row = df[df["Dossier N"] == selected].iloc[0].copy()

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def money(v):
    try:
        return f"${float(v):,.2f}"
    except:
        return "$0.00"

def parse_date(value):
    try:
        v = pd.to_datetime(value, errors="coerce")
        if pd.isna(v):
            return None
        return v.date()
    except:
        return None

def badge_status(solde, total):
    if solde <= 0:
        return "<span style='color:#22c55e; font-weight:bold;'>✔ Payé</span>"
    elif solde < total:
        return "<span style='color:#eab308; font-weight:bold;'>➖ Partiellement payé</span>"
    else:
        return "<span style='color:#ef4444; font-weight:bold;'>✘ Impayé</span>"

# ---------------------------------------------------------
# FACTURATION ↔ ACOMPTES (2 colonnes)
# ---------------------------------------------------------
hon = float(row.get("Montant honoraires (US $)", 0))
frais = float(row.get("Autres frais (US $)", 0))
total = hon + frais

ac_values = [
    float(row.get("Acompte 1", 0)),
    float(row.get("Acompte 2", 0)),
    float(row.get("Acompte 3", 0)),
    float(row.get("Acompte 4", 0)),
]

dates_ac = [
    row.get("Date Acompte 1", ""),
    row.get("Date Acompte 2", ""),
    row.get("Date Acompte 3", ""),
    row.get("Date Acompte 4", "")
]

modes_ac = [
    row.get("Mode Acompte 1", ""),
    row.get("Mode Acompte 2", ""),
    row.get("Mode Acompte 3", ""),
    row.get("Mode Acompte 4", "")
]

total_paid = sum(ac_values)
solde = total - total_paid

badge = badge_status(solde, total)

colF1, colF2 = st.columns(2)

# ---------------------------------------------------------
# COLONNE GAUCHE – FACTURATION
# ---------------------------------------------------------
with colF1:
    st.markdown("### 💰 Facturation")

    st.markdown(f"""
    <div style="padding:15px; border-radius:10px; background:#1f2937;">
        <p><b>Montant honoraires :</b> {money(hon)}</p>
        <p><b>Autres frais :</b> {money(frais)}</p>
        <hr style="border:0.5px solid #374151;">
        <p><b>Total facturé :</b> {money(total)}</p>
        <p><b>Total payé :</b> {money(total_paid)}</p>
        <p><b>Solde restant :</b> {money(solde)}</p>
        <p><b>Statut :</b> {badge}</p>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# COLONNE DROITE – ACOMPTES & RÈGLEMENTS
# ---------------------------------------------------------
with colF2:
    st.markdown("### 🏦 Acomptes & Paiements")

    for i in range(4):
        st.markdown(f"""
        <div style="padding:12px; margin-bottom:10px; border-radius:8px; background:#111827; border:1px solid #374151;">
            <p><b>Acompte {i+1} :</b> {money(ac_values[i])}</p>
            <p><b>Mode :</b> {modes_ac[i] or "—"}</p>
            <p><b>Date :</b> {dates_ac[i] or "—"}</p>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# INFORMATIONS GÉNÉRALES
# ---------------------------------------------------------
st.markdown("---")
st.markdown("## 📌 Informations générales")

st.markdown(f"""
**Nom :** {row['Nom']}  
**Catégorie :** {row.get("Categories", "")}  
**Sous-catégorie :** {row.get("Sous-categories", "")}  
**Visa :** {row.get("Visa", "")}  
**Date création :** {row.get("Date", "")}
""")

# ---------------------------------------------------------
# TIMELINE
# ---------------------------------------------------------
st.markdown("---")
st.markdown("## 🕓 Timeline du dossier")

def timeline(title, date):
    return f"""
    <div style="padding:10px; margin-bottom:12px; border-left:4px solid #3b82f6;">
        <div style="font-weight:bold; color:#3b82f6;">{title}</div>
        <div style="opacity:0.8;">{date}</div>
    </div>
    """

st.markdown(timeline("📄 Dossier créé", row.get("Date", "")), unsafe_allow_html=True)

if row.get("Escrow", False):
    st.markdown(timeline("💰 Escrow ouvert", row.get("Date", "")), unsafe_allow_html=True)

if row.get("Dossier envoye", False):
    st.markdown(timeline("📤 Dossier envoyé", row.get("Date envoi", "")), unsafe_allow_html=True)

# ---------------------------------------------------------
# ACTIONS
# ---------------------------------------------------------
st.markdown("---")
st.markdown("## ⚙️ Actions")

colA1, colA2, colA3 = st.columns(3)

with colA1:
    if st.button("✏️ Modifier ce dossier"):
        st.switch_page("pages/03_✏️_Modifier_dossier.py")

with colA2:
    st.button("📄 Export PDF (à venir)")

with colA3:
    st.button("🗑️ Supprimer (sécurisé)", type="secondary")

from components.export_pdf import generate_pdf

colA1, colA2, colA3 = st.columns(3)

with colA1:
    if st.button("✏️ Modifier ce dossier"):
        st.switch_page("pages/03_✏️_Modifier_dossier.py")

with colA2:
    if st.button("📄 Export PDF"):
        fname = generate_pdf(row)
        with open(fname, "rb") as f:
            st.download_button(
                label="⬇ Télécharger le PDF",
                data=f,
                file_name=f"Dossier_{row['Dossier N']}.pdf",
                mime="application/pdf"
            )

with colA3:
    st.button("🗑️ Supprimer (sécurisé)", type="secondary")

