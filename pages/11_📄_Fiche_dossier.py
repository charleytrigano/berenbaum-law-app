import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tempfile
import os

# -------------------------------------------------------------------
# ⚙ CONFIG
# -------------------------------------------------------------------
st.set_page_config(page_title="📄 Fiche dossier", page_icon="📄", layout="wide")
st.title("📄 Fiche dossier")

# -------------------------------------------------------------------
# 📂 CHARGEMENT DATABASE
# -------------------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.error("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)

# -------------------------------------------------------------------
# 🛠 NORMALISATION NUMÉROS
# -------------------------------------------------------------------
df["Dossier N"] = pd.to_numeric(df["Dossier N"], errors="coerce")
nums = sorted(df["Dossier N"].dropna().astype(int).unique())

if not nums:
    st.error("Aucun numéro de dossier valide.")
    st.stop()

selected = st.selectbox("Sélectionner un dossier", nums)
row = df[df["Dossier N"] == selected].iloc[0]

# -------------------------------------------------------------------
# 🌗 CSS Style premium mode sombre
# -------------------------------------------------------------------
st.markdown("""
    <style>
        .card {
            background-color: rgba(255,255,255,0.07);
            padding: 18px;
            border-radius: 12px;
            margin-bottom: 10px;
            border: 1px solid rgba(255,255,255,0.15);
        }
        .timeline {
            border-left: 2px solid #888;
            padding-left: 20px;
            margin-top: 20px;
        }
        .event-title {
            font-weight: 600;
            color: #4FA3FF;
        }
        .event-date {
            font-size: 13px;
            opacity: 0.8;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# 🧾 FONCTION EXPORT PDF
# -------------------------------------------------------------------
def export_pdf(d):
    """Crée un PDF dans un fichier temporaire et retourne son chemin."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(tmp.name, pagesize=letter)
    width, height = letter

    y = height - 50
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, f"Dossier {int(d['Dossier N'])} — {d['Nom']}")
    y -= 40

    c.setFont("Helvetica", 12)

    def add_line(label, value):
        nonlocal y
        c.drawString(50, y, f"{label}: {value}")
        y -= 20

    for k, v in d.items():
        add_line(k, v)

    c.save()
    return tmp.name

# -------------------------------------------------------------------
# 🧾 BOUTONS ACTIONS
# -------------------------------------------------------------------
colA, colB, colC = st.columns(3)

# EXPORT PDF
if colA.button("📄 Exporter en PDF"):
    pdf_path = export_pdf(row)
    with open(pdf_path, "rb") as f:
        st.download_button("⬇️ Télécharger le PDF", f, file_name=f"dossier_{selected}.pdf")
    os.unlink(pdf_path)

# MODIFIER
if colB.button("✏️ Modifier ce dossier"):
    st.query_params["dossier"] = selected
    st.switch_page("pages/03_✏️_Modifier_dossier.py")

# SUPPRIMER
if colC.button("🗑️ Supprimer ce dossier"):
    st.session_state["confirm_delete"] = True

# POPUP CONFIRMATION
if st.session_state.get("confirm_delete", False):
    st.error("⚠️ Confirmer la suppression ? Cette action est irréversible.")
    c1, c2 = st.columns(2)

    if c1.button("❌ Oui, supprimer définitivement"):
        df = df[df["Dossier N"] != selected]
        db["clients"] = df.to_dict(orient="records")
        save_database(db)
        st.success("✔️ Dossier supprimé.")
        st.session_state["confirm_delete"] = False
        st.rerun()

    if c2.button("Annuler"):
        st.session_state["confirm_delete"] = False

# -------------------------------------------------------------------
# 📌 Informations affichées
# -------------------------------------------------------------------
st.markdown("<h3>📌 Informations générales</h3>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("**Nom :**", row.get("Nom", ""))
    st.write("**Dossier N° :**", int(row["Dossier N"]))
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("**Catégorie :**", row.get("Categories", ""))
    st.write("**Sous-catégorie :**", row.get("Sous-categories", ""))
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("**Visa :**", row.get("Visa", ""))
    st.write("**Date création :**", row.get("Date", ""))
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------------
# 💰 FACTURATION
# -------------------------------------------------------------------
st.markdown("<h3>💰 Facturation</h3>", unsafe_allow_html=True)

colF1, colF2, colF3 = st.columns(3)
with colF1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("**Honoraires :** $", row.get("Montant honoraires (US $)", 0))
    st.write("**Autres frais :** $", row.get("Autres frais (US $)", 0))
    st.markdown("</div>", unsafe_allow_html=True)

with colF2:
    total = float(row.get("Montant honoraires (US $)", 0)) + float(row.get("Autres frais (US $)", 0))
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("**Total facturé :** $", total)
    st.write("**Mode paiement :**", row.get("mode de paiement", ""))
    st.markdown("</div>", unsafe_allow_html=True)

with colF3:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("**Acompte 1 :**", row.get("Acompte 1", ""))
    st.write("**Acompte 2 :**", row.get("Acompte 2", ""))
    st.write("**Acompte 3 :**", row.get("Acompte 3", ""))
    st.write("**Acompte 4 :**", row.get("Acompte 4", ""))
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------------
# 🕓 TIMELINE
# -------------------------------------------------------------------
st.markdown("<h3>🕓 Timeline du dossier</h3>", unsafe_allow_html=True)
st.markdown("<div class='timeline'>", unsafe_allow_html=True)

# Dossier créé
st.markdown(f"""
<div class='event'>
    <div class='event-title'>📄 Dossier créé</div>
    <div class='event-date'>{row.get("Date","")}</div>
</div>
""", unsafe_allow_html=True)

if row.get("Escrow", False):
    st.markdown(f"""
    <div class='event'>
        <div class='event-title'>💰 Escrow ouvert</div>
        <div class='event-date'>{row.get("Date","")}</div>
    </div>
    """, unsafe_allow_html=True)

if row.get("Dossier envoye", False):
    st.markdown(f"""
    <div class='event'>
        <div class='event-title'>✈️ Dossier envoyé</div>
        <div class='event-date'>{row.get("Date envoi","")}</div>
    </div>
    """, unsafe_allow_html=True)

if row.get("Dossier accepte", False):
    st.markdown(f"""
    <div class='event'>
        <div class='event-title'>✅ Accepté</div>
        <div class='event-date'>{row.get("Date acceptation","")}</div>
    </div>
    """, unsafe_allow_html=True)

if row.get("Dossier refuse", False):
    st.markdown(f"""
    <div class='event'>
        <div class='event-title'>❌ Refusé</div>
        <div class='event-date'>{row.get("Date refus","")}</div>
    </div>
    """, unsafe_allow_html=True)

if row.get("RFE", False):
    st.markdown(f"""
    <div class='event'>
        <div class='event-title'>📩 RFE reçue</div>
        <div class='event-date'>{row.get("Date reclamation","")}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
