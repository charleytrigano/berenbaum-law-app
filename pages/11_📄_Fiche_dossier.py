import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database
from utils.timeline_builder import build_timeline
from utils.pdf_export import export_dossier_pdf

# ---------------------------------------------------------
# CONFIG & SIDEBAR
# ---------------------------------------------------------
st.set_page_config(page_title="📄 Fiche dossier", page_icon="📄", layout="wide")
render_sidebar()
st.title("📄 Fiche dossier")

# ---------------------------------------------------------
# CHARGEMENT BASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.error("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)

# Normalisation Dossier N (support xxxxx-1)
df["Dossier N"] = df["Dossier N"].astype(str)

nums = sorted(df["Dossier N"].unique())
selected = st.selectbox("Sélectionner un dossier", nums)

dossier = df[df["Dossier N"] == selected].iloc[0].to_dict()

# ---------------------------------------------------------
# INFOS GÉNÉRALES
# ---------------------------------------------------------
st.subheader(f"Dossier {dossier['Dossier N']} — {dossier.get('Nom','')}")

c1, c2, c3 = st.columns(3)
c1.write(f"**Catégorie** : {dossier.get('Categories','')}")
c2.write(f"**Sous-catégorie** : {dossier.get('Sous-categories','')}")
c3.write(f"**Visa** : {dossier.get('Visa','')}")

st.markdown("---")

# ---------------------------------------------------------
# FACTURATION & RÈGLEMENTS (MÊME LIGNE)
# ---------------------------------------------------------
st.subheader("💰 Facturation & règlements")

colF, colP = st.columns(2)

with colF:
    honoraires = float(dossier.get("Montant honoraires (US $)", 0))
    frais = float(dossier.get("Autres frais (US $)", 0))
    total_facture = honoraires + frais

    st.metric("Montant honoraires", f"${honoraires:,.2f}")
    st.metric("Autres frais", f"${frais:,.2f}")
    st.metric("Total facturé", f"${total_facture:,.2f}")

with colP:
    total_encaisse = 0.0
    for i in range(1, 5):
        a = float(dossier.get(f"Acompte {i}", 0) or 0)
        total_encaisse += a

        if a > 0:
            st.write(
                f"**Acompte {i}** : ${a:,.2f}  "
                f"({dossier.get('mode de paiement','')})  "
                f"{dossier.get(f'Date Acompte {i}','')}"
            )

    solde = total_facture - total_encaisse
    st.metric("Total encaissé", f"${total_encaisse:,.2f}")
    st.metric("Solde dû", f"${solde:,.2f}")

st.markdown("---")

# ---------------------------------------------------------
# STATUT FINANCIER
# ---------------------------------------------------------
if solde <= 0:
    st.success("✅ Dossier payé")
elif total_encaisse > 0:
    st.warning("🟡 Paiement partiel")
else:
    st.error("🔴 Impayé")

# ---------------------------------------------------------
# ESCROW
# ---------------------------------------------------------
st.subheader("💼 Escrow")

escrow_amount = float(dossier.get("Acompte 1", 0) or 0)

if dossier.get("Escrow"):
    st.info(f"💼 Escrow actif — ${escrow_amount:,.2f}")
elif dossier.get("Escrow_a_reclamer"):
    st.warning(f"📤 Escrow à réclamer — ${escrow_amount:,.2f}")
elif dossier.get("Escrow_reclame"):
    st.success(f"✅ Escrow réclamé — ${escrow_amount:,.2f}")
else:
    st.write("Aucun escrow pour ce dossier.")

# ---------------------------------------------------------
# TIMELINE
# ---------------------------------------------------------
st.markdown("---")
st.subheader("🕓 Timeline du dossier")

timeline = build_timeline(dossier)

if not timeline:
    st.info("Aucun événement enregistré.")
else:
    for ev in timeline:
        line = f"**{ev['date'].date()}** — {ev['label']}"
        if ev.get("amount"):
            line += f" — ${ev['amount']:,.2f}"
        st.markdown(line)

# ---------------------------------------------------------
# EXPORT PDF
# ---------------------------------------------------------
st.markdown("---")
if st.button("📄 Exporter la fiche dossier en PDF"):
    output = f"/tmp/dossier_{dossier['Dossier N']}.pdf"
    export_dossier_pdf(dossier, output)
    with open(output, "rb") as f:
        st.download_button(
            "⬇️ Télécharger le PDF",
            f,
            file_name=f"Dossier_{dossier['Dossier N']}.pdf",
            mime="application/pdf"
        )