import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database
from utils.visa_filters import clean_visa_df

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("📊 Tableau de bord – Berenbaum Law App")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
visa_raw = pd.DataFrame(db.get("visa", []))

if not clients:
    st.warning("Aucun dossier trouvé dans Dropbox.")
    st.stop()

df = pd.DataFrame(clients)

# ---------------------------------------------------------
# NORMALISATION VISA TABLE
# ---------------------------------------------------------
visa_table = clean_visa_df(visa_raw)

# ---------------------------------------------------------
# NORMALISATION CLIENTS
# ---------------------------------------------------------

df["Date"] = pd.to_datetime(df.get("Date"), errors="coerce")

num_cols = [
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4"
]

for c in num_cols:
    if c not in df.columns:
        df[c] = 0
    df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

df["Total facturé"] = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
df["Montant encaissé"] = df["Acompte 1"] + df["Acompte 2"] + df["Acompte 3"] + df["Acompte 4"]
df["Solde"] = df["Total facturé"] - df["Montant encaissé"]
df["Année"] = df["Date"].dt.year

# ---------------------------------------------------------
# FILTRES PÉRIODE 1
# ---------------------------------------------------------
st.subheader("🎛️ Filtres – Période 1")

colA, colB, colC, colD, colE, colF = st.columns(6)

# Catégories réelles
real_categories = sorted(
    set(visa_table["Categories"].dropna().astype(str))
    - set(visa_table["Sous-categories"].dropna().astype(str))
)

cat1 = colA.selectbox("Catégorie", ["Toutes"] + real_categories)
if cat1 != "Toutes":
    souscat_list1 = ["Toutes"] + sorted(
        visa_table.loc[visa_table["Categories"] == cat1, "Sous-categories"]
        .dropna().unique().tolist()
    )
else:
    souscat_list1 = ["Toutes"] + sorted(
        visa_table["Sous-categories"].dropna().unique().tolist()
    )
souscat1 = colB.selectbox("Sous-catégorie", souscat_list1)

if souscat1 != "Toutes":
    visa_list1 = ["Tous"] + sorted(
        visa_table.loc[visa_table["Sous-categories"] == souscat1, "Visa"]
        .dropna().unique().tolist()
    )
elif cat1 != "Toutes":
    visa_list1 = ["Tous"] + sorted(
        visa_table.loc[visa_table["Categories"] == cat1, "Visa"]
        .dropna().unique().tolist()
    )
else:
    visa_list1 = ["Tous"] + sorted(visa_table["Visa"].dropna().unique().tolist())

visa1 = colC.selectbox("Visa", visa_list1)

annee1 = colD.selectbox("Année", ["Toutes"] + sorted(df["Année"].dropna().unique().tolist()))
date_debut1 = colE.date_input("Début P1")
date_fin1 = colF.date_input("Fin P1")

# -------------------- APPLY FILTER P1 --------------------
df1 = df.copy()

if cat1 != "Toutes":
    df1 = df1[df1["Catégories"] == cat1]
if souscat1 != "Toutes":
    df1 = df1[df1["Sous-catégories"] == souscat1]
if visa1 != "Tous":
    df1 = df1[df1["Visa"] == visa1]
if annee1 != "Toutes":
    df1 = df1[df1["Année"] == annee1]
df1 = df1[df1["Date"] >= pd.to_datetime(date_debut1)]
df1 = df1[df1["Date"] <= pd.to_datetime(date_fin1)]

# ---------------------------------------------------------
# FILTRES PÉRIODE 2
# ---------------------------------------------------------
st.subheader("🎛️ Filtres – Période 2 (Comparaison)")

colA2, colB2, colC2, colD2, colE2, colF2 = st.columns(6)

cat2 = colA2.selectbox("Catégorie P2", ["Toutes"] + real_categories, index=0)
if cat2 != "Toutes":
    souscat_list2 = ["Toutes"] + sorted(
        visa_table.loc[visa_table["Categories"] == cat2, "Sous-categories"]
        .dropna().unique().tolist()
    )
else:
    souscat_list2 = ["Toutes"] + sorted(
        visa_table["Sous-categories"].dropna().unique().tolist()
    )
souscat2 = colB2.selectbox("Sous-cat P2", souscat_list2)

if souscat2 != "Toutes":
    visa_list2 = ["Tous"] + sorted(
        visa_table.loc[visa_table["Sous-categories"] == souscat2, "Visa"]
        .dropna().unique().tolist()
    )
elif cat2 != "Toutes":
    visa_list2 = ["Tous"] + sorted(
        visa_table.loc[visa_table["Categories"] == cat2, "Visa"]
        .dropna().unique().tolist()
    )
else:
    visa_list2 = ["Tous"] + sorted(visa_table["Visa"].dropna().unique().tolist())

visa2 = colC2.selectbox("Visa P2", visa_list2)
annee2 = colD2.selectbox("Année P2", ["Toutes"] + sorted(df["Année"].dropna().unique().tolist()))
date_debut2 = colE2.date_input("Début P2")
date_fin2 = colF2.date_input("Fin P2")

# -------------------- APPLY FILTER P2 --------------------
df2 = df.copy()

if cat2 != "Toutes":
    df2 = df2[df2["Catégories"] == cat2]
if souscat2 != "Toutes":
    df2 = df2[df2["Sous-catégories"] == souscat2]
if visa2 != "Tous":
    df2 = df2[df2["Visa"] == visa2]
if annee2 != "Toutes":
    df2 = df2[df2["Année"] == annee2]
df2 = df2[df2["Date"] >= pd.to_datetime(date_debut2)]
df2 = df2[df2["Date"] <= pd.to_datetime(date_fin2)]

# ---------------------------------------------------------
# KPI COMPARATIFS (TABLEAU)
# ---------------------------------------------------------
st.subheader("📊 Comparaison des KPI entre les deux périodes")

def kpi(df):
    return {
        "Dossiers": len(df),
        "Honoraires": df["Montant honoraires (US $)"].sum(),
        "Autres frais": df["Autres frais (US $)"].sum(),
        "Facturé": df["Total facturé"].sum(),
        "Encaissé": df["Montant encaissé"].sum(),
        "Solde": df["Solde"].sum()
    }

k1 = kpi(df1)
k2 = kpi(df2)

comparison = pd.DataFrame({
    "KPI": k1.keys(),
    "Période 1": k1.values(),
    "Période 2": k2.values(),
    "Différence": [b - a for a, b in zip(k1.values(), k2.values())],
    "% évolution": [((b - a) / a * 100) if a != 0 else 0 for a, b in zip(k1.values(), k2.values())],
})

st.dataframe(comparison, use_container_width=True)

# ---------------------------------------------------------
# TABLEAU P1
# ---------------------------------------------------------
st.subheader("📋 Dossiers – Période 1")
st.dataframe(df1, use_container_width=True)

# ---------------------------------------------------------
# TABLEAU P2
# ---------------------------------------------------------
st.subheader("📋 Dossiers – Période 2")
st.dataframe(df2, use_container_width=True)
