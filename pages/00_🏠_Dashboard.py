import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

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
from utils.visa_filters import clean_visa_df


    # Normalisation des noms de colonnes
    rename_map = {}
    for col in dfv.columns:
        col_clean = col.lower().replace("é", "e").replace("è", "e").replace("ê", "e")

        if "categorie" in col_clean:
            rename_map[col] = "Categories"
        elif "sous" in col_clean:
            rename_map[col] = "Sous-categories"
        elif "visa" in col_clean:
            rename_map[col] = "Visa"

    dfv = dfv.rename(columns=rename_map)

    # Colonnes obligatoires
    for col in ["Categories", "Sous-categories", "Visa"]:
        if col not in dfv.columns:
            dfv[col] = ""

    # Nettoyage valeurs
    dfv["Categories"] = dfv["Categories"].astype(str).str.strip()
    dfv["Sous-categories"] = dfv["Sous-categories"].astype(str).str.strip()
    dfv["Visa"] = dfv["Visa"].astype(str).str.strip()

    return dfv


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
# KPI (COULEUR + TEXTE PETIT)
# ---------------------------------------------------------
st.markdown("""
<style>
.big-metric div[data-testid="stMetricValue"] {
    font-size: 18px !important;
}
</style>
""", unsafe_allow_html=True)

st.subheader("📌 Indicateurs")

k1, k2, k3, k4, k5, k6 = st.columns(6)

with k1:
    st.metric("Dossiers", len(df))

with k2:
    st.metric("Honoraires", f"${df['Montant honoraires (US $)'].sum():,.0f}")

with k3:
    st.metric("Autres frais", f"${df['Autres frais (US $)'].sum():,.0f}")

with k4:
    st.metric("Facturé", f"${df['Total facturé'].sum():,.0f}")

with k5:
    st.metric("Encaissé", f"${df['Montant encaissé'].sum():,.0f}")

with k6:
    st.metric("Solde", f"${df['Solde'].sum():,.0f}")

st.markdown("---")

# ---------------------------------------------------------
# FILTRES INTELLIGENTS
# ---------------------------------------------------------
st.subheader("🧩 Filtres")

colA, colB, colC, colD, colE, colF = st.columns([1,1,1,1,1,1])

# ---------------- CATÉGORIES réelles --------------------
real_categories = sorted(
    set(visa_table["Categories"].dropna().astype(str))
    - set(visa_table["Sous-categories"].dropna().astype(str))
)

cat_list = ["Toutes"] + real_categories
cat = colA.selectbox("Catégorie", cat_list)

# ---------------- SOUS-CATÉGORIES dépendantes ----------
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

# ---------------- VISA dépendant ------------------------
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

# ---------------- ANNÉE ------------------------
annees = ["Toutes"] + sorted(df["Année"].dropna().unique().tolist())
annee = colD.selectbox("Année", annees)

# ---------------- DATES (alignées) ---------------
date_debut = colE.date_input("Date début")
date_fin = colF.date_input("Date fin")

# ---------------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------------
filtered = df.copy()

if cat != "Toutes":
    filtered = filtered[filtered["Catégories"] == cat]

if souscat != "Toutes":
    filtered = filtered[filtered["Sous-catégories"] == souscat]

if visa_choice != "Tous":
    filtered = filtered[filtered["Visa"] == visa_choice]

if annee != "Toutes":
    filtered = filtered[filtered["Année"] == annee]

if date_debut:
    filtered = filtered[filtered["Date"] >= pd.to_datetime(date_debut)]

if date_fin:
    filtered = filtered[filtered["Date"] <= pd.to_datetime(date_fin)]

# ---------------------------------------------------------
# TABLEAU FINAL
# ---------------------------------------------------------
st.subheader("📋 Dossiers filtrés")

st.dataframe(
    filtered,
    use_container_width=True,
    height=600
)
