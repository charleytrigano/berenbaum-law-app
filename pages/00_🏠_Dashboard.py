import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")
st.markdown("<h1 style='margin-bottom:0px;'>🏠 Dashboard — Berenbaum Law App</h1>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 🔹 Charger data
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
# Normalisation
# ---------------------------------------------------------
BOOL_COLS = [
    "Dossier envoye", "Dossier accepte",
    "Dossier refuse", "Dossier Annule",
    "Escrow", "Escrow_a_reclamer", "Escrow_reclame"
]

def normalize_bool(x):
    if isinstance(x, bool): return x
    if str(x).lower() in ["1", "true", "yes", "oui"]: return True
    return False

for col in BOOL_COLS:
    if col not in df.columns:
        df[col] = False
    df[col] = df[col].apply(normalize_bool)

if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Année"] = df["Date"].dt.year.fillna(0).astype(int)
df["Mois"] = df["Date"].dt.strftime("%Y-%m")
df["Trimestre"] = df["Date"].dt.to_period("Q").astype(str)
df["Semestre"] = df["Date"].dt.to_period("6M").astype(str)

# ---------------------------------------------------------
# 🔍 FILTRES AVANCÉS
# ---------------------------------------------------------
st.subheader("🔍 Filtres avancés")

colA, colB, colC, colD = st.columns(4)

# Catégories dépendantes
cat_list = sorted(visa_df["Categories"].dropna().unique())
categorie = colA.selectbox("📌 Catégorie", ["Toutes"] + cat_list)

# Sous-catégories dépendantes
if categorie != "Toutes":
    sous_list = sorted(visa_df[visa_df["Categories"] == categorie]["Sous-categories"].dropna().unique())
else:
    sous_list = sorted(visa_df["Sous-categories"].dropna().unique())

sous_categorie = colB.selectbox("📁 Sous-catégorie", ["Toutes"] + sous_list)

# Visa dépendant
if sous_categorie != "Toutes":
    visa_list = sorted(visa_df[visa_df["Sous-categories"] == sous_categorie]["Visa"].dropna().unique())
else:
    visa_list = sorted(visa_df["Visa"].dropna().unique())

visa_filter = colC.selectbox("🛂 Visa", ["Toutes"] + visa_list)

# Statut
statut = colD.selectbox(
    "📂 Statut",
    [
        "Tous", "Envoyé", "Accepté", "Refusé",
        "Annulé", "Escrow en cours", "Escrow à réclamer", "Escrow réclamé"
    ]
)

# ---------------------------------------------------------
# 🔍 FILTRE : COMPARAISON ENTRE PERIODES
# ---------------------------------------------------------
st.subheader("🕒 Comparaison entre périodes")

colP1, colP2, colP3 = st.columns(3)

type_periode = colP1.selectbox(
    "Type de période",
    ["Aucune comparaison", "Mois", "Trimestre", "Semestre", "Date à date", "Années multiples"]
)

# --- sélection des périodes selon le type ---

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
    periode_A = colP2.date_input("Début → Fin (A)", [])
    periode_B = colP3.date_input("Début → Fin (B)", [])

elif type_periode == "Années multiples":
    annees = sorted(df["Année"].unique())
    periodes = colP2.multiselect("Sélectionner jusqu'à 5 années", annees, max_selections=5)

# ---------------------------------------------------------
# 🔹 APPLICATION DES FILTRES SUR LES DOSSIERS
# ---------------------------------------------------------
df_filtered = df.copy()

if categorie != "Toutes":
    df_filtered = df_filtered[df_filtered["Categories"] == categorie]

if sous_categorie != "Toutes":
    df_filtered = df_filtered[df_filtered["Sous-categories"] == sous_categorie]

if visa_filter != "Toutes":
    df_filtered = df_filtered[df_filtered["Visa"] == visa_filter]

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

# ---------------------------------------------------------
# 🎨 KPIs COLORÉS (NOUVEAU DESIGN)
# ---------------------------------------------------------

def kpi_box(label, value, color):
    html = f"""
    <div style="
        background:{color};
        padding:15px;
        border-radius:12px;
        text-align:center;
        color:white;
        font-size:15px;">
        <span>{label}</span><br>
        <span style='font-size:22px; font-weight:bold;'>{value}</span>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

st.subheader("📊 Indicateurs clés")

col1, col2, col3, col4 = st.columns(4)
kpi_box("Total dossiers", len(df_filtered), "#2c3e50")
kpi_box("Envoyés", df_filtered["Dossier envoye"].sum(), "#2980b9")
kpi_box("Acceptés", df_filtered["Dossier accepte"].sum(), "#27ae60")
kpi_box("Refusés", df_filtered["Dossier refuse"].sum(), "#c0392b")

col5, col6, col7, col8 = st.columns(4)
kpi_box("Annulés", df_filtered["Dossier Annule"].sum(), "#8e44ad")
kpi_box("Escrow en cours", df_filtered["Escrow"].sum(), "#16a085")
kpi_box("À réclamer", df_filtered["Escrow_a_reclamer"].sum(), "#d35400")
kpi_box("Réclamé", df_filtered["Escrow_reclame"].sum(), "#7f8c8d")

# ---------------------------------------------------------
# 📄 TABLEAU FINAL
# ---------------------------------------------------------
st.subheader("📄 Liste des dossiers filtrés")

colonnes = [
    "Dossier N", "Nom", "Date", "Categories",
    "Sous-categories", "Visa", "Dossier envoye", "Escrow"
]

colonnes = [c for c in colonnes if c in df_filtered.columns]

st.dataframe(
    df_filtered[colonnes].sort_values("Date", ascending=False),
    use_container_width=True
)
