import streamlit as st
import pandas as pd
import plotly.express as px
from backend.dropbox_utils import load_database
from utils.visa_filters import clean_visa_df

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="Analyses & Statistiques", page_icon="📊", layout="wide")
st.title("📊 Analyses & Statistiques – Berenbaum Law App")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)

# Nettoyage Date
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# ---------------------------------------------------------
# NORMALISATION DES CHAMPS
# ---------------------------------------------------------
bool_cols = ["Dossier envoye", "Dossier accepte", "Dossier refuse", "Dossier Annule", "RFE"]
for c in bool_cols:
    if c not in df:
        df[c] = False
    df[c] = df[c].astype(bool)

numeric_cols = ["Montant honoraires (US $)", "Autres frais (US $)", "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4"]
for c in numeric_cols:
    df[c] = pd.to_numeric(df.get(c, 0), errors="coerce").fillna(0)

df["Total facture"] = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
df["Total acomptes"] = df[["Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4"]].sum(axis=1)
df["Solde"] = df["Total facture"] - df["Total acomptes"]

# ---------------------------------------------------------
# 🔎 FILTRES SIMPLES
# ---------------------------------------------------------
st.subheader("🎚️ Filtres")

colf1, colf2, colf3, colf4 = st.columns(4)

# Catégorie
cats = ["(Toutes)"] + sorted([c for c in df["Categories"].dropna().unique() if c != ""])
categorie = colf1.selectbox("Catégorie :", cats)

# Sous-catégorie dépendante
if categorie != "(Toutes)":
    souscats = ["(Toutes)"] + sorted(df[df["Categories"] == categorie]["Sous-categories"].unique())
else:
    souscats = ["(Toutes)"] + sorted(df["Sous-categories"].dropna().unique())
sous_categorie = colf2.selectbox("Sous-catégorie :", souscats)

# Visa dépendant
if sous_categorie != "(Toutes)":
    visas = ["(Toutes)"] + sorted(df[df["Sous-categories"] == sous_categorie]["Visa"].unique())
else:
    visas = ["(Toutes)"] + sorted(df["Visa"].dropna().unique())
visa = colf3.selectbox("Visa :", visas)

# Statut
statuts = ["(Tous)", "Envoyés", "Acceptés", "Refusés", "Annulés"]
statut = colf4.selectbox("Statut dossier :", statuts)

# ✔ Application filtres
fdf = df.copy()

if categorie != "(Toutes)":
    fdf = fdf[fdf["Categories"] == categorie]

if sous_categorie != "(Toutes)":
    fdf = fdf[fdf["Sous-categories"] == sous_categorie]

if visa != "(Toutes)":
    fdf = fdf[fdf["Visa"] == visa]

if statut == "Envoyés":
    fdf = fdf[fdf["Dossier envoye"] == True]
elif statut == "Acceptés":
    fdf = fdf[fdf["Dossier accepte"] == True]
elif statut == "Refusés":
    fdf = fdf[fdf["Dossier refuse"] == True]
elif statut == "Annulés":
    fdf = fdf[fdf["Dossier Annule"] == True]

# ---------------------------------------------------------
# 🌟 KPI PRINCIPAUX
# ---------------------------------------------------------
st.subheader("🌟 KPI Globaux (Filtres appliqués)")

k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("Total dossiers", len(fdf))
k2.metric("Envoyés", fdf["Dossier envoye"].sum())
k3.metric("Acceptés", fdf["Dossier accepte"].sum())
k4.metric("Refusés", fdf["Dossier refuse"].sum())
k5.metric("Honoraires (US$)", f"{fdf['Montant honoraires (US $)'].sum():,.0f}")
k6.metric("Solde total dû", f"{fdf['Solde'].sum():,.0f}")

# ---------------------------------------------------------
# 🔥 TABLEAU DÉTAILLÉ FILTRÉ
# ---------------------------------------------------------
st.subheader("📄 Dossiers filtrés")
st.dataframe(fdf, use_container_width=True)

# ---------------------------------------------------------
# 📊 COMPARAISON MULTI-PÉRIODES
# ---------------------------------------------------------
st.markdown("---")
st.header("⏱️ Comparaison Multi-Périodes")

type_periode = st.selectbox("Type de période :", ["Mois", "Trimestre", "Année", "Date à date"])

# Génération des périodes
df["Mois"] = df["Date"].dt.to_period("M").astype(str)
df["Trimestre"] = df["Date"].dt.to_period("Q").astype(str)
df["Année"] = df["Date"].dt.year.astype(str)

if type_periode != "Date à date":
    liste_periodes = sorted(df[type_periode].dropna().unique())
    choix = st.multiselect("Périodes :", liste_periodes, max_selections=5)

else:
    colD1, colD2 = st.columns(2)
    d1 = colD1.date_input("Date début")
    d2 = colD2.date_input("Date fin")
    choix = [(d1, d2)]

if not choix:
    st.info("Sélectionnez au moins une période.")
    st.stop()

# ---------------------------------------------------------
# 📌 Construction de la comparaison
# ---------------------------------------------------------
resultats = []

for periode in choix:

    if type_periode == "Date à date":
        f = df[(df["Date"] >= pd.to_datetime(periode[0])) & (df["Date"] <= pd.to_datetime(periode[1]))]
        lib = f"{periode[0]} → {periode[1]}"
    else:
        f = df[df[type_periode] == periode]
        lib = periode

    resultats.append({
        "Période": lib,
        "Dossiers": len(f),
        "Envoyés": f["Dossier envoye"].sum(),
        "Acceptés": f["Dossier accepte"].sum(),
        "Refusés": f["Dossier refuse"].sum(),
        "Honoraires (US$)": f["Montant honoraires (US $)"].sum()
    })

comp_df = pd.DataFrame(resultats)

# ---------------------------------------------------------
# ⭐ KPI COMPARATIFS
# ---------------------------------------------------------
st.subheader("⭐ KPI Comparatifs")

cols = st.columns(len(comp_df))

for i, (_, r) in enumerate(comp_df.iterrows()):
    cols[i].metric(r["Période"], f"{r['Dossiers']} dossiers", f"{r['Honoraires (US$)']:,.0f} $")

# ---------------------------------------------------------
# 📊 GRAPH COMPARATIF
# ---------------------------------------------------------
st.subheader("📊 Graphique comparatif")

fig = px.bar(
    comp_df,
    x="Période",
    y=["Dossiers", "Acceptés", "Envoyés"],
    barmode="group",
    text_auto=True,
)
st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# 📄 TABLEAU COMPARATIF
# ---------------------------------------------------------
st.subheader("📄 Tableau comparatif")
st.dataframe(comp_df, use_container_width=True)
