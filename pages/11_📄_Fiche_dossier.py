import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

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


# -------------------------------------------------------------------
# 🧩 SELECTION DOSSIER
# -------------------------------------------------------------------
selected = st.selectbox("Sélectionner un dossier", nums)
row = df[df["Dossier N"] == selected].iloc[0]


# -------------------------------------------------------------------
# 🌗 CSS DARK-MODE FRIENDLY
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
        .event {
            margin-bottom: 15px;
        }
        .event-title {
            font-weight: 600;
            color: #4FA3FF;
        }
        .event-date {
            font-size: 13px;
            opacity: 0.8;
            margin-left: 4px;
        }
        .field-label {
            opacity: .7;
            font-size: 13px;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# 🧾 CARTE — INFOS GÉNÉRALES
# -------------------------------------------------------------------
st.markdown("<h3>📌 Informations générales</h3>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("**Nom :**", row.get("Nom",""))
    st.write("**Dossier N° :**", int(row["Dossier N"]))
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("**Catégorie :**", row.get("Categories",""))
    st.write("**Sous-catégorie :**", row.get("Sous-categories",""))
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("**Visa :**", row.get("Visa",""))
    st.write("**Date création :**", row.get("Date",""))
    st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------------------------
# 💰 CARTE — FINANCES
# -------------------------------------------------------------------
st.markdown("<h3>💰 Facturation</h3>", unsafe_allow_html=True)

colA, colB, colC = st.columns(3)
with colA:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("**Honoraires :** $", row.get("Montant honoraires (US $)",0))
    st.write("**Autres frais :** $", row.get("Autres frais (US $)",0))
    st.markdown("</div>", unsafe_allow_html=True)

with colB:
    total = float(row.get("Montant honoraires (US $)",0)) + float(row.get("Autres frais (US $)",0))
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("**Total facturé :** $", total)
    st.write("**Mode paiement :**", row.get("mode de paiement",""))
    st.markdown("</div>", unsafe_allow_html=True)

with colC:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("**Acompte 1 :**", row.get("Acompte 1",""))
    st.write("**Acompte 2 :**", row.get("Acompte 2",""))
    st.write("**Acompte 3 :**", row.get("Acompte 3",""))
    st.write("**Acompte 4 :**", row.get("Acompte 4",""))
    st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------------------------
# 🕓 TIMELINE DU DOSSIER
# -------------------------------------------------------------------
st.markdown("<h3>🕓 Timeline du dossier</h3>", unsafe_allow_html=True)
st.markdown("<div class='timeline'>", unsafe_allow_html=True)

# 🔹 Création du dossier
st.markdown(f"""
<div class='event'>
    <div class='event-title'>📄 Dossier créé</div>
    <div class='event-date'>{row.get("Date","")}</div>
</div>
""", unsafe_allow_html=True)

# 🔹 Escrow ouvert
if row.get("Escrow", False):
    st.markdown(f"""
    <div class='event'>
        <div class='event-title'>💰 Escrow ouvert</div>
        <div class='event-date'>{row.get("Date","")}</div>
    </div>
    """, unsafe_allow_html=True)

# 🔹 Dossier envoyé
if row.get("Dossier envoye", False):
    st.markdown(f"""
    <div class='event'>
        <div class='event-title'>✈️ Dossier envoyé</div>
        <div class='event-date'>{row.get("Date envoi","")}</div>
    </div>
    """, unsafe_allow_html=True)

# 🔹 Accepté
if row.get("Dossier accepte", False):
    st.markdown(f"""
    <div class='event'>
        <div class='event-title'>✅ Accepté</div>
        <div class='event-date'>{row.get("Date acceptation","")}</div>
    </div>
    """, unsafe_allow_html=True)

# 🔹 Refusé
if row.get("Dossier refuse", False):
    st.markdown(f"""
    <div class='event'>
        <div class='event-title'>❌ Refusé</div>
        <div class='event-date'>{row.get("Date refus","")}</div>
    </div>
    """, unsafe_allow_html=True)

# 🔹 RFE
if row.get("RFE", False):
    st.markdown(f"""
    <div class='event'>
        <div class='event-title'>📩 RFE reçue</div>
        <div class='event-date'>{row.get("Date reclamation","")}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------------------------
# 📤 EXPORT PDF (placeholder)
# -------------------------------------------------------------------
st.markdown("### 📄 Export PDF")
st.info("📌 Le bouton Export PDF sera ajouté dans la prochaine version.")


