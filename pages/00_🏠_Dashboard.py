import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

st.set_page_config(page_title="🏠 Dashboard", page_icon="🏠", layout="wide")

# ---------------------------------------------------------
# UTILS
# ---------------------------------------------------------
def safe_float(x):
    try:
        return float(x)
    except:
        return 0.0

def safe_int(x):
    try:
        return int(float(x))
    except:
        return 0

def normalize(x):
    if isinstance(x, bool):
        return x
    if str(x).lower() in ["true", "1", "yes", "oui"]:
        return True
    return False

# ---------------------------------------------------------
# LOAD DB
# ---------------------------------------------------------
db = load_database()
clients = pd.DataFrame(db.get("clients", []))

if clients.empty:
    st.error("Aucun dossier trouvé.")
    st.stop()

# ---------------------------------------------------------
# NORMALISATION
# ---------------------------------------------------------
clients["Dossier N"] = clients["Dossier N"].apply(safe_int)

for col in ["Dossier envoye", "Dossier accepte", "Dossier refuse", "Escrow"]:
    if col not in clients.columns:
        clients[col] = False
    clients[col] = clients[col].apply(normalize)

# ---------------------------------------------------------
# FILTRES (bandeau horizontal)
# ---------------------------------------------------------
st.markdown("## 🔍 Filtres")

colF1, colF2, colF3 = st.columns(3)

# ➤ Filtre Catégorie
cat_list = ["Toutes"] + sorted([c for c in clients["Categories"].unique() if c not in ["", None]])
selected_cat = colF1.selectbox("Catégorie", cat_list)

df = clients.copy()

if selected_cat != "Toutes":
    df = df[df["Categories"] == selected_cat]

# ➤ Filtre Sous-catégorie
ss_list = ["Toutes"] + sorted([s for s in df["Sous-categories"].unique() if s not in ["", None]])
selected_ss = colF2.selectbox("Sous-catégorie", ss_list)

if selected_ss != "Toutes":
    df = df[df["Sous-categories"] == selected_ss]

# ➤ Filtre Visa
visa_list = ["Toutes"] + sorted([v for v in df["Visa"].unique() if v not in ["", None]])
selected_visa = colF3.selectbox("Visa", visa_list)

if selected_visa != "Toutes":
    df = df[df["Visa"] == selected_visa]

# ---------------------------------------------------------
# KPI Section
# ---------------------------------------------------------
st.markdown("## 📊 Indicateurs")

col1, col2, col3, col4, col5, col6 = st.columns(6)

# KPI values
total_dossiers = len(df)
envoyes = df["Dossier envoye"].sum()
acceptes = df["Dossier accepte"].sum()
refuses = df["Dossier refuse"].sum()
escrow = df["Escrow"].sum()
total_hon = df["Montant honoraires (US $)"].apply(safe_float).sum()

def kpi_box(col, title, value, color):
    col.markdown(
        f"""
        <div style="
            background-color:{color};
            padding:12px;
            border-radius:10px;
            text-align:center;
            color:white;
            font-size:14px;">
            <div style="font-size:16px;"><b>{title}</b></div>
            <div style="font-size:22px; margin-top:6px;">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

kpi_box(col1, "Total dossiers", total_dossiers, "#444")
kpi_box(col2, "Envoyés", envoyes, "#2b6cb0")
kpi_box(col3, "Acceptés", acceptes, "#38a169")
kpi_box(col4, "Refusés", refuses, "#e53e3e")
kpi_box(col5, "Escrow en cours", escrow, "#d69e2e")
kpi_box(col6, "Honoraires totaux", f"${total_hon:,.0f}", "#805ad5")

# ---------------------------------------------------------
# LISTE DES DOSSIERS (CARTES INTERACTIVES)
# ---------------------------------------------------------
st.markdown("## 📁 Liste des dossiers filtrés")

for i, (_, row) in enumerate(df.iterrows()):
    with st.container():
        st.markdown(
            f"""
            <div style="
                border:1px solid #444;
                padding:15px;
                border-radius:10px;
                margin-bottom:10px;">
                <b>Dossier {row['Dossier N']} — {row['Nom']}</b><br>
                <span style='opacity:0.7;'>{row.get('Categories','')} → {row.get('Sous-categories','')} → {row.get('Visa','')}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Bouton voir dossier (clé unique)
        st.button(
            f"👁️ Voir dossier {row['Dossier N']}",
            key=f"view_btn_{i}",
            on_click=lambda r=row: st.session_state.update({"selected_dossier": r["Dossier N"]})
        )

        # Si clic → redirection vers Fiche dossier
        if st.session_state.get("selected_dossier") == row["Dossier N"]:
            st.switch_page("pages/11_📄_Fiche_dossier.py")

