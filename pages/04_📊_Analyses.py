# pages/04_📊_Analyses.py
import streamlit as st
import pandas as pd
import plotly.express as px

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database
from utils.status_utils import normalize_status_columns, normalize_bool

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="📊 Analyses", page_icon="📊", layout="wide")
render_sidebar()
st.title("📊 Analyses & Statistiques")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients).copy()

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def to_float(x):
    try:
        return float(x or 0)
    except Exception:
        return 0.0

def safe_str(x):
    return "" if x is None else str(x)

# ---------------------------------------------------------
# NORMALISATION
# ---------------------------------------------------------
# Dossier N en string (support xxxxx-1)
if "Dossier N" not in df.columns:
    df["Dossier N"] = ""
df["Dossier N"] = df["Dossier N"].astype(str).fillna("").str.strip()

# Normalisation statuts (crée les colonnes canoniques)
df = normalize_status_columns(df)

# Dates
if "Date" not in df.columns:
    df["Date"] = None
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Année"] = df["Date"].dt.year

# Colonnes texte pour filtres
for col in ["Categories", "Sous-categories", "Visa", "Nom"]:
    if col not in df.columns:
        df[col] = ""
    df[col] = df[col].apply(safe_str).fillna("").str.strip()

# Numériques
for c in ["Montant honoraires (US $)", "Autres frais (US $)"]:
    if c not in df.columns:
        df[c] = 0.0
    df[c] = df[c].apply(to_float)

for i in range(1, 5):
    col = f"Acompte {i}"
    if col not in df.columns:
        df[col] = 0.0
    df[col] = df[col].apply(to_float)

df["Total facturé"] = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
df["Total encaissé"] = df[[f"Acompte {i}" for i in range(1, 5)]].sum(axis=1)
df["Solde"] = df["Total facturé"] - df["Total encaissé"]

# ---------------------------------------------------------
# FILTRES
# ---------------------------------------------------------
st.subheader("🧰 Filtres")

c1, c2, c3, c4 = st.columns(4)

# Multi-années
years = sorted([int(y) for y in df["Année"].dropna().unique().tolist() if pd.notna(y)])
annees_sel = c1.multiselect("Années", options=years, default=years)

# Catégorie / Sous-cat / Visa (dépendants)
cat_list = ["Tous"] + sorted([x for x in df["Categories"].unique().tolist() if x and x.strip()])
categorie_sel = c2.selectbox("Catégorie", options=cat_list)

df_cat = df[df["Categories"] == categorie_sel] if categorie_sel != "Tous" else df
sous_list = ["Tous"] + sorted([x for x in df_cat["Sous-categories"].unique().tolist() if x and x.strip()])
sous_sel = c3.selectbox("Sous-catégorie", options=sous_list)

df_sous = df_cat[df_cat["Sous-categories"] == sous_sel] if sous_sel != "Tous" else df_cat
visa_list = ["Tous"] + sorted([x for x in df_sous["Visa"].unique().tolist() if x and x.strip()])
visa_sel = c4.selectbox("Visa", options=visa_list)

# Statuts + Solde (ligne séparée, plus lisible)
c5, c6 = st.columns(2)

statut_sel = c5.selectbox(
    "Statut du dossier",
    options=["Tous", "Envoyé", "Accepté", "Refusé", "Annulé", "RFE"],
    index=0,
)

solde_filter = c6.selectbox(
    "Filtre Solde",
    options=[
        "Tous",
        "Dossiers soldés (Solde ≤ 0)",
        "Solde > 0 (non soldés)",
        "Solde < 0 (surpayés)",
    ],
    index=0,
)

# ---------------------------------------------------------
# APPLICATION FILTRES
# ---------------------------------------------------------
df_filt = df.copy()

# Années
if annees_sel:
    df_filt = df_filt[df_filt["Année"].isin(annees_sel)]

# Catégorie
if categorie_sel != "Tous":
    df_filt = df_filt[df_filt["Categories"] == categorie_sel]

# Sous-catégorie
if sous_sel != "Tous":
    df_filt = df_filt[df_filt["Sous-categories"] == sous_sel]

# Visa
if visa_sel != "Tous":
    df_filt = df_filt[df_filt["Visa"] == visa_sel]

# Statut
if statut_sel != "Tous":
    mapping = {
        "Envoyé": "Dossier envoye",
        "Accepté": "Dossier accepte",
        "Refusé": "Dossier refuse",
        "Annulé": "Dossier Annule",
        "RFE": "RFE",
    }
    col = mapping[statut_sel]
    if col not in df_filt.columns:
        df_filt[col] = False
    df_filt = df_filt[df_filt[col].apply(normalize_bool) == True]

# Solde
if solde_filter == "Dossiers soldés (Solde ≤ 0)":
    df_filt = df_filt[df_filt["Solde"] <= 0]
elif solde_filter == "Solde > 0 (non soldés)":
    df_filt = df_filt[df_filt["Solde"] > 0]
elif solde_filter == "Solde < 0 (surpayés)":
    df_filt = df_filt[df_filt["Solde"] < 0]

