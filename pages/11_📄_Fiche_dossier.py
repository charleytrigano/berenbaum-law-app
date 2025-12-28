# pages/11_📄_Fiche_dossier.py
import streamlit as st
import pandas as pd
from io import BytesIO

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database
from utils.timeline_builder import build_timeline
from utils.pdf_export import export_dossier_pdf


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def to_float(v):
    try:
        return float(v or 0)
    except Exception:
        return 0.0


def to_bool(v):
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    return s in ["true", "1", "1.0", "yes", "oui", "y", "vrai"]


def safe_str(v):
    if v is None:
        return ""
    return str(v)


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
if "Dossier N" not in df.columns:
    st.error("Colonne 'Dossier N' introuvable dans la base.")
    st.stop()

df["Dossier N"] = df["Dossier N"].astype(str)
nums = sorted(df["Dossier N"].unique())

selected = st.selectbox("Sélectionner un dossier", nums)
dossier = df[df["Dossier N"] == selected].iloc[0].to_dict()

# ---------------------------------------------------------
# INFOS GÉNÉRALES
# ---------------------------------------------------------
st.subheader(f"Dossier {safe_str(dossier.get('Dossier N',''))} — {safe_str(dossier.get('Nom',''))}")

c1, c2, c3 = st.columns(3)
c1.write(f"**Catégorie** : {safe_str(dossier.get('Categories',''))}")
c2.write(f"**Sous-catégorie** : {safe_str(dossier.get('Sous-categories',''))}")
c3.write(f"**Visa** : {safe_str(dossier.get('Visa',''))}")

st.markdown("---")

# ---------------------------------------------------------
# FACTURATION & RÈGLEMENTS (MÊME LIGNE)
# ---------------------------------------------------------
st.subheader("💰 Facturation & règlements")

colF, colP = st.columns(2)

with colF:
    honoraires = to_float(dossier.get("Montant honoraires (US $)", 0))
    frais = to_float(dossier.get("Autres frais (US $)", 0))
    total_facture = honoraires + frais

    st.metric("Montant honoraires", f"${honoraires:,.2f}")
    st.metric("Autres frais", f"${frais:,.2f}")
    st.metric("Total facturé", f"${total_facture:,.2f}")

with colP:
    total_encaisse = 0.0

    # Affichage acomptes détaillés si présents :
    # - Montant: Acompte i
    # - Date: Date Acompte i (fallback Date Paiement i si existant)
    # - Mode: Mode Acompte i (fallback mode de paiement)
    for i in range(1, 5):
        a = to_float(dossier.get(f"Acompte {i}", 0))
        total_encaisse += a

        if a > 0:
            mode = dossier.get(f"Mode Acompte {i}", dossier.get("mode de paiement", ""))
            date_paiement = dossier.get(
                f"Date Acompte {i}",
                dossier.get(f"Date Paiement {i}", "")
            )

            st.write(
                f"**Acompte {i}** : ${a:,.2f}  "
                f"— Mode: {safe_str(mode)}  "
                f"— Date: {safe_str(date_paiement)}"
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

escrow_amount = to_float(dossier.get("Acompte 1", 0))

escrow_actif = to_bool(dossier.get("Escrow", False))
escrow_a_reclamer = to_bool(dossier.get("Escrow_a_reclamer", False))
escrow_reclame = to_bool(dossier.get("Escrow_reclame", False))

if escrow_actif:
    st.info(f"💼 Escrow actif — ${escrow_amount:,.2f}")
elif escrow_a_reclamer:
    st.warning(f"📤 Escrow à réclamer — ${escrow_amount:,.2f}")
elif escrow_reclame:
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
        d = ev.get("date")
        label = ev.get("label", "")
        amount = ev.get("amount", None)

        # d peut être Timestamp/datetime/date/string
        try:
            d_str = pd.to_datetime(d, errors="coerce")
            if pd.isna(d_str):
                d_out = safe_str(d)
            else:
                d_out = d_str.date().isoformat()
        except Exception:
            d_out = safe_str(d)

        line = f"**{d_out}** — {label}"
        if amount is not None:
            try:
                line += f" — ${float(amount):,.2f}"
            except Exception:
                pass
        st.markdown(line)

# ---------------------------------------------------------
# EXPORT PDF
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📄 Export PDF")

if st.button("📄 Exporter la fiche dossier en PDF", type="primary"):
    # Export robuste: BytesIO (pas d'écriture disque)
    pdf_buffer = BytesIO()

    # Compat: certaines versions export_dossier_pdf écrivent dans un buffer,
    # d'autres retournent directement des bytes.
    try:
        result = export_dossier_pdf(dossier, pdf_buffer)
        if isinstance(result, (bytes, bytearray)):
            pdf_bytes = bytes(result)
        else:
            pdf_bytes = pdf_buffer.getvalue()
    except TypeError:
        # fallback si la fonction ne prend qu'un paramètre (dossier)
        pdf_bytes = export_dossier_pdf(dossier)

    if not pdf_bytes:
        st.error("❌ Export PDF impossible : aucun contenu généré.")
    else:
        st.download_button(
            "⬇️ Télécharger le PDF",
            data=pdf_bytes,
            file_name=f"Dossier_{safe_str(dossier.get('Dossier N',''))}.pdf",
            mime="application/pdf",
        )