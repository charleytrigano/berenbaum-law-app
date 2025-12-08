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

if not clients:
    st.warning("Aucun dossier trouvé dans la base.")
    st.stop()

df = pd.DataFrame(clients)

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

for col in BOOL_COLS:
    if col not in df.columns:
        df[col] = False

def normalize_bool(x):
    if isinstance(x, bool):
        return x
    if str(x).lower() in ["1", "true", "yes", "oui"]:
        return True
    return False

for col in BOOL_COLS:
    df[col] = df[col].apply(normalize_bool)

# Dates
if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
else:
    df["Date"] = pd.NaT

df["Année"] = df["Date"].dt.year.fillna(0).astype(int)

# ---------------------------------------------------------
# 🔍 FILTRES VISIBLES SUR LA PAGE
# ---------------------------------------------------------
st.subheader("🔍 Filtres")

col_f1, col_f2, col_f3, col_f4 = st.columns(4)

# ▪ Filtre Année
annee_list = sorted(df["Année"].unique())
annee = col_f1.selectbox(
    "📅 Année",
    ["Toutes"] + [str(a) for a in annee_list if a > 0]
)

# ▪ Filtre Catégories
categories = df.get("Categories", pd.Series([""])).fillna("")
categorie = col_f2.selectbox("📌 Catégorie", ["Toutes"] + sorted(categories.unique()))

# ▪ Filtre Sous-catégories
souscats = df.get("Sous-categories", pd.Series([""])).fillna("")
sous_categorie = col_f3.selectbox("📁 Sous-catégorie", ["Toutes"] + sorted(souscats.unique()))

# ▪ Filtre Visa
visa_list = df.get("Visa", pd.Series([""])).fillna("")
visa_filter = col_f4.selectbox("🛂 Visa", ["Toutes"] + sorted(visa_list.unique()))


# ---------------------------------------------------------
# 🔍 COMPARAISON ENTRE PÉRIODES (5 ANS MAX)
# ---------------------------------------------------------
st.subheader("📈 Comparaison entre périodes")

col_p1, col_p2 = st.columns(2)

per1 = col_p1.selectbox("📆 Période A (année)", ["Aucune"] + [str(a) for a in annee_list if a > 0])
per2 = col_p2.selectbox("📆 Période B (année)", ["Aucune"] + [str(a) for a in annee_list if a > 0])

# ---------------------------------------------------------
# 🔹 Application des filtres simples
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


# ---------------------------------------------------------
# 🔹 KPIs
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
# 📈 COMPARAISON ENTRE PÉRIODES
# ---------------------------------------------------------
if per1 != "Aucune" and per2 != "Aucune":
    st.markdown("### 📊 Comparaison Périodes A vs B")

    dfA = df[df["Année"] == int(per1)]
    dfB = df[df["Année"] == int(per2)]

    c1, c2 = st.columns(2)

    c1.metric(f"Dossiers {per1}", len(dfA))
    c2.metric(f"Dossiers {per2}", len(dfB))

    c1.metric(f"Acceptés {per1}", dfA["Dossier accepte"].sum())
    c2.metric(f"Acceptés {per2}", dfB["Dossier accepte"].sum())

    c1.metric(f"Facturé {per1}", f"${dfA.get('Montant honoraires (US $)', 0).sum():,.2f}")
    c2.metric(f"Facturé {per2}", f"${dfB.get('Montant honoraires (US $)', 0).sum():,.2f}")

# ---------------------------------------------------------
# 📄 Tableau
# ---------------------------------------------------------
st.subheader("📄 Liste des dossiers filtrés")

colonnes = [
    "Dossier N",
    "Nom",
    "Date",
    "Categories",
    "Sous-categories",
    "Visa",
    "Dossier envoye",
    "Escrow"
]

colonnes = [c for c in colonnes if c in df_filtered.columns]

st.dataframe(
    df_filtered[colonnes].sort_values("Date", ascending=False),
    use_container_width=True
)
