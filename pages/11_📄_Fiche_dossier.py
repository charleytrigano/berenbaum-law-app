import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

# ---------------------------------------------------------
# ⚙️ CONFIGURATION PAGE
# ---------------------------------------------------------
st.set_page_config(page_title="Fiche Dossier", page_icon="📄", layout="wide")

# Style VisionOS
VISIONOS_CARD = """
<style>
.vcard {
    background: rgba(255, 255, 255, 0.25);
    backdrop-filter: blur(16px) saturate(180%);
    -webkit-backdrop-filter: blur(16px) saturate(180%);
    border-radius: 18px;
    border: 1px solid rgba(209, 213, 219, 0.3);
    padding: 20px 25px;
    margin-bottom: 25px;
}
.vbadge {
    display:inline-block;
    padding:6px 12px;
    border-radius:12px;
    font-size:0.8rem;
    font-weight:600;
    margin-right:6px;
}
.bgreen { background: #d1fae5; color:#065f46; }
.byellow { background: #fef9c3; color:#92400e; }
.bred { background:#fee2e2; color:#991b1b; }
.bblue { background:#dbeafe; color:#1e3a8a; }
.bgray { background:#e5e7eb; color:#374151; }
</style>
"""
st.markdown(VISIONOS_CARD, unsafe_allow_html=True)

# ---------------------------------------------------------
# 📥 CHARGEMENT BASE
# ---------------------------------------------------------
db = load_database()
clients = pd.DataFrame(db.get("clients", []))

if clients.empty:
    st.error("Aucun dossier trouvé.")
    st.stop()

# ---------------------------------------------------------
# 🔄 SUPPORT DASHBOARD → FICHE
# ---------------------------------------------------------
if "selected_dossier" in st.session_state:
    preselected = st.session_state["selected_dossier"]
else:
    preselected = None

# ---------------------------------------------------------
# 🧭 SELECTBOX POUR NAVIGATION
# ---------------------------------------------------------
st.title("📄 Fiche dossier")

liste_dossiers = (
    clients["Dossier N"]
    .dropna()
    .astype(int)
    .sort_values()
    .tolist()
)

selected = st.selectbox(
    "Sélectionner un dossier :", 
    liste_dossiers,
    index = liste_dossiers.index(preselected) if preselected in liste_dossiers else 0
)

# Récupération du dossier
d = clients[clients["Dossier N"] == selected].iloc[0]

# ---------------------------------------------------------
# 🏷️ BADGES
# ---------------------------------------------------------
def badge(text, color):
    return f"<span class='vbadge {color}'>{text}</span>"

# Statut principal
if d.get("Dossier envoye"):
    statut = badge("Envoyé", "bblue")
elif d.get("Dossier accepte"):
    statut = badge("Accepté", "bgreen")
elif d.get("Dossier refuse"):
    statut = badge("Refusé", "bred")
else:
    statut = badge("En cours", "bgray")

# Escrow
if d.get("Escrow"):
    escrow_badge = badge("Escrow en cours", "byellow")
elif d.get("Escrow_a_reclamer"):
    escrow_badge = badge("Escrow à réclamer", "bred")
elif d.get("Escrow_reclame"):
    escrow_badge = badge("Escrow réclamé", "bgreen")
else:
    escrow_badge = badge("Pas d'Escrow", "bgray")

# ---------------------------------------------------------
# 🧊 BLOC HEADER
# ---------------------------------------------------------
st.markdown(f"""
<div class='vcard'>
    <h2>📁 Dossier {int(d['Dossier N'])} — {d['Nom']}</h2>
    {statut} {escrow_badge}
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 📌 BLOC INFORMATIONS GÉNÉRALES
# ---------------------------------------------------------
st.markdown("<div class='vcard'>", unsafe_allow_html=True)
st.subheader("📄 Informations générales")
col1, col2, col3 = st.columns(3)
col1.write(f"**Catégorie :** {d.get('Categories','')}")
col2.write(f"**Sous-catégorie :** {d.get('Sous-categories','')}")
col3.write(f"**Visa :** {d.get('Visa','')}")
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 💰 FINANCES
# ---------------------------------------------------------
st.markdown("<div class='vcard'>", unsafe_allow_html=True)
st.subheader("💰 Facturation")

total = float(d.get("Montant honoraires (US $)", 0)) + float(d.get("Autres frais (US $)", 0))

col1, col2, col3 = st.columns(3)
col1.metric("Honoraires", f"${d.get('Montant honoraires (US $)',0):,.0f}")
col2.metric("Autres frais", f"${d.get('Autres frais (US $)',0):,.0f}")
col3.metric("Total", f"${total:,.0f}")

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 🏦 ACOMPTES
# ---------------------------------------------------------
st.markdown("<div class='vcard'>", unsafe_allow_html=True)
st.subheader("🏦 Acomptes")

ac1 = float(d.get("Acompte 1",0))
ac2 = float(d.get("Acompte 2",0))
ac3 = float(d.get("Acompte 3",0))
ac4 = float(d.get("Acompte 4",0))

acomptes_total = ac1+ac2+ac3+ac4
reste = total - acomptes_total

col1, col2, col3 = st.columns(3)
col1.metric("Total acomptes", f"${acomptes_total:,.0f}")
col2.metric("Solde dû", f"${reste:,.0f}")
col3.write("")

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 🔄 TIMELINE STATUS / ESCROW
# ---------------------------------------------------------
st.markdown("<div class='vcard'>", unsafe_allow_html=True)
st.subheader("📅 Suivi du dossier")

st.write(f"**Date envoi :** {d.get('Date envoi','')}")
st.write(f"**Date acceptation :** {d.get('Date acceptation','')}")
st.write(f"**Date refus :** {d.get('Date refus','')}")
st.write(f"**Date annulation :** {d.get('Date annulation','')}")
st.write(f"**Date RFE :** {d.get('Date reclamation','')}")
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 📎 ACTIONS
# ---------------------------------------------------------
from components.export_pdf import export_dossier_pdf

pdf_buffer = export_dossier_pdf(d)

st.download_button(
    label="📄 Télécharger PDF",
    data=pdf_buffer,
    file_name=f"Dossier_{d['Dossier N']}.pdf",
    mime="application/pdf",
    type="primary"
)
