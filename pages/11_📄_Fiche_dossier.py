import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

st.set_page_config(page_title="📄 Fiche dossier", page_icon="🗂️", layout="wide")

# -------------------------------
# LOAD DB
# -------------------------------
db = load_database()
df = pd.DataFrame(db.get("clients", []))

if df.empty:
    st.error("Aucun dossier trouvé.")
    st.stop()


# -------------------------------
# THEME DETECTION (Dark / Light)
# -------------------------------
try:
    theme = st.get_option("theme.base")
except:
    theme = "light"

DARK = theme == "dark"

if DARK:
    V_BG = "rgba(30,30,30,0.45)"
    V_BORDER = "rgba(255,255,255,0.10)"
    V_TEXT = "#F9FAFB"
    V_TEXT_SOFT = "#9CA3AF"
    V_SHADOW = "rgba(0,0,0,0.6)"
else:
    V_BG = "rgba(255,255,255,0.35)"
    V_BORDER = "rgba(0,0,0,0.12)"
    V_TEXT = "#1F2937"
    V_TEXT_SOFT = "#6B7280"
    V_SHADOW = "rgba(0,0,0,0.1)"


# -------------------------------
# CSS VisionOS (Dark + Light)
# -------------------------------
st.markdown(
    f"""
<style>

.vcard {{
    background: {V_BG};
    backdrop-filter: blur(18px) saturate(180%);
    -webkit-backdrop-filter: blur(18px) saturate(180%);
    border-radius: 18px;
    border: 1px solid {V_BORDER};
    padding: 26px;
    margin-bottom: 28px;
    box-shadow: 0 8px 24px {V_SHADOW};
    color: {V_TEXT};
}}

.vtitle {{
    font-size: 1.4rem;
    font-weight: 700;
    color: {V_TEXT};
}}

.vlabel {{
    font-weight: 600;
    color: {V_TEXT_SOFT};
}}

.vvalue {{
    font-size: 1.1rem;
    color: {V_TEXT};
}}

.timeline-box {{
    background: {V_BG};
    backdrop-filter: blur(12px);
    padding: 22px;
    border-radius: 18px;
    border: 1px solid {V_BORDER};
    box-shadow: 0 4px 14px {V_SHADOW};
}}

.timeline {{
    border-left: 2px solid {V_TEXT_SOFT};
    padding-left: 16px;
}}

.event {{
    margin-bottom: 14px;
    position: relative;
}}

.event:before {{
    content: '';
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: {V_TEXT};
    border: 2px solid {V_TEXT_SOFT};
    position: absolute;
    left: -22px;
    top: 4px;
}}

.event-title {{
    font-weight: 700;
    color: {V_TEXT};
}}

.event-date {{
    font-size: 0.9rem;
    color: {V_TEXT_SOFT};
}}

.badge {{
    display: inline-block;
    padding: 6px 12px;
    border-radius: 10px;
    font-size: .78rem;
    font-weight: 600;
    margin-right: 6px;
}}

.bgreen {{ background: #15803d; color: white; }}
.byellow {{ background: #ca8a04; color: white; }}
.bred {{ background: #b91c1c; color: white; }}
.bblue {{ background: #1d4ed8; color: white; }}
.bgray {{ background: #374151; color: white; }}

</style>
    """,
    unsafe_allow_html=True,
)


# -------------------------------
# SELECT DOSSIER
# -------------------------------
nums = sorted(df["Dossier N"].astype(int).unique())
selected = st.selectbox("Sélectionner un dossier", nums)

d = df[df["Dossier N"] == selected].iloc[0]


# -------------------------------
# HEADER
# -------------------------------
st.markdown(
    f"""
<div class="vcard">
    <div class="vtitle">📄 Dossier {d['Dossier N']} — {d['Nom']}</div>
</div>
""",
    unsafe_allow_html=True,
)


# -------------------------------
# BADGES STATUTS
# -------------------------------
st.markdown("### 🏷️ Statuts")

badges = ""

if d.get("Dossier envoye"):
    badges += "<span class='badge bblue'>Envoyé</span>"
if d.get("Dossier accepte"):
    badges += "<span class='badge bgreen'>Accepté</span>"
if d.get("Dossier refuse"):
    badges += "<span class='badge bred'>Refusé</span>"
if d.get("Dossier Annule"):
    badges += "<span class='badge bgray'>Annulé</span>"
if d.get("RFE"):
    badges += "<span class='badge byellow'>RFE</span>"

if badges == "":
    badges = "<span class='badge bgray'>Aucun statut</span>"

st.markdown(f"<div class='vcard'>{badges}</div>", unsafe_allow_html=True)


# -------------------------------
# SECTION : Infos générales
# -------------------------------
st.markdown("### 🧾 Informations générales")

with st.container():
    st.markdown(
        f"""
<div class="vcard">
    <div><span class="vlabel">Catégorie :</span> <span class="vvalue">{d['Categories']}</span></div>
    <div><span class="vlabel">Sous-catégorie :</span> <span class="vvalue">{d['Sous-categories']}</span></div>
    <div><span class="vlabel">Visa :</span> <span class="vvalue">{d['Visa']}</span></div>
</div>
""",
        unsafe_allow_html=True,
    )


# -------------------------------
# SECTION : Paiements
# -------------------------------
st.markdown("### 💰 Paiements")

restant = (d["Montant honoraires (US $)"] + d["Autres frais (US $)"]) - (
    d["Acompte 1"] + d["Acompte 2"] + d["Acompte 3"] + d["Acompte 4"]
)

st.markdown(
    f"""
<div class="vcard">
    <div><span class="vlabel">Honoraires :</span> {d['Montant honoraires (US $)']}$</div>
    <div><span class="vlabel">Autres frais :</span> {d['Autres frais (US $)']}$</div>
    <div><span class="vlabel">Total payé :</span> {d['Acompte 1'] + d['Acompte 2'] + d['Acompte 3'] + d['Acompte 4']}$</div>
    <div><span class="vlabel">Solde restant :</span> <b>{restant}$</b></div>
</div>
""",
    unsafe_allow_html=True,
)


# -------------------------------
# TIMELINE
# -------------------------------
st.markdown("### 🕓 Timeline du dossier")

events = []

if d.get("Date"):
    events.append(("📄 Dossier créé", d["Date"]))

if d.get("Escrow"):
    events.append(("💰 Escrow ouvert", d["Date"]))

if d.get("Dossier envoye"):
    events.append(("📤 Dossier envoyé", d.get("Date envoi", "")))

if d.get("Dossier accepte"):
    events.append(("✅ Dossier accepté", d.get("Date acceptation", "")))

if d.get("Dossier refuse"):
    events.append(("❌ Dossier refusé", d.get("Date refus", "")))

# Render timeline
timeline_html = "<div class='timeline-box'><div class='timeline'>"

for title, date in events:
    timeline_html += f"""
        <div class="event">
            <div class="event-title">{title}</div>
            <div class="event-date">{date}</div>
        </div>
    """

timeline_html += "</div></div>"

st.markdown(timeline_html, unsafe_allow_html=True)
