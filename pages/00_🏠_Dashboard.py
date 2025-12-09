import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")
st.markdown("<h1 style='margin-bottom:0px;'>🏠 Dashboard — Berenbaum Law App</h1>", unsafe_allow_html=True)

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
visa_raw = db.get("visa", [])

if not clients:
    st.warning("Aucun dossier trouvé dans la base.")
    st.stop()

df = pd.DataFrame(clients)
visa_df = pd.DataFrame(visa_raw)

# ---------------------------------------------------------
# NORMALISATION COLONNES
# ---------------------------------------------------------
BOOL_COLS = [
    "Dossier envoye", "Dossier accepte", "Dossier refuse",
    "Dossier Annule", "Escrow", "Escrow_a_reclamer", "Escrow_reclame", "RFE"
]

def normalize_bool(x):
    if isinstance(x, bool): return x
    if str(x).lower() in ["1", "true", "oui", "yes"]: return True
    return False

for col in BOOL_COLS:
    if col not in df.columns:
        df[col] = False
    df[col] = df[col].apply(normalize_bool)

# Dates
if "Date" not in df.columns:
    df["Date"] = None

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Année"]     = df["Date"].dt.year.fillna(0).astype(int)
df["Mois"]      = df["Date"].dt.strftime("%Y-%m")
df["Trimestre"] = df["Date"].dt.to_period("Q").astype(str)
df["Semestre"]  = df["Date"].dt.to_period("6M").astype(str)

# ---------------------------------------------------------
# 🔍 FILTRES AVANCÉS AVEC LIENS CATÉGORIES → SOUS-CATÉGORIES → VISA
# ---------------------------------------------------------
st.subheader("🔍 Filtres avancés")

colA, colB, colC, colD = st.columns(4)

# FILTRE Année
annees = sorted(df["Année"].unique())
annee = colA.selectbox("📅 Année", ["Toutes"] + [str(a) for a in annees if a > 0])

# FILTRE Catégorie
if "Categories" in visa_df.columns:
    cat_list = sorted(visa_df["Categories"].dropna().unique())
else:
    cat_list = sorted(df["Categories"].dropna().unique())

categorie = colB.selectbox("📌 Catégorie", ["Toutes"] + cat_list)

# FILTRE Sous-catégories dépendantes
if categorie != "Toutes":
    sous_list = sorted(
        visa_df[visa_df["Categories"] == categorie]["Sous-categories"]
        .dropna().unique()
    )
else:
    sous_list = sorted(visa_df["Sous-categories"].dropna().unique())

sous_categorie = colC.selectbox("📁 Sous-catégorie", ["Toutes"] + sous_list)

# FILTRE Visa dépendant
if sous_categorie != "Toutes":
    visa_list = sorted(
        visa_df[visa_df["Sous-categories"] == sous_categorie]["Visa"]
        .dropna().unique()
    )
else:
    visa_list = sorted(visa_df["Visa"].dropna().unique())

visa_filter = colD.selectbox("🛂 Visa", ["Toutes"] + visa_list)

# ---------------------------------------------------------
# FILTRE STATUT
# ---------------------------------------------------------
st.subheader("📂 Filtre statut")

statut = st.selectbox(
    "Statut dossier",
    [
        "Tous", "Envoyé", "Accepté", "Refusé",
        "Annulé", "Escrow en cours", "Escrow à réclamer", "Escrow réclamé", "RFE"
    ]
)

# ---------------------------------------------------------
# COMPARAISON ENTRE PERIODES
# ---------------------------------------------------------
st.subheader("🕒 Comparaison entre périodes")

colP1, colP2, colP3 = st.columns(3)

type_periode = colP1.selectbox(
    "Type de période",
    ["Aucune comparaison", "Mois", "Trimestre", "Semestre", "Date à date", "Années multiples"]
)

periode_A = periode_B = None

if type_periode == "Mois":
    mois_list = sorted(df["Mois"].dropna().unique())
    periode_A = colP2.selectbox("Période A", mois_list)
    periode_B = colP3.selectbox("Période B", mois_list)

elif type_periode == "Trimestre":
    tri_list = sorted(df["Trimestre"].dropna().unique())
    periode_A = colP2.selectbox("Période A", tri_list)
    periode_B = colP3.selectbox("Période B", tri_list)

elif type_periode == "Semestre":
    sem_list = sorted(df["Semestre"].dropna().unique())
    periode_A = colP2.selectbox("Période A", sem_list)
    periode_B = colP3.selectbox("Période B", sem_list)

elif type_periode == "Date à date":
    periode_A = colP2.date_input("Début → Fin (A)")
    periode_B = colP3.date_input("Début → Fin (B)")

elif type_periode == "Années multiples":
    annees = sorted(df["Année"].unique())
    periodes = colP2.multiselect("Sélectionner jusqu'à 5 années", annees, max_selections=5)

# ---------------------------------------------------------
# APPLICATION DES FILTRES
# ---------------------------------------------------------
df_filtered = df.copy()

if annee != "Toutes":
    df_filtered = df_filtered[df_filtered["Année"] == int(annee)]

if categorie != "Toutes":
    df_filtered = df_filtered[df_filtered["Categories"] == categorie]

if sous_categorie != "Toutes":
    df_filtered = df_filtered[df_filtered["Sous-categories"] == sous_categorie]

