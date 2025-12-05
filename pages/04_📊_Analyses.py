import streamlit as st
import pandas as pd
import plotly.express as px
from backend.dropbox_utils import load_database
from utils.visa_filters import clean_visa_df


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="Analyses", page_icon="📊", layout="wide")
st.title("📊 Analyses & Statistiques – Berenbaum Law App")


# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
visa_raw = pd.DataFrame(db.get("visa", []))

if not clients:
    st.warning("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)
visa_table = clean_visa_df(visa_raw)

# ---------------------------------------------------------
# NORMALISATION
# ---------------------------------------------------------
df["Date"] = pd.to_datetime(df.get("Date"), errors="coerce")
df["Année"] = df["Date"].dt.year
df["Mois"] = df["Date"].dt.to_period("M").astype(str)

num_cols = [
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4"
]

for c in num_cols:
    df[c] = pd.to_numeric(df.get(c, 0), errors="coerce").fillna(0)

df["Total facturé"] = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
df["Montant encaissé"] = df["Acompte 1"] + df["Acompte 2"] + df["Acompte 3"] + df["Acompte 4"]
df["Solde"] = df["Total facturé"] - df["Montant encaissé"]


# ---------------------------------------------------------
# FILTRES
# ---------------------------------------------------------
st.subheader("🎛️ Filtres")

colA, colB, colC, colD, colE, colF = st.columns(6)

# Catégories
cat_list = ["Toutes"] + sorted(
    set(visa_table["Categories"]) - set(visa_table["Sous-categories"])
)
cat = colA.selectbox("Catégorie", cat_list)

# Sous-catégories
if cat != "Toutes":
    souscat_list = ["Toutes"] + sorted(
        visa_table[visa_table["Categories"] == cat]["Sous-categories"].unique()
    )
else:
    souscat_list = ["Toutes"] + sorted(visa_table["Sous-categories"].unique())

souscat = colB.selectbox("Sous-catégorie", souscat_list)

# Visa
if souscat != "Toutes":
    visa_list = ["Tous"] + sorted(
        visa_table[visa_table["Sous-categories"] == souscat]["Visa"].unique()
    )
elif cat != "Toutes":
    visa_list = ["Tous"] + sorted(
        visa_table[visa_table["Categories"] == cat]["Visa"].unique()
    )
else:
    visa_list = ["Tous"] + sorted(visa_table["Visa"].unique())

visa_choice = colC.selectbox("Visa", visa_list)

# Année
annees = ["Toutes"] + sorted(df["Année"].dropna().unique().tolist())
annee = colD.selectbox("Année", annees)

# Date range
date_debut = colE.date_input("Date début")
date_fin = colF.date_input("Date fin")

# Statut dossier
colS1, colS2, colS3, colS4, colS5 = st.columns(5)
f_envoye = colS1.checkbox("Envoyé")
f_accepte = colS2.checkbox("Accepté")
f_refuse = colS3.checkbox("Refusé")
f_annule = colS4.checkbox("Annulé")
f_rfe = colS5.checkbox("RFE")


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

# Statuts
if f_envoye:
    filtered = filtered[filtered["Dossier envoye"] == True]
if f_accepte:
    filtered = filtered[filtered["Dossier accepte"] == True]
if f_refuse:
    filtered = filtered[filtered["Dossier refuse"] == True]
if f_annule:
    filtered = filtered[filtered["Dossier Annule"] == True]
if f_rfe:
    filtered = filtered[filtered["RFE"] == True]


# ---------------------------------------------------------
# KPI APRES FILTRE
# ---------------------------------------------------------
st.subheader("📌 Indicateurs après filtres")

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Dossiers", len(filtered))
k2.metric("Honoraires", f"${filtered['Montant honoraires (US $)'].sum():,.0f}")
k3.metric("Autres frais", f"${filtered['Autres frais (US $)'].sum():,.0f}")
k4.metric("Facturé", f"${filtered['Total facturé'].sum():,.0f}")
k5.metric("Encaissé", f"${filtered['Montant encaissé'].sum():,.0f}")
k6.metric("Solde", f"${filtered['Solde'].sum():,.0f}")


# ---------------------------------------------------------
# GRAPHIQUES
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📈 Analyses graphiques")

if len(filtered) == 0:
    st.info("Aucun dossier ne correspond aux filtres.")
    st.stop()

# 📌 Honoraires par mois
fig1 = px.bar(
    filtered.groupby("Mois")["Montant honoraires (US $)"].sum().reset_index(),
    x="Mois", y="Montant honoraires (US $)",
    title="Honoraires par mois"
)
st.plotly_chart(fig1, use_container_width=True)

# 📌 Répartition catégories
fig2 = px.pie(
    filtered,
    names="Categories",
    title="Répartition par catégories"
)
st.plotly_chart(fig2, use_container_width=True)

# 📌 Répartition Visa
fig3 = px.pie(
    filtered,
    names="Visa",
    title="Répartition par type de visa"
)
st.plotly_chart(fig3, use_container_width=True)

# 📌 Statuts dossiers
fig4 = px.bar(
    pd.DataFrame({
        "Envoyé": [filtered["Dossier envoye"].sum()],
        "Accepté": [filtered["Dossier accepte"].sum()],
        "Refusé": [filtered["Dossier refuse"].sum()],
        "Annulé": [filtered["Dossier Annule"].sum()],
        "RFE": [filtered["RFE"].sum()],
    }).T.reset_index().rename(columns={"index": "Statut", 0: "Total"}),
    x="Statut", y="Total",
    title="Statut des dossiers"
)
st.plotly_chart(fig4, use_container_width=True)

# ---------------------------------------------------------
# TABLEAU PIVOT ANALYTIQUE
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📊 Tableau analytique")

pivot = filtered.pivot_table(
    index="Categories",
    values=["Montant honoraires (US $)", "Autres frais (US $)", "Total facturé", "Montant encaissé", "Solde"],
    aggfunc="sum"
)

st.dataframe(pivot, use_container_width=True)
