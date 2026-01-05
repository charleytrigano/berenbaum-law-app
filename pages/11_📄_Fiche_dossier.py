import os
import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database
from utils.timeline_builder import build_timeline
from utils.pdf_export import export_dossier_pdf

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(page_title="📄 Fiche dossier", page_icon="📄", layout="wide")
render_sidebar()
st.title("📄 Fiche dossier")

# =====================================================
# LOAD DATABASE
# =====================================================
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.error("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients).copy()
df["Dossier N"] = df["Dossier N"].astype(str)

# =====================================================
# SÉLECTION DOSSIER (support clic externe)
# =====================================================
default_dossier = st.session_state.get("open_dossier")

if default_dossier and default_dossier in df["Dossier N"].values:
    selected = default_dossier
    st.session_state["open_dossier"] = None
else:
    selected = st.selectbox(
        "Sélectionner un dossier",
        sorted(df["Dossier N"].unique())
    )

dossier = df[df["Dossier N"] == selected].iloc[0].to_dict()

# =====================================================
# INFOS GÉNÉRALES
# =====================================================
st.markdown("---")
st.subheader(f"Dossier {dossier.get('Dossier N')} — {dossier.get('Nom','')}")

info_df = pd.DataFrame([
    ["Catégorie", dossier.get("Categories","")],
    ["Sous-catégorie", dossier.get("Sous-categories","")],
    ["Visa", dossier.get("Visa","")],
    ["Date dossier", dossier.get("Date","")],
], columns=["Champ", "Valeur"])

st.table(info_df)

# =====================================================
# FACTURATION & RÈGLEMENTS
# =====================================================
st.markdown("---")
st.subheader("💰 Facturation & règlements")

honoraires = float(dossier.get("Montant honoraires (US $)", 0) or 0)
frais = float(dossier.get("Autres frais (US $)", 0) or 0)
total_facture = honoraires + frais

rows = []
total_encaisse = 0.0

for i in range(1, 5):
    montant = float(dossier.get(f"Acompte {i}", 0) or 0)
    if montant > 0:
        total_encaisse += montant
        rows.append([
            f"Acompte {i}",
            f"${montant:,.2f}",
            dossier.get(f"Mode Acompte {i}", dossier.get("mode de paiement","")),
            dossier.get(f"Date Acompte {i}","")
        ])

fact_df = pd.DataFrame(rows, columns=["Paiement", "Montant", "Mode", "Date"])
st.dataframe(fact_df, use_container_width=True)

solde = total_facture - total_encaisse

k1, k2, k3, k4 = st.columns(4)
k1.metric("Honoraires", f"${honoraires:,.2f}")
k2.metric("Autres frais", f"${frais:,.2f}")
k3.metric("Total encaissé", f"${total_encaisse:,.2f}")
k4.metric("Solde dû", f"${solde:,.2f}")

# =====================================================
# STATUT FINANCIER
# =====================================================
if solde <= 0:
    st.success("✅ Dossier soldé")
elif total_encaisse > 0:
    st.warning("🟡 Paiement partiel")
else:
    st.error("🔴 Impayé")

# =====================================================
# STATUTS & ESCROW (TABLEAU ALIGNÉ)
# =====================================================
st.markdown("---")
st.subheader("📦 Statuts & Escrow")

status_rows = [
    ["Dossier envoyé", dossier.get("Dossier envoye", False), dossier.get("Date envoi","")],
    ["Dossier accepté", dossier.get("Dossier accepte", False), dossier.get("Date acceptation","")],
    ["Dossier refusé", dossier.get("Dossier refuse", False), dossier.get("Date refus","")],
    ["Dossier annulé", dossier.get("Dossier Annule", False), dossier.get("Date annulation","")],
    ["RFE", dossier.get("RFE", False), dossier.get("Date reclamation","")],
]

status_df = pd.DataFrame(status_rows, columns=["Statut", "Actif", "Date"])
st.dataframe(status_df, use_container_width=True)

# ESCROW
escrow_amount = float(dossier.get("Acompte 1", 0) or 0)

if dossier.get("Escrow"):
    st.info(f"💼 Escrow actif — ${escrow_amount:,.2f}")
elif dossier.get("Escrow_a_reclamer"):
    st.warning(f"📤 Escrow à réclamer — ${escrow_amount:,.2f}")
elif dossier.get("Escrow_reclame"):
    st.success(f"✅ Escrow réclamé — ${escrow_amount:,.2f}")
else:
    st.write("Aucun escrow pour ce dossier.")

# =====================================================
# TIMELINE
# =====================================================
st.markdown("---")
st.subheader("🕓 Timeline du dossier")

timeline = build_timeline(dossier)

if not timeline:
    st.info("Aucun événement enregistré.")
else:
    for ev in timeline:
        label = f"**{ev['date'].date()}** — {ev['label']}"
        if ev.get("amount"):
            label += f" — ${ev['amount']:,.2f}"
        st.markdown(label)

# =====================================================
# COMMENTAIRE
# =====================================================
commentaire = dossier.get("Commentaire","")
if str(commentaire).strip():
    st.markdown("---")
    st.subheader("📝 Commentaire")
    st.write(commentaire)

# =====================================================
# EXPORT PDF
# =====================================================
st.markdown("---")
if st.button("📄 Exporter la fiche dossier en PDF", type="primary"):
    output = f"/tmp/dossier_{dossier['Dossier N']}.pdf"
    export_dossier_pdf(dossier, output)

    with open(output, "rb") as f:
        st.download_button(
            "⬇️ Télécharger le PDF",
            data=f,
            file_name=f"Dossier_{dossier['Dossier N']}.pdf",
            mime="application/pdf"
        )