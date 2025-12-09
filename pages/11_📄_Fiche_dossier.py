import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database
from components.export_pdf import export_dossier_pdf


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="Fiche Dossier", page_icon="📄", layout="wide")


# ---------------------------------------------------------
# STYLES VISIONOS PREMIUM
# ---------------------------------------------------------
VISIONOS_CSS = """
<style>

.vcard {
    background: rgba(255, 255, 255, 0.35);
    backdrop-filter: blur(16px) saturate(180%);
    -webkit-backdrop-filter: blur(16px) saturate(180%);
    border-radius: 18px;
    border: 1px solid rgba(209, 213, 219, 0.32);
    padding: 22px 28px;
    margin-bottom: 25px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.06);
}

/* BADGES */
.vbadge {
    display:inline-block;
    padding:6px 12px;
    border-radius:12px;
    font-size:0.78rem;
    font-weight:600;
    margin-right:6px;
}
.bgreen { background:#d1fae5; color:#065f46; }
.byellow { background:#fef9c3; color:#92400e; }
.bred { background:#fee2e2; color:#991b1b; }
.bblue { background:#dbeafe; color:#1e3a8a; }
.bgray { background:#e5e7eb; color:#374151; }

/* TIMELINE CONTAINER */
.timeline-container {
    display: flex;
    gap: 40px;
    flex-wrap: wrap;
}

/* TIMELINE BOX */
.timeline-box {
    background: rgba(255,255,255,0.55);
    backdrop-filter: blur(15px);
    padding: 22px;
    border-radius: 18px;
    width: 45%;
    min-width: 300px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.08);
}

/* VERTICAL TIMELINE */
.timeline {
    border-left: 2px solid rgba(180,180,180,0.35);
    margin-left: 20px;
    padding-left: 12px;
    position: relative;
}

/* ANIMATED FLOW */
.timeline:after {
    content: "";
    position: absolute;
    left: -2px;
    top: 0;
    width: 2px;
    height: 100%;
    background: linear-gradient(rgba(255,255,255,0), rgba(0,122,255,0.4), rgba(255,255,255,0));
    animation: flow 3s linear infinite;
}
@keyframes flow {
    0% { transform: translateY(-100%); }
    100% { transform: translateY(100%); }
}

/* EVENT */
.event {
    position: relative;
    margin-bottom: 26px;
}

/* DOT */
.event:before {
    content: "";
    position: absolute;
    left: -18px;
    top: 4px;
    width: 14px;
    height: 14px;
    background: rgba(255,255,255,0.9);
    border-radius: 50%;
    border: 2px solid rgba(150,150,150,0.5);
    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}

/* COLORED DOTS */
.dot-green { border-color:#059669 !important; }
.dot-red { border-color:#DC2626 !important; }
.dot-blue { border-color:#2563EB !important; }
.dot-yellow { border-color:#CA8A04 !important; }
.dot-gray { border-color:#6B7280 !important; }

/* TITLES */
.event-title {
    font-weight: 600;
    font-size: 15px;
    color: #1F2937;
}

/* DATES */
.event-date {
    font-size: 13px;
    color: #6B7280;
}

</style>
"""
st.markdown(VISIONOS_CSS, unsafe_allow_html=True)



# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = pd.DataFrame(db.get("clients", []))

if clients.empty:
    st.error("Aucun dossier trouvé.")
    st.stop()


# ---------------------------------------------------------
# READ SELECTED DOSSIER (Dashboard → Fiche)
# ---------------------------------------------------------
if "selected_dossier" in st.session_state:
    selected_initial = st.session_state["selected_dossier"]
else:
    selected_initial = None


# ---------------------------------------------------------
# SELECTBOX DOSSIERS
# ---------------------------------------------------------
st.title("📄 Fiche dossier")

liste = clients["Dossier N"].dropna().astype(int).sort_values().tolist()

selected = st.selectbox(
    "Sélectionner un dossier :",
    liste,
    index = liste.index(selected_initial) if selected_initial in liste else 0
)

d = clients[clients["Dossier N"] == selected].iloc[0]


# ---------------------------------------------------------
# BADGES — STATUT + ESCROW
# ---------------------------------------------------------
def badge(text, color):
    return f"<span class='vbadge {color}'>{text}</span>"


# Statut dossier
if d.get("Dossier envoye"):
    statut = badge("Envoyé", "bblue")
elif d.get("Dossier accepte"):
    statut = badge("Accepté", "bgreen")
elif d.get("Dossier refuse"):
    statut = badge("Refusé", "bred")
else:
    statut = badge("En cours", "bgray")

# Statut Escrow
if d.get("Escrow"):
    escrow_badge = badge("Escrow en cours", "byellow")
elif d.get("Escrow_a_reclamer"):
    escrow_badge = badge("Escrow à réclamer", "bred")
elif d.get("Escrow_reclame"):
    escrow_badge = badge("Escrow réclamé", "bgreen")
else:
    escrow_badge = badge("Pas d'Escrow", "bgray")



# ---------------------------------------------------------
# HEADER VISIONOS
# ---------------------------------------------------------
st.markdown(f"""
<div class='vcard'>
    <h2>📁 Dossier {int(d['Dossier N'])} — {d['Nom']}</h2>
    {statut} {escrow_badge}
</div>
""", unsafe_allow_html=True)



# ---------------------------------------------------------
# INFO GÉNÉRALES
# ---------------------------------------------------------
st.markdown("<div class='vcard'>", unsafe_allow_html=True)
st.subheader("📄 Informations générales")

col1, col2, col3 = st.columns(3)
col1.write(f"**Catégorie :** {d.get('Categories','')}")
col2.write(f"**Sous-catégorie :** {d.get('Sous-categories','')}")
col3.write(f"**Visa :** {d.get('Visa','')}")

st.markdown("</div>", unsafe_allow_html=True)



# ---------------------------------------------------------
# FACTURATION
# ---------------------------------------------------------
st.markdown("<div class='vcard'>", unsafe_allow_html=True)
st.subheader("💰 Facturation")

hon = float(d.get("Montant honoraires (US $)", 0))
frais = float(d.get("Autres frais (US $)", 0))
total = hon + frais

c1, c2, c3 = st.columns(3)
c1.metric("Honoraires", f"${hon:,.0f}")
c2.metric("Autres frais", f"${frais:,.0f}")
c3.metric("Total facturé", f"${total:,.0f}")

st.markdown("</div>", unsafe_allow_html=True)



# ---------------------------------------------------------
# ACOMPTES
# ---------------------------------------------------------
st.markdown("<div class='vcard'>", unsafe_allow_html=True)
st.subheader("🏦 Acomptes")

ac1 = float(d.get("Acompte 1",0))
ac2 = float(d.get("Acompte 2",0))
ac3 = float(d.get("Acompte 3",0))
ac4 = float(d.get("Acompte 4",0))
tot_ac = ac1 + ac2 + ac3 + ac4
solde = total - tot_ac

c1, c2, c3 = st.columns(3)
c1.metric("Total acomptes", f"${tot_ac:,.0f}")
c2.metric("Solde dû", f"${solde:,.0f}")
c3.write("")

st.markdown("</div>", unsafe_allow_html=True)



# ---------------------------------------------------------
# TIMELINES (DOSSIER + ESCROW)
# ---------------------------------------------------------

# Build timeline events
timeline_dossier = []
timeline_escrow = []

def add_ev(lst, label, date, icon, dot):
    if date not in ["", None, "None", ""]:
        lst.append((label, date, icon, dot))

# Dossier timeline
add_ev(timeline_dossier, "Dossier créé", d.get("Date"), "📄", "dot-blue")
add_ev(timeline_dossier, "Envoyé", d.get("Date envoi"), "📨", "dot-blue")
add_ev(timeline_dossier, "Accepté", d.get("Date acceptation"), "✅", "dot-green")
add_ev(timeline_dossier, "Refusé", d.get("Date refus"), "❌", "dot-red")
add_ev(timeline_dossier, "Annulé", d.get("Date annulation"), "🚫", "dot-gray")
add_ev(timeline_dossier, "RFE", d.get("Date reclamation"), "📬", "dot-yellow")

# Escrow timeline
if d.get("Escrow"):
    add_ev(timeline_escrow, "Escrow ouvert", d.get("Date"), "💰", "dot-yellow")
if d.get("Escrow_a_reclamer"):
    add_ev(timeline_escrow, "Escrow à réclamer", d.get("Date envoi"), "⚠️", "dot-red")
if d.get("Escrow_reclame"):
    add_ev(timeline_escrow, "Escrow réclamé", d.get("Date acceptation"), "🟢", "dot-green")


# Render timelines
st.markdown("<div class='timeline-container'>", unsafe_allow_html=True)


# === TIMELINE DOSSIER ===
st.markdown("<div class='timeline-box'>", unsafe_allow_html=True)
st.subheader("📁 Timeline du dossier")

html = "<div class='timeline'>"
for label, date, icon, dot in timeline_dossier:
    html += f"""
    <div class='event {dot}'>
        <div class='event-title'>{icon} {label}</div>
        <div class='event-date'>{date}</div>
    </div>
    """
html += "</div>"

st.markdown(html, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)


# === TIMELINE ESCROW ===
st.markdown("<div class='timeline-box'>", unsafe_allow_html=True)
st.subheader("💰 Timeline Escrow")

html = "<div class='timeline'>"
for label, date, icon, dot in timeline_escrow:
    html += f"""
    <div class='event {dot}'>
        <div class='event-title'>{icon} {label}</div>
        <div class='event-date'>{date}</div>
    </div>
    """
html += "</div>"

st.markdown(html, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)


st.markdown("</div>", unsafe_allow_html=True)



# ---------------------------------------------------------
# ACTIONS (incl. PDF EXPORT)
# ---------------------------------------------------------
st.markdown("<div class='vcard'>", unsafe_allow_html=True)
st.subheader("⚙️ Actions")

pdf = export_dossier_pdf(d)

st.download_button(
    "📄 Télécharger PDF",
    data=pdf,
    file_name=f"Dossier_{d['Dossier N']}.pdf",
    mime="application/pdf",
    type="primary"
)

st.markdown("</div>", unsafe_allow_html=True)
