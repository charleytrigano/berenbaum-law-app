import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database
from utils.visa_filters import clean_visa_df

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
# NORMALISATION VISA
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
    df[c] = pd.to_numeric(df.get(c, 0), errors="coerce").fillna(0)

df["Total facturé"] = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
df["Montant encaissé"] = df["Acompte 1"] + df["Acompte 2"] + df["Acompte 3"] + df["Acompte 4"]
df["Solde"] = df["Total facturé"] - df["Montant encaissé"]
df["Année"] = df["Date"].dt.year

# ---------------------------------------------------------
# KPI STYLE
# ---------------------------------------------------------
st.markdown("""
<style>
div[data-testid="stMetricValue"] {
    font-size: 18px !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# KPI GLOBALS
# ---------------------------------------------------------
st.subheader("📌 Indicateurs (Filtres actifs)")

def show_kpis(df_local):
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Dossiers", len(df_local))
    c2.metric("Honoraires", f"${df_local['Montant honoraires (US $)'].sum():,.0f}")
    c3.metric("Autres frais", f"${df_local['Autres frais (US $)'].sum():,.0f}")
    c4.metric("Facturé", f"${df_local['Total facturé'].sum():,.0f}")
    c5.metric("Encaissé", f"${df_local['Montant encaissé'].sum():,.0f}")
    c6.metric("Solde", f"${df_local['Solde'].sum():,.0f}")

# ---------------------------------------------------------
# 🎛️ FILTRES PRINCIPAUX
# ---------------------------------------------------------
st.subheader("🎛️ Filtres")

colA, colB, colC, colD, colE, colF = st.columns([1,1,1,1,1,1])

# ---- CATÉGORIES UNIQUEMENT ----
cat_list = ["Toutes"] + sorted(visa_table["Categories"].dropna().astype(str).unique().tolist())
cat = colA.selectbox("Catégorie", cat_list)

# ---- SOUS-CATÉGORIES DÉPENDANTES ----
if cat != "Toutes":
    souscat_list = ["Toutes"] + sorted(
        visa_table.loc[visa_table["Categories"] == cat, "Sous-categories"]
        .dropna().unique().tolist()
    )
else:
    souscat_list = ["Toutes"] + sorted(
        visa_table["Sous-categories"].dropna().unique().tolist()
    )

souscat = colB.selectbox("Sous-catégorie", souscat_list)

# ---- VISA DÉPENDANT ----
if souscat != "Toutes":
    visa_list = ["Tous"] + sorted(
        visa_table.loc[visa_table["Sous-categories"] == souscat, "Visa"]
        .dropna().unique().tolist()
    )
elif cat != "Toutes":
    visa_list = ["Tous"] + sorted(
        visa_table.loc[visa_table["Categories"] == cat, "Visa"]
        .dropna().unique().tolist()
    )
else:
    visa_list = ["Tous"] + sorted(visa_table["Visa"].dropna().unique().tolist())

visa_choice = colC.selectbox("Visa", visa_list)

# ---- ANNÉE ----
annees = ["Toutes"] + sorted(df["Année"].dropna().unique().tolist())
annee = colD.selectbox("Année", annees)

# ---- DATE RANGE ----
date_debut = colE.date_input("Début")
date_fin = colF.date_input("Fin")

# ---------------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------------
filtered = df.copy()

if cat != "Toutes":
    filtered = filtered[filtered["Categories"] == cat]

if souscat != "Toutes":
    filtered = filtered[filtered["Sous-categories"] == souscat]

if visa_choice != "Tous":
    filtered = filtered[filtered["Visa"] == visa_choice]

if annee != "Toutes":
    filtered = filtered[filtered["Année"] == annee]

if date_debut:
    filtered = filtered[filtered["Date"] >= pd.to_datetime(date_debut)]

if date_fin:
    filtered = filtered[filtered["Date"] <= pd.to_datetime(date_fin)]

# ---------------------------------------------------------
# KPI MIS À JOUR
# ---------------------------------------------------------
show_kpis(filtered)

st.markdown("---")

# ---------------------------------------------------------
# 🆚 COMPARAISON ENTRE 2 PÉRIODES
# ---------------------------------------------------------
st.subheader("🆚 Comparaison entre deux périodes")

col1, col2, col3 = st.columns([1,1,1])
p1_start = col1.date_input("Période 1 - Début")
p1_end   = col1.date_input("Période 1 - Fin")

p2_start = col2.date_input("Période 2 - Début")
p2_end   = col2.date_input("Période 2 - Fin")

if col3.button("Comparer", type="primary"):

    df1 = df.copy()
    df2 = df.copy()

    # FILTRE P1
    if p1_start:
        df1 = df1[df1["Date"] >= pd.to_datetime(p1_start)]
    if p1_end:
        df1 = df1[df1["Date"] <= pd.to_datetime(p1_end)]

    # FILTRE P2
    if p2_start:
        df2 = df2[df2["Date"] >= pd.to_datetime(p2_start)]
    if p2_end:
        df2 = df2[df2["Date"] <= pd.to_datetime(p2_end)]

    st.write("### 📅 Résultats")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Période 1")
        show_kpis(df1)

    with c2:
        st.subheader("Période 2")
        show_kpis(df2)

st.markdown("---")

# ---------------------------------------------------------
# TABLEAU FINAL
# ---------------------------------------------------------
st.subheader("📋 Dossiers filtrés")

st.dataframe(
    filtered,
    use_container_width=True,
    height=600
)
