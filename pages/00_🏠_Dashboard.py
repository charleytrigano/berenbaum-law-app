import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("📊 Tableau de bord – Berenbaum Law App")

# ======================================================
# 🔹 LOAD DATABASE
# ======================================================
db = load_database()
clients = db.get("clients", [])
visa_raw = pd.DataFrame(db.get("visa", []))

if not clients:
    st.warning("Aucun dossier trouvé dans Dropbox.")
    st.stop()

df = pd.DataFrame(clients)

# ======================================================
# 🔹 CLEAN VISA TABLE (robuste)
# ======================================================
def clean_visa_df(dfv):
    if dfv is None or dfv.empty:
        return pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

    rename_map = {}
    for col in dfv.columns:
        c = col.lower().replace("é", "e").replace("è", "e").replace("ê", "e")
        if "categorie" in c:
            rename_map[col] = "Categories"
        elif "sous" in c:
            rename_map[col] = "Sous-categories"
        elif "visa" in c:
            rename_map[col] = "Visa"

    dfv = dfv.rename(columns=rename_map)

    for col in ["Categories", "Sous-categories", "Visa"]:
        if col not in dfv.columns:
            dfv[col] = ""

    dfv["Categories"] = dfv["Categories"].astype(str).str.strip()
    dfv["Sous-categories"] = dfv["Sous-categories"].astype(str).str.strip()
    dfv["Visa"] = dfv["Visa"].astype(str).str.strip()

    return dfv

visa_table = clean_visa_df(visa_raw)

# ======================================================
# 🔹 CLEAN CLIENT TABLE
# ======================================================
df["Date"] = pd.to_datetime(df.get("Date"), errors="coerce")

money_cols = [
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4"
]
for c in money_cols:
    df[c] = pd.to_numeric(df.get(c, 0), errors="coerce").fillna(0)

df["Total facturé"] = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
df["Montant encaissé"] = df["Acompte 1"] + df["Acompte 2"] + df["Acompte 3"] + df["Acompte 4"]
df["Solde"] = df["Total facturé"] - df["Montant encaissé"]
df["Année"] = df["Date"].dt.year

# Helper colonne "Statut"
def compute_status(row):
    if row.get("Dossier accepte"):
        return "Accepté"
    if row.get("Dossier refuse"):
        return "Refusé"
    if row.get("Dossier Annule"):
        return "Annulé"
    if row.get("RFE"):
        return "RFE"
    if row.get("Dossier envoye"):
        return "Envoyé"
    return "En cours"

df["Statut"] = df.apply(compute_status, axis=1)

# ======================================================
# 🔹 KPI (style minimal + dynamique)
# ======================================================
kpi_style = """
<style>
div[data-testid="stMetricValue"] { font-size:20px !important; }
</style>
"""
st.markdown(kpi_style, unsafe_allow_html=True)

st.subheader("📌 Indicateurs")

k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("Dossiers", len(df))
k2.metric("Honoraires", f"${df['Montant honoraires (US $)'].sum():,.0f}")
k3.metric("Autres frais", f"${df['Autres frais (US $)'].sum():,.0f}")
k4.metric("Facturé", f"${df['Total facturé'].sum():,.0f}")
k5.metric("Encaissé", f"${df['Montant encaissé'].sum():,.0f}")
k6.metric("Solde", f"${df['Solde'].sum():,.0f}")

st.markdown("---")

# ======================================================
# 🔹 FILTERS
# ======================================================
st.subheader("🧩 Filtres")

colA, colB, colC, colD, colE, colF, colG = st.columns([1,1,1,1,1,1,1])

# Category
cat_list = ["Toutes"] + sorted(visa_table["Categories"].unique().tolist())
cat = colA.selectbox("Catégorie", cat_list)

# Sous-cat
if cat != "Toutes":
    souscat_list = ["Toutes"] + sorted(
        visa_table[visa_table["Categories"] == cat]["Sous-categories"].unique().tolist()
    )
else:
    souscat_list = ["Toutes"] + sorted(visa_table["Sous-categories"].unique().tolist())

souscat = colB.selectbox("Sous-catégorie", souscat_list)

# Visa
if souscat != "Toutes":
    visa_list = ["Tous"] + sorted(
        visa_table[visa_table["Sous-categories"] == souscat]["Visa"].unique().tolist()
    )
elif cat != "Toutes":
    visa_list = ["Tous"] + sorted(
        visa_table[visa_table["Categories"] == cat]["Visa"].unique().tolist()
    )
else:
    visa_list = ["Tous"] + sorted(visa_table["Visa"].unique().tolist())

visa_choice = colC.selectbox("Visa", visa_list)

# Année
annee = colD.selectbox("Année", ["Toutes"] + sorted(df["Année"].unique().tolist()))

# Dates
date_debut = colE.date_input("Date début")
date_fin = colF.date_input("Date fin")

# Statuts
statuts = ["Tous", "En cours", "Envoyé", "Accepté", "Refusé", "Annulé", "RFE"]
statut_choice = colG.selectbox("Statut", statuts)

# ======================================================
# 🔹 APPLY FILTERS
# ======================================================
filtered = df.copy()

if cat != "Toutes":
    filtered = filtered[filtered["Categories"] == cat]

if souscat != "Toutes":
    filtered = filtered[filtered["Sous-categories"] == souscat]

if visa_choice != "Tous":
    filtered = filtered[filtered["Visa"] == visa_choice]

if annee != "Toutes":
    filtered = filtered[filtered["Année"] == annee]

if statut_choice != "Tous":
    filtered = filtered[filtered["Statut"] == statut_choice]

if date_debut:
    filtered = filtered[filtered["Date"] >= pd.to_datetime(date_debut)]

if date_fin:
    filtered = filtered[filtered["Date"] <= pd.to_datetime(date_fin)]

# ======================================================
# 🔹 TABLE
# ======================================================
st.subheader("📋 Dossiers filtrés")
st.dataframe(filtered, use_container_width=True, height=600)
