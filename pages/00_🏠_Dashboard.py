import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")
st.title("🏠 Tableau de bord — Berenbaum Law")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = pd.DataFrame(db.get("clients", []))

if clients.empty:
    st.info("Aucun dossier trouvé.")
    st.stop()

# ---------------------------------------------------------
# NORMALISATION
# ---------------------------------------------------------
clients["Dossier N"] = pd.to_numeric(clients["Dossier N"], errors="coerce")

def to_bool(x):
    if isinstance(x, bool):
        return x
    return str(x).lower() in ["yes", "true", "1", "oui"]

for col in ["Dossier envoye", "Dossier accepte", "Dossier refuse", 
            "Dossier Annule", "RFE", "Escrow", "Escrow_a_reclamer", "Escrow_reclame"]:
    if col not in clients.columns:
        clients[col] = False
    clients[col] = clients[col].apply(to_bool)

# ---------------------------------------------------------
# COMPUTE KPI
# ---------------------------------------------------------
total_dossiers = len(clients)
envoyes = clients["Dossier envoye"].sum()
acceptes = clients["Dossier accepte"].sum()
refuses = clients["Dossier refuse"].sum()
annules = clients["Dossier Annule"].sum()
en_escrow = clients["Escrow"].sum()

# ---------------------------------------------------------
# KPI DISPLAY (VisionOS)
# ---------------------------------------------------------
st.write("""
<style>
.kpi-card {
    background: rgba(255,255,255,0.4);
    backdrop-filter: blur(14px);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.1);
    cursor:pointer;
    transition:0.2s;
}
.kpi-card:hover {
    transform:scale(1.02);
}
.kpi-number {
    font-size:30px;
    font-weight:700;
}
.kpi-label {
    font-size:16px;
}
</style>
""", unsafe_allow_html=True)

kpi_cols = st.columns(6)

KPIS = [
    ("📁", total_dossiers, "Dossiers"),
    ("📨", envoyes, "Envoyés"),
    ("✅", acceptes, "Acceptés"),
    ("❌", refuses, "Refusés"),
    ("🚫", annules, "Annulés"),
    ("💰", en_escrow, "Escrow en cours"),
]

for i, (icon, number, label) in enumerate(KPIS):
    with kpi_cols[i]:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-number">{icon} {number}</div>
                <div class="kpi-label">{label}</div>
            </div>
            """, unsafe_allow_html=True
        )

# ---------------------------------------------------------
# LISTE DES DOSSIERS (VisionOS Cards)
# ---------------------------------------------------------
st.subheader("📂 Tous les dossiers")

for i, row in clients.sort_values("Dossier N").iterrows():
    dnum = int(row["Dossier N"])
    nom = row.get("Nom", "")

    with st.container():
        cols = st.columns([4, 1])
        cols[0].markdown(
            f"""
            <div style="
                background:rgba(255,255,255,0.5);
                backdrop-filter:blur(14px);
                border-radius:16px;
                padding:14px;
                margin-bottom:12px;">
                <b>Dossier {dnum}</b> — {nom}<br>
                <span style="font-size:13px;color:#666;">Click → Voir fiche</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        if cols[1].button("👁️ Voir", key=f"view_{dnum}"):
            st.session_state["selected_dossier"] = dnum
            st.switch_page("pages/11_📄_Fiche_dossier.py")
