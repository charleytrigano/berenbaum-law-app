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

df = pd.DataFrame(clients).copy()

# Normalisation Dossier N (support xxxxx-1)
df["Dossier N"] = df.get("Dossier N", "").astype(str).fillna("").str.strip()

def norm_txt(x):
    return str(x or "").strip()

df["_Nom_norm"] = df.get("Nom", "").apply(norm_txt)
df["_Dossier_norm"] = df["Dossier N"].apply(norm_txt)

# =========================================================
# ✅ RECHERCHE DOSSIER (Nom OU Dossier N)
# =========================================================
st.subheader("🔎 Rechercher un dossier")

search = st.text_input(
    "Recherche (Nom ou Dossier N)",
    value="",
    placeholder="Ex: 12904 ou LUCAS",
)

if search.strip():
    s = search.strip().lower()
    df_filtered = df[
        df["_Nom_norm"].str.lower().str.contains(s, na=False)
        | df["_Dossier_norm"].str.lower().str.contains(s, na=False)
    ].copy()
else:
    df_filtered = df.copy()

df_filtered["_label"] = df_filtered.apply(
    lambda r: f"{norm_txt(r.get('Dossier N'))} — {norm_txt(r.get('Nom'))}",
    axis=1
)

options = df_filtered["_label"].tolist()

if not options:
    st.warning("Aucun dossier ne correspond à la recherche.")
    st.stop()

selected_label = st.selectbox("Sélectionner un dossier", options)

selected = df_filtered[df_filtered["_label"] == selected_label].iloc[0]["Dossier N"]
dossier = df[df["Dossier N"] == str(selected)].iloc[0].to_dict()

# ---------------------------------------------------------
# INFOS GÉNÉRALES
# ---------------------------------------------------------
st.markdown("---")
st.subheader(f"Dossier {dossier.get('Dossier N','')} — {dossier.get('Nom','')}")

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
    honoraires = float(dossier.get("Montant honoraires (US $)", 0) or 0)
    frais = float(dossier.get("Autres frais (US $)", 0) or 0)
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
            mode = dossier.get(f"Mode Acompte {i}", "") or dossier.get("mode de paiement", "")
            date_paiement = dossier.get(f"Date Acompte {i}", "")
            st.write(
                f"**Acompte {i}** : ${a:,.2f}  \n"
                f"Mode : {mode}  \n"
                f"Date : {date_paiement}"
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

if bool(dossier.get("Escrow")):
    st.info(f"💼 Escrow actif — ${escrow_amount:,.2f}")
elif bool(dossier.get("Escrow_a_reclamer")):
    st.warning(f"📤 Escrow à réclamer — ${escrow_amount:,.2f}")
elif bool(dossier.get("Escrow_reclame")):
    st.success(f"✅ Escrow réclamé — ${escrow_amount:,.2f}")
else:
    st.write("Aucun escrow pour ce dossier.")

# ---------------------------------------------------------
# STATUTS (présentation améliorée : valeurs décalées à droite)
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📦 Statuts du dossier")

def yesno(v):
    return "✅ Oui" if str(v).strip().lower() in ["true", "1", "yes", "oui"] or v is True else "❌ Non"

left, right = st.columns([1, 2])

with left:
    st.write("**Dossier envoyé**")
    st.write("**Dossier accepté**")
    st.write("**Dossier refusé**")
    st.write("**Dossier annulé**")
    st.write("**RFE**")

with right:
    st.write(yesno(dossier.get("Dossier envoye", False)))
    st.write(yesno(dossier.get("Dossier accepte", False)))
    st.write(yesno(dossier.get("Dossier refuse", False)))
    st.write(yesno(dossier.get("Dossier Annule", False)))
    st.write(yesno(dossier.get("RFE", False)))

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
st.subheader("📄 Export PDF")

if st.button("📄 Exporter la fiche dossier en PDF", type="primary"):
    output = f"/tmp/dossier_{dossier['Dossier N']}.pdf"
    try:
        export_dossier_pdf(dossier, output)
        with open(output, "rb") as f:
            st.download_button(
                "⬇️ Télécharger le PDF",
                data=f,
                file_name=f"Dossier_{dossier['Dossier N']}.pdf",
                mime="application/pdf"
            )
        st.success("✔ PDF généré avec succès.")
    except Exception as e:
        st.error(f"❌ Erreur export PDF : {e}")