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

# Support des sous-dossiers (xxxxx-1, etc.)
df["Dossier N"] = df["Dossier N"].astype(str)

# ---------------------------------------------------------
# SÉLECTION DOSSIER (N° + NOM)
# ---------------------------------------------------------
df["Label"] = df["Dossier N"] + " — " + df.get("Nom", "").astype(str)

labels = df["Label"].unique().tolist()
selected_label = st.selectbox("Sélectionner un dossier", labels)

selected_row = df[df["Label"] == selected_label].iloc[0]
dossier = selected_row.to_dict()

# ---------------------------------------------------------
# INFOS GÉNÉRALES
# ---------------------------------------------------------
st.subheader(f"Dossier {dossier.get('Dossier N')} — {dossier.get('Nom','')}")

c1, c2, c3 = st.columns(3)
c1.write(f"**Catégorie** : {dossier.get('Categories','')}")
c2.write(f"**Sous-catégorie** : {dossier.get('Sous-categories','')}")
c3.write(f"**Visa** : {dossier.get('Visa','')}")

st.markdown("---")

# ---------------------------------------------------------
# FACTURATION & RÈGLEMENTS
# ---------------------------------------------------------
st.subheader("💰 Facturation & règlements")

colF, colP = st.columns(2)

with colF:
    honoraires = float(dossier.get("Montant honoraires (US $)", 0) or 0)
    frais = float(dossier.get("Autres frais (US $)", 0) or 0)
    total_facture = honoraires + frais

    st.metric("Montant honoraires", f"${honoraires:,.2f}")
    st.metric("Autres frais", f"${frais:,.2f}")
    st.metric("Total facturé", f"${total_facture:,.2f}")

with colP:
    total_encaisse = 0.0
    paiements = []

    for i in range(1, 5):
        montant = float(dossier.get(f"Acompte {i}", 0) or 0)
        date_p = dossier.get(f"Date Acompte {i}", "")
        mode = dossier.get(f"Mode Acompte {i}", dossier.get("mode de paiement", ""))

        if montant > 0:
            paiements.append([
                f"Acompte {i}",
                f"${montant:,.2f}",
                date_p,
                mode
            ])
            total_encaisse += montant

    if paiements:
        st.markdown("**Paiements encaissés**")
        st.dataframe(
            pd.DataFrame(
                paiements,
                columns=["Acompte", "Montant", "Date de paiement", "Mode"]
            ),
            hide_index=True,
            use_container_width=True
        )

    solde = total_facture - total_encaisse
    st.metric("Total encaissé", f"${total_encaisse:,.2f}")
    st.metric("Solde dû", f"${solde:,.2f}")

st.markdown("---")

# ---------------------------------------------------------
# STATUT FINANCIER
# ---------------------------------------------------------
if solde <= 0:
    st.success("✅ Dossier soldé")
elif total_encaisse > 0:
    st.warning("🟡 Paiement partiel")
else:
    st.error("🔴 Aucun paiement enregistré")

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
# 📦 STATUTS DU DOSSIER (TABLEAU ALIGNÉ)
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📦 Statuts du dossier")

def yesno(v):
    return "✅ Oui" if str(v).strip().lower() in ["true", "1", "yes", "oui"] or v is True else "❌ Non"

statuts_rows = [
    ("Dossier envoyé", yesno(dossier.get("Dossier envoye", False))),
    ("Dossier accepté", yesno(dossier.get("Dossier accepte", False))),
    ("Dossier refusé", yesno(dossier.get("Dossier refuse", False))),
    ("Dossier annulé", yesno(dossier.get("Dossier Annule", False))),
    ("RFE", yesno(dossier.get("RFE", False))),
]

st.dataframe(
    pd.DataFrame(statuts_rows, columns=["Statut", "Valeur"]),
    hide_index=True,
    use_container_width=True
)

# ---------------------------------------------------------
# 🕓 TIMELINE
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
# 📝 COMMENTAIRE
# ---------------------------------------------------------
commentaire = dossier.get("Commentaire", "")
if str(commentaire).strip():
    st.markdown("---")
    st.subheader("📝 Commentaire")
    st.write(commentaire)

# ---------------------------------------------------------
# 📄 EXPORT PDF
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