import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")
st.title("🏠 Dashboard — Berenbaum Law App")

# ---------------------------------------------------------
# 🔹 Charger base
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
# 🔹 Normalisation colonnes manquantes
# ---------------------------------------------------------
BOOL_COLS = [
    "Dossier envoye",
    "Dossier accepte",
    "Dossier refuse",
    "Dossier Annule",
    "Escrow",
    "Escrow_a_reclamer",
    "Escrow_reclame",
]

def normalize_bool(x):
    if isinstance(x, bool): return x
    if str(x).lower() in ["1", "true", "yes", "oui"]: return True
    return False

for col in BOOL_COLS:
    if col not in df.columns:
        df[col] = False
    df[col] = df[col].apply(normalize_bool)

# Date
if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
else:
    df["Date"] = pd.NaT

df["Année"] = df["Date"].dt.year.fillna(0).astype(int)

# ---------------------------------------------------------
# 🔍 FILTRES DÉPENDANTS
# ---------------------------------------------------------
st.subheader("🔍 Filtres avancés")

col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)

# Année
annees = sorted(df["Année"].unique())
annee = col_f1.selectbox("📅 Année", ["Toutes"] + [str(a) for a in annees if a > 0])

# Catégories dépendant du VISA.CSV ou VISA.JSON
if "Categories" in visa_df.columns:
    liste_cat = sorted(visa_df["Categories"].dropna().unique())
else:
    liste_cat = sorted(df["Categories"].dropna().unique())

categorie = col_f2.selectbox("📌 Catégorie", ["Toutes"] + liste_cat)

# Sous-catégories dépendantes
if categorie != "Toutes":
    souscats = sorted(
        visa_df[visa_df["Categories"] == categorie]["Sous-categories"]
        .dropna()
        .unique()
    )
else:
    souscats = sorted(visa_df["Sous-categories"].dropna().unique())

sous_categorie = col_f3.selectbox("📁 Sous-catégorie", ["Toutes"] + souscats)

# Visas dépendants
if sous_categorie != "Toutes":
    visas = sorted(
        visa_df[visa_df["Sous-categories"] == sous_categorie]["Visa"]
        .dropna()
        .unique()
    )
else:
    visas = sorted(visa_df["Visa"].dropna().unique())

visa_filter = col_f4.selectbox("🛂 Visa", ["Toutes"] + visas)

# Statut
statut = col_f5.selectbox(
    "📂 Statut",
    [
        "Tous",
        "Envoyé",
        "Accepté",
        "Refusé",
        "Annulé",
        "Escrow en cours",
        "Escrow à réclamer",
        "Escrow réclamé",
    ]
)

# ---------------------------------------------------------
# 🔹 APPLICATION DES FILTRES SUR LES DOSSIERS
# ---------------------------------------------------------
df_filtered = df.copy()

# Année
if annee != "Toutes":
    df_filtered = df_filtered[df_filtered["Année"] == int(annee)]

# Catégorie
if categorie != "Toutes":
    df_filtered = df_filtered[df_filtered["Categories"] == categorie]

# Sous-catégorie
if sous_categorie != "Toutes":
    df_filtered = df_filtered[df_filtered["Sous-categories"] == sous_categorie]

# Visa
if visa_filter != "Toutes":
    df_filtered = df_filtered[df_filtered["Visa"] == visa_filter]

# Statut
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
# 📊 KPIs
# ---------------------------------------------------------
st.subheader("📊 Indicateurs clés")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total dossiers", len(df_filtered))
k2.metric("Envoyés", df_filtered["Dossier envoye"].sum())
k3.metric("Acceptés", df_filtered["Dossier accepte"].sum())
k4.metric("Refusés", df_filtered["Dossier refuse"].sum())

k5, k6, k7, k8 = st.columns(4)
k5.metric("Annulés", df_filtered["Dossier Annule"].sum())
k6.metric("Escrow en cours", df_filtered["Escrow"].sum())
k7.metric("Escrow à réclamer", df_filtered["Escrow_a_reclamer"].sum())
k8.metric("Escrow réclamé", df_filtered["Escrow_reclame"].sum())

# ---------------------------------------------------------
# 💰 FINANCES
# ---------------------------------------------------------
st.subheader("💰 Finances")

honoraires = df_filtered.get("Montant honoraires (US $)", pd.Series([0])).fillna(0).sum()
frais = df_filtered.get("Autres frais (US $)", pd.Series([0])).fillna(0).sum()

paiements = 0
for col in ["Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4"]:
    if col in df_filtered.columns:
        paiements += df_filtered[col].fillna(0).sum()

solde = honoraires + frais - paiements

f1, f2, f3 = st.columns(3)
f1.metric("Total facturé", f"${honoraires + frais:,.2f}")
f2.metric("Paiements reçus", f"${paiements:,.2f}")
f3.metric("Solde restant", f"${solde:,.2f}")

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