if visa_filter != "Toutes":
    df_filtered = df_filtered[df_filtered["Visa"] == visa_filter]

# STATUT
if statut == "Envoyé":
    df_filtered = df_filtered[df_filtered["Dossier envoye"]]
elif statut == "Accepté":
    df_filtered = df_filtered[df_filtered["Dossier accepte"]]
elif statut == "Refusé":
    df_filtered = df_filtered[df_filtered["Dossier refuse"]]
elif statut == "Annulé":
    df_filtered = df_filtered[df_filtered["Dossier Annule"]]
elif statut == "Escrow en cours":
    df_filtered = df_filtered[df_filtered["Escrow"]]
elif statut == "Escrow à réclamer":
    df_filtered = df_filtered[df_filtered["Escrow_a_reclamer"]]
elif statut == "Escrow réclamé":
    df_filtered = df_filtered[df_filtered["Escrow_reclame"]]
elif statut == "RFE":
    df_filtered = df_filtered[df_filtered["RFE"]]

# ---------------------------------------------------------
# KPI CARDS — PREMIUM VERSION (6 PAR LIGNE)
# ---------------------------------------------------------
st.subheader("📊 Indicateurs clés")

def kpi_card(label, value, color, icon, page):
    html = f"""
    <a href="/{page}" target="_self" style="text-decoration:none;">
    <div style="
        background:{color};
        padding:10px;
        border-radius:12px;
        text-align:center;
        color:white;
        min-height:73px;
        box-shadow:0px 2px 6px rgba(0,0,0,0.2);
        transition:0.15s;
    " onmouseover="this.style.transform='scale(1.03)'"
      onmouseout="this.style.transform='scale(1)'">
        <div style="font-size:17px; margin-bottom:3px;">{icon}</div>
        <div style="font-size:13px; line-height:14px;">{label}</div>
        <div style="font-size:18px; font-weight:bold; margin-top:2px;">{value}</div>
    </div></a>
    """
    return html

# CALCUL FINANCIER
honoraires = df_filtered.get("Montant honoraires (US $)", pd.Series([0])).fillna(0).sum()
frais = df_filtered.get("Autres frais (US $)", pd.Series([0])).fillna(0).sum()

paiements = 0
for col in ["Acompte 1","Acompte 2","Acompte 3","Acompte 4"]:
    if col in df_filtered.columns:
        paiements += df_filtered[col].fillna(0).sum()

solde = honoraires + frais - paiements

line1 = st.columns(6)
line2 = st.columns(6)

line1[0].markdown(kpi_card("Total", len(df_filtered), "#2c3e50", "📁", "01_📁_Liste_dossiers"), unsafe_allow_html=True)
line1[1].markdown(kpi_card("Envoyés", df_filtered["Dossier envoye"].sum(), "#2980b9", "📤", "01_📁_Liste_dossiers"), unsafe_allow_html=True)
line1[2].markdown(kpi_card("Acceptés", df_filtered["Dossier accepte"].sum(), "#27ae60", "✅", "01_📁_Liste_dossiers"), unsafe_allow_html=True)
line1[3].markdown(kpi_card("Refusés", df_filtered["Dossier refuse"].sum(), "#c0392b", "⛔", "01_📁_Liste_dossiers"), unsafe_allow_html=True)
line1[4].markdown(kpi_card("Annulés", df_filtered["Dossier Annule"].sum(), "#8e44ad", "❌", "01_📁_Liste_dossiers"), unsafe_allow_html=True)
line1[5].markdown(kpi_card("RFE", df_filtered["RFE"].sum() if "RFE" in df_filtered else 0, "#d35400", "⚠️", "01_📁_Liste_dossiers"), unsafe_allow_html=True)

line2[0].markdown(kpi_card("Escrow en cours", df_filtered["Escrow"].sum(), "#16a085", "💰", "06_💰_Escrow"), unsafe_allow_html=True)
line2[1].markdown(kpi_card("À réclamer", df_filtered["Escrow_a_reclamer"].sum(), "#e67e22", "📩", "06_💰_Escrow"), unsafe_allow_html=True)
line2[2].markdown(kpi_card("Réclamé", df_filtered["Escrow_reclame"].sum(), "#7f8c8d", "📬", "06_💰_Escrow"), unsafe_allow_html=True)
line2[3].markdown(kpi_card("Honoraires", f"{honoraires:,.0f}$", "#34495e", "💵", "08_📒_Comptabilite"), unsafe_allow_html=True)
line2[4].markdown(kpi_card("Paiements", f"{paiements:,.0f}$", "#1abc9c", "🏦", "08_📒_Comptabilite"), unsafe_allow_html=True)
line2[5].markdown(kpi_card("Solde", f"{solde:,.0f}$", "#d35400", "🧾", "08_📒_Comptabilite"), unsafe_allow_html=True)

# ---------------------------------------------------------
# TABLEAU FINAL
# ---------------------------------------------------------
st.subheader("📄 Liste des dossiers filtrés")

colonnes = [
    "Dossier N", "Nom", "Date", "Categories", "Sous-categories",
    "Visa", "Dossier envoye", "Escrow"
]

colonnes = [c for c in colonnes if c in df_filtered.columns]

st.dataframe(
    df_filtered[colonnes].sort_values("Date", ascending=False),
    use_container_width=True
)
