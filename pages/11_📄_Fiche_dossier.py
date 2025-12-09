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
# 🌗 CSS STYLE (MODE SOMBRE)
# -------------------------------------------------------------------
st.markdown("""
    <style>
        .card {
            background-color: rgba(40,40,40,0.5);
            padding: 18px;
            border-radius: 12px;
            margin-bottom: 12px;
            border: 1px solid rgba(255,255,255,0.08);
        }
        .timeline {
            border-left: 3px solid #6ea8fe;
            padding-left: 20px;
            margin-top: 20px;
        }
        .event-title {
            font-weight: 600;
            color: #6ea8fe;
        }
        .event-date {
            font-size: 13px;
            opacity: 0.8;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# 🧾 EXPORT PDF
# -------------------------------------------------------------------
def export_pdf(d):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(tmp.name, pagesize=letter)
    width, height = letter

    y = height - 50
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, f"Dossier {int(d['Dossier N'])} — {d['Nom']}")
    y -= 40

    c.setFont("Helvetica", 12)

    def add(label, value):
        nonlocal y
        c.drawString(50, y, f"{label}: {value}")
        y -= 20

    for k, v in d.items():
        add(k, v)

    c.save()
    return tmp.name

# -------------------------------------------------------------------
# 🧾 BOUTONS ACTIONS
# -------------------------------------------------------------------
colA, colB, colC = st.columns(3)

if colA.button("📄 Exporter en PDF"):
    pdf_path = export_pdf(row)
    with open(pdf_path, "rb") as f:
        st.download_button("⬇️ Télécharger le PDF", f, file_name=f"dossier_{selected}.pdf")
    os.unlink(pdf_path)

if colB.button("✏️ Modifier ce dossier"):
    st.query_params["dossier"] = selected
    st.switch_page("pages/03_✏️_Modifier_dossier.py")

if colC.button("🗑️ Supprimer ce dossier"):
    st.session_state["confirm_delete"] = True

if st.session_state.get("confirm_delete", False):
    st.error("⚠️ Confirmer la suppression du dossier ? Action irréversible.")
    cc1, cc2 = st.columns(2)

    if cc1.button("❌ Oui, supprimer définitivement"):
        df = df[df["Dossier N"] != selected]
        db["clients"] = df.to_dict(orient="records")
        save_database(db)
        st.success("✔ Dossier supprimé.")
        st.session_state["confirm_delete"] = False
        st.rerun()

    if cc2.button("Annuler"):
        st.session_state["confirm_delete"] = False

# -------------------------------------------------------------------
# 📌 Informations générales
# -------------------------------------------------------------------
st.markdown("## 📌 Informations générales")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("**Client :**", row.get("Nom"))
    st.write("**Dossier N° :**", int(row["Dossier N"]))
    st.write("**Créé le :**", row.get("Date"))
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("**Catégorie :**", row.get("Categories", ""))
    st.write("**Sous-catégorie :**", row.get("Sous-categories", ""))
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("**Visa :**", row.get("Visa", ""))
    st.write("**Mode de règlement :** Dernier acompte", "")
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------------
# 💰 Facturation & Acomptes
# -------------------------------------------------------------------
st.markdown("## 💰 Facturation")

colF1, colF2, colF3 = st.columns(3)

with colF1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("**Honoraires :** $", row.get("Montant honoraires (US $)", 0))
    st.write("**Autres frais :** $", row.get("Autres frais (US $)", 0))
    total = float(row.get("Montant honoraires (US $)", 0)) + float(row.get("Autres frais (US $)", 0))
    st.write("**Total facturé :** $", total)
    st.markdown("</div>", unsafe_allow_html=True)

with colF3:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("### 🏦 Acomptes")

    for i in range(1, 5):
        st.write(f"**Acompte {i} :**", row.get(f"Acompte {i}", 0))
        st.write(f"Mode :** {row.get(f'Mode Acompte {i}', '')}")
        st.write(f"Date :** {row.get(f'Date Paiement {i}', '')}")
        st.markdown("---")

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------------
# 🕓 TIMELINE
# -------------------------------------------------------------------
st.markdown("## 🕓 Timeline du dossier")
st.markdown("<div class='timeline'>", unsafe_allow_html=True)

# Création
st.markdown(f"""
<div class='event'>
  <div class='event-title'>📄 Dossier créé</div>
  <div class='event-date'>{row.get("Date","")}</div>
</div>
""", unsafe_allow_html=True)

# Escrow ouvert
if row.get("Escrow", False):
    st.markdown(f"""
    <div class='event'>
      <div class='event-title'>💰 Escrow ouvert</div>
      <div class='event-date'>{row.get("Date","")}</div>
    </div>
    """, unsafe_allow_html=True)

# Acomptes
for i in range(1, 4 + 1):
    if float(row.get(f"Acompte {i}", 0)) > 0:
        st.markdown(f"""
        <div class='event'>
          <div class='event-title'>💳 Paiement Acompte {i} — {row.get(f"Mode Acompte {i}", "")}</div>
          <div class='event-date'>{row.get(f"Date Paiement {i}", "")}</div>
        </div>
        """, unsafe_allow_html=True)

# Envoi
if row.get("Dossier envoye", False):
    st.markdown(f"""
<div class='event'>
  <div class='event-title'>✈️ Dossier envoyé</div>
  <div class='event-date'>{row.get("Date envoi","")}</div>
</div>
""", unsafe_allow_html=True)

# Acceptation
if row.get("Dossier accepte", False):
    st.markdown(f"""
<div class='event'>
  <div class='event-title'>✅ Accepté</div>
  <div class='event-date'>{row.get("Date acceptation","")}</div>
</div>
""", unsafe_allow_html=True)

# Refus
if row.get("Dossier refuse", False):
    st.markdown(f"""
<div class='event'>
  <div class='event-title'>❌ Refusé</div>
  <div class='event-date'>{row.get("Date refus","")}</div>
</div>
""", unsafe_allow_html=True)

# RFE
if row.get("RFE", False):
    st.markdown(f"""
<div class='event'>
  <div class='event-title'>📩 RFE reçue</div>
  <div class='event-date'>{row.get("Date reclamation","")}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
