import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database


# =====================================================================
# PAGE SETUP
# =====================================================================
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("📊 Tableau de bord – Berenbaum Law App")


# =====================================================================
# LOAD DATABASE
# =====================================================================
db = load_database()
clients = db.get("clients", [])
visa_raw = pd.DataFrame(db.get("visa", []))

if not clients:
    st.warning("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)


# =====================================================================
# NORMALISATION VISA (TRÈS IMPORTANT)
# =====================================================================
def clean_visa_df(dfv):
    if dfv is None or dfv.empty:
        return pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

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

    for col in ["Categories", "Sous-categories", "Visa"]:
        if col not in dfv.columns:
            dfv[col] = ""

    dfv["Categories"] = dfv["Categories"].astype(str).str.strip()
    dfv["Sous-categories"] = dfv["Sous-categories"].astype(str).str.strip()
    dfv["Visa"] = dfv["Visa"].astype(str).str.strip()

    return dfv


visa_table = clean_visa_df(visa_raw)


# =====================================================================
# NORMALISATION CLIENTS
# =====================================================================
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


# =====================================================================
# KPI DESIGN
# =====================================================================
st.markdown("""
<style>
.big-metric div[data-testid="stMetricValue"] {
    font-size: 18px !important;
}
</style>
""", unsafe_allow_html=True)

st.subheader("📌 Indicateurs globaux")

k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("Dossiers", len(df))
k2.metric("Honoraires", f"${df['Montant honoraires (US $)'].sum():,.0f}")
k3.metric("Autres frais", f"${df['Autres frais (US $)'].sum():,.0f}")
k4.metric("Facturé", f"${df['Total facturé'].sum():,.0f}")
k5.metric("Encaissé", f"${df['Montant encaissé'].sum():,.0f}")
k6.metric("Solde", f"${df['Solde'].sum():,.0f}")

st.markdown("---")


# =====================================================================
# FILTRES
# =====================================================================
st.subheader("🎛️ Filtres")

colA, colB, colC, colD, colE, colF, colG = st.columns([1,1,1,1,1,1,1])

# -------------------- CATÉGORIES --------------------
real_cats = sorted(
    set(visa_table["Categories"]) - set(visa_table["Sous-categories"])
)
cat_list = ["Toutes"] + real_cats
cat = colA.selectbox("Catégorie", cat_list)

# -------------------- SOUS-CATÉGORIES --------------------
if cat != "Toutes":
    souscat_list = ["Toutes"] + sorted(
        visa_table.loc[visa_table["Categories"] == cat]["Sous-categories"].unique()
    )
else:
    souscat_list = ["Toutes"] + sorted(visa_table["Sous-categories"].unique())

souscat = colB.selectbox("Sous-catégorie", souscat_list)

# -------------------- VISA --------------------
if souscat != "Toutes":
    visa_list = ["Tous"] + sorted(
        visa_table.loc[visa_table["Sous-categories"] == souscat]["Visa"].unique()
    )
elif cat != "Toutes":
    visa_list = ["Tous"] + sorted(
        visa_table.loc[visa_table["Categories"] == cat]["Visa"].unique()
    )
else:
    visa_list = ["Tous"] + sorted(visa_table["Visa"].unique())

visa_choice = colC.selectbox("Visa", visa_list)

# -------------------- STATUT --------------------
statuts = ["Tous", "En cours", "Envoyé", "Accepté", "Refusé", "Annulé", "RFE"]
statut = colD.selectbox("Statut dossier", statuts)

# -------------------- ANNÉE --------------------
annee_list = ["Toutes"] + sorted(df["Année"].dropna().unique().tolist())
annee = colE.selectbox("Année", annee_list)

# -------------------- DATES --------------------
date_debut = colF.date_input("Date début")
date_fin = colG.date_input("Date fin")


# =====================================================================
# APPLICATION DES FILTRES
# =====================================================================
filtered = df.copy()

if cat != "Toutes":
    filtered = filtered[filtered["Catégories"] == cat]

if souscat != "Toutes":
    filtered = filtered[filtered["Sous-catégories"] == souscat]

if visa_choice != "Tous":
    filtered = filtered[filtered["Visa"] == visa_choice]

if statut != "Tous":
    if statut == "En cours":
        filtered = filtered[
            (filtered["Envoye"] != True) &
            (filtered["Accepte"] != True) &
            (filtered["Refuse"] != True) &
            (filtered["Annule"] != True)
        ]
    elif statut == "Envoyé":
        filtered = filtered[filtered["Envoye"] == True]
    elif statut == "Accepté":
        filtered = filtered[filtered["Accepte"] == True]
    elif statut == "Refusé":
        filtered = filtered[filtered["Refuse"] == True]
    elif statut == "Annulé":
        filtered = filtered[filtered["Annule"] == True]
    elif statut == "RFE":
        filtered = filtered[filtered["RFE"] == True]

if annee != "Toutes":
    filtered = filtered[filtered["Année"] == annee]

if date_debut:
    filtered = filtered[filtered["Date"] >= pd.to_datetime(date_debut)]

if date_fin:
    filtered = filtered[filtered["Date"] <= pd.to_datetime(date_fin)]


# =====================================================================
# KPI FILTRÉS
# =====================================================================
st.subheader("📌 Indicateurs après filtres")

f1, f2, f3, f4, f5, f6 = st.columns(6)
f1.metric("Dossiers", len(filtered))
f2.metric("Honoraires", f"${filtered['Montant honoraires (US $)'].sum():,.0f}")
f3.metric("Autres frais", f"${filtered['Autres frais (US $)'].sum():,.0f}")
f4.metric("Facturé", f"${filtered['Total facturé'].sum():,.0f}")
f5.metric("Encaissé", f"${filtered['Montant encaissé'].sum():,.0f}")
f6.metric("Solde", f"${filtered['Solde'].sum():,.0f}")

st.markdown("---")


# =====================================================================
# TABLEAU FINAL
# =====================================================================
st.subheader("📋 Dossiers filtrés")
st.dataframe(filtered, use_container_width=True, height=700)