# ---------------------------------------------------------
# KPI
# ---------------------------------------------------------
st.subheader("📌 KPI")

nb = len(df_filt)
hon = df_filt["Montant honoraires (US $)"].sum()
frais = df_filt["Autres frais (US $)"].sum()
tot = df_filt["Total facturé"].sum()
enc = df_filt["Total encaissé"].sum()
solde_sum = df_filt["Solde"].sum()

envoyes = int(df_filt.get("Dossier envoye", pd.Series([False]*len(df_filt))).apply(normalize_bool).sum())
acceptes = int(df_filt.get("Dossier accepte", pd.Series([False]*len(df_filt))).apply(normalize_bool).sum())
refuses = int(df_filt.get("Dossier refuse", pd.Series([False]*len(df_filt))).apply(normalize_bool).sum())
annules = int(df_filt.get("Dossier Annule", pd.Series([False]*len(df_filt))).apply(normalize_bool).sum())
rfe = int(df_filt.get("RFE", pd.Series([False]*len(df_filt))).apply(normalize_bool).sum())

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Dossiers", nb)
k2.metric("Honoraires", f"${hon:,.2f}")
k3.metric("Autres frais", f"${frais:,.2f}")
k4.metric("Total facturé", f"${tot:,.2f}")
k5.metric("Total encaissé", f"${enc:,.2f}")
k6.metric("Solde (somme)", f"${solde_sum:,.2f}")

k7, k8, k9, k10, k11 = st.columns(5)
k7.metric("Envoyés", envoyes)
k8.metric("Acceptés", acceptes)
k9.metric("Refusés", refuses)
k10.metric("Annulés", annules)   # ✅ ajouté / conservé
k11.metric("RFE", rfe)

st.markdown("---")

# ---------------------------------------------------------
# GRAPHIQUES INTERACTIFS
# ---------------------------------------------------------
st.subheader("📊 Graphiques interactifs")

tab1, tab2, tab3, tab4 = st.tabs([
    "📅 Volumes par mois",
    "📈 Courbes multi-années",
    "💰 Facturé vs encaissé",
    "🧩 Répartition Catégories",
])

# --- Tab 1 : Volumes par mois
with tab1:
    df_m = df_filt.copy()
    df_m["Mois"] = df_m["Date"].dt.to_period("M").astype(str)

    if df_m["Mois"].dropna().empty:
        st.info("Aucune donnée datée exploitable pour tracer l'histogramme mensuel.")
    else:
        agg = df_m.groupby("Mois", as_index=False).agg(Dossiers=("Dossier N", "count"))
        fig = px.bar(agg, x="Mois", y="Dossiers")
        st.plotly_chart(fig, use_container_width=True)

# --- Tab 2 : Courbes multi-années
with tab2:
    df_line = df_filt.copy()
    df_line["Mois"] = df_line["Date"].dt.to_period("M").astype(str)

    if df_line["Mois"].dropna().empty:
        st.info("Aucune donnée datée exploitable pour tracer les courbes.")
    else:
        agg = df_line.groupby(["Année", "Mois"], as_index=False).agg(
            Total_facture=("Total facturé", "sum"),
            Total_encaisse=("Total encaissé", "sum"),
            Solde=("Solde", "sum"),
        )

        metric_choice = st.selectbox(
            "Indicateur (multi-années)",
            ["Total_facture", "Total_encaisse", "Solde"],
            index=0
        )

        fig = px.line(
            agg,
            x="Mois",
            y=metric_choice,
            color="Année",
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)

# --- Tab 3 : Facturé vs encaissé
with tab3:
    df_line2 = df_filt.copy()
    df_line2["Mois"] = df_line2["Date"].dt.to_period("M").astype(str)

    if df_line2["Mois"].dropna().empty:
        st.info("Aucune donnée datée exploitable pour tracer Facturé vs Encaissé.")
    else:
        agg = df_line2.groupby("Mois", as_index=False).agg(
            Total_facture=("Total facturé", "sum"),
            Total_encaisse=("Total encaissé", "sum"),
        )
        fig = px.line(agg, x="Mois", y=["Total_facture", "Total_encaisse"], markers=True)
        st.plotly_chart(fig, use_container_width=True)

# --- Tab 4 : Répartition catégories
with tab4:
    if df_filt.empty:
        st.info("Aucun dossier pour la répartition.")
    else:
        agg = df_filt.groupby("Categories", as_index=False).agg(Dossiers=("Dossier N", "count"))
        fig = px.pie(agg, names="Categories", values="Dossiers")
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------
# TABLEAU DETAIL
# ---------------------------------------------------------
st.subheader("📋 Dossiers (détail)")

cols = [
    "Dossier N", "Nom", "Date",
    "Categories", "Sous-categories", "Visa",
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Total facturé", "Total encaissé", "Solde",
    "Dossier envoye", "Dossier accepte", "Dossier refuse", "Dossier Annule", "RFE",
]
cols_display = [c for c in cols if c in df_filt.columns]

st.dataframe(
    df_filt.sort_values(["Date", "Dossier N"], ascending=[False, True])[cols_display],
    use_container_width=True,
)