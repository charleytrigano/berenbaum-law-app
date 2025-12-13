import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database
from components.kpi_cards import kpi_card

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="🏠 Dashboard", page_icon="🏠", layout="wide")
render_sidebar()
st.title("🏠 Tableau de bord – Berenbaum Law App")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = pd.DataFrame(db.get("clients", []))

if clients.empty:
    st.warning("Aucun dossier trouvé.")
    st.stop()

# ---------------------------------------------------------
# NORMALISATION NUMÉRIQUE
# ---------------------------------------------------------
for col in [
    "Montant honoraires (US $)",
    "Autres frais (US $)",
    "Acompte 1",
    "Acompte 2",
    "Acompte 3",
    "Acompte 4",
]:
    if col not in clients.columns:
        clients[col] = 0
    clients[col] = pd.to_numeric(clients[col], errors="coerce").fillna(0)

# ---------------------------------------------------------
# CALCULS FINANCIERS
# ---------------------------------------------------------
clients["Total facturé"] = (
    clients["Montant honoraires (US $)"] + clients["Autres frais (US $)"]
)

clients["Total encaissé"] = (
    clients["Acompte 1"]
    + clients["Acompte 2"]
    + clients["Acompte 3"]
    + clients["Acompte 4"]
)

clients["Solde dû"] = clients["Total facturé"] - clients["Total encaissé"]

# ---------------------------------------------------------
# FILTRES
# ---------------------------------------------------------
st.subheader("🎛️ Filtres")

f1, f2, f3, f4 = st.columns(4)

cat = f1.selectbox(
    "Catégorie",
    ["Toutes"] + sorted(clients["Categories"].dropna().unique().tolist()),
)

df = clients.copy()
if cat != "Toutes":
    df = df[df["Categories"] == cat]

sous = f2.selectbox(
    "Sous-catégorie",
    ["Toutes"] + sorted(df["Sous-categories"].dropna().unique().tolist()),
)

if sous != "Toutes":
    df = df[df["Sous-categories"] == sous]

visa = f3.selectbox(
    "Visa",
    ["Tous"] + sorted(df["Visa"].dropna().unique().tolist()),
)

if visa != "Tous":
    df = df[df["Visa"] == visa]

statut = f4.selectbox(
    "Statut",
    ["Tous", "Envoyé", "Accepté", "Refusé", "Annulé", "RFE"],
)

if statut != "Tous":
    mapping = {
        "Envoyé": "Dossier envoye",
        "Accepté": "Dossier accepte",
        "Refusé": "Dossier refuse",
        "Annulé": "Dossier Annule",
        "RFE": "RFE",
    }
    col_statut = mapping.get(statut)
    if col_statut in df.columns:
        df = df[df[col_statut] == True]

# ---------------------------------------------------------
# KPI — UNE SEULE LIGNE (TAILLE RÉDUITE)
# ---------------------------------------------------------
st.subheader("📈 Indicateurs clés")

k1, k2, k3, k4, k5, k6 = st.columns(6)

kpi_card("Nombre de dossiers", len(df), "📁")
kpi_card("Honoraires", f"${df['Montant honoraires (US $)'].sum():,.0f}", "💰")
kpi_card("Autres frais", f"${df['Autres frais (US $)'].sum():,.0f}", "➕")
kpi_card("Total facturé", f"${df['Total facturé'].sum():,.0f}", "🧾")
kpi_card("Total encaissé", f"${df['Total encaissé'].sum():,.0f}", "🏦")
kpi_card("Solde dû", f"${df['Solde dû'].sum():,.0f}", "⚠️")

# ---------------------------------------------------------
# 🔧 TRI ROBUSTE DOSSIER / SOUS-DOSSIER
# ---------------------------------------------------------
def split_dossier_n(val):
    if pd.isna(val):
        return (0, 0)
    s = str(val)
    if "-" in s:
        p, i = s.split("-", 1)
        try:
            return int(p), int(i)
        except:
            return 0, 0
    else:
        try:
            return int(s), 0
        except:
            return 0, 0

df = df.copy()
df["__parent"] = df["Dossier N"].apply(lambda x: split_dossier_n(x)[0])
df["__index"] = df["Dossier N"].apply(lambda x: split_dossier_n(x)[1])

# ---------------------------------------------------------
# TABLEAU DOSSIERS
# ---------------------------------------------------------
st.subheader("📋 Liste des dossiers")

cols_display = [
    "Dossier N",
    "Nom",
    "Categories",
    "Sous-categories",
    "Visa",
    "Total facturé",
    "Total encaissé",
    "Solde dû",
    "Escrow",
    "Escrow_a_reclamer",
    "Escrow_reclame",
]

st.dataframe(
    df[cols_display + ["__parent", "__index"]]
    .sort_values(["__parent", "__index"])
    .drop(columns=["__parent", "__index"]),
    use_container_width=True,
)