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
# NORMALISATION
# ---------------------------------------------------------
# Dossier N en string (support xxxxx-1)
df["Dossier N"] = df.get("Dossier N", "").astype(str)

# Statuts
df = normalize_status_columns(df)

# Dates
df["Date"] = pd.to_datetime(df.get("Date", None), errors="coerce")
df["Année"] = df["Date"].dt.year

# Numériques
def to_float(x):
    try:
        return float(x or 0)
    except Exception:
        return 0.0

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

# Champs texte pour filtres
for col in ["Categories", "Sous-categories", "Visa"]:
    if col not in df.columns:
        df[col] = ""
    df[col] = df[col].astype(str).fillna("")

# ---------------------------------------------------------
# FILTRES (dont Soldés / Solde >0 / Solde <0)
# ---------------------------------------------------------
st.subheader("🧰 Filtres")

c1, c2, c3, c4, c5 = st.columns(5)

# Multi-années
years = sorted([y for y in df["Année"].dropna().unique().tolist() if pd.notna(y)])
years_int = [int(y) for y in years]
annees_sel = c1.multiselect("Années", options=years_int, default=years_int)

# Catégorie / Sous-cat / Visa
cat_list = ["Tous"] + sorted([x for x in df["Categories"].dropna().unique().tolist() if x.strip() != ""])
categorie_sel = c2.selectbox("Catégorie", options=cat_list)

if categorie_sel != "Tous":
    df_cat = df[df["Categories"] == categorie_sel]
else:
    df_cat = df

sous_list = ["Tous"] + sorted([x for x in df_cat["Sous-categories"].dropna().unique().tolist() if x.strip() != ""])
sous_sel = c3.selectbox("Sous-catégorie", options=sous_list)

if sous_sel != "Tous":
    df_sous = df_cat[df_cat["Sous-categories"] == sous_sel]
else:
    df_sous = df_cat

visa_list = ["Tous"] + sorted([x for x in df_sous["Visa"].dropna().unique().tolist() if x.strip() != ""])
visa_sel = c4.selectbox("Visa", options=visa_list)

# ✅ FILTRE SOLDE (rétabli)
solde_filter = c5.selectbox(
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

# ✅ Solde (rétabli)
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

k1, k2, k3, k4, k5, k6, k7 = st.columns(7)

nb = len(df_filt)
hon = df_filt["Montant honoraires (US $)"].sum()
frais = df_filt["Autres frais (US $)"].sum()
tot = df_filt["Total facturé"].sum()
enc = df_filt["Total encaissé"].sum()
solde_sum = df_filt["Solde"].sum()

# Statuts
accepted = int(df_filt.get("Dossier accepte", pd.Series([False]*len(df_filt))).apply(normalize_bool).sum())
refused = int(df_filt.get("Dossier refuse", pd.Series([False]*len(df_filt))).apply(normalize_bool).sum())
annules = int(df_filt.get("Dossier Annule", pd.Series([False]*len(df_filt))).apply(normalize_bool).sum())

k1.metric("Dossiers", nb)
k2.metric("Honoraires", f"${hon:,.2f}")
k3.metric("Autres frais", f"${frais:,.2f}")
k4.metric("Total facturé", f"${tot:,.2f}")
k5.metric("Total encaissé", f"${enc:,.2f}")
k6.metric("Solde (somme)", f"${solde_sum:,.2f}")
k7.metric("Annulés", annules)

k8, k9 = st.columns(2)
k8.metric("Acceptés", accepted)
k9.metric("Refusés", refused)

st.markdown("---")

# ---------------------------------------------------------
# COURBES MULTI-ANNÉES (existant + sécurisé)
# ---------------------------------------------------------
st.subheader("📈 Courbes multi-années")

df_month = df_filt.copy()
df_month["Mois"] = df_month["Date"].dt.to_period("M").astype(str)

if df_month["Mois"].dropna().empty:
    st.info("Aucune donnée datée exploitable pour tracer les courbes.")
else:
    agg = df_month.groupby(["Mois"], as_index=False).agg(
        Dossiers=("Dossier N", "count"),
        Total_facture=("Total facturé", "sum"),
        Total_encaisse=("Total encaissé", "sum"),
        Solde=("Solde", "sum"),
    )

    metric_choice = st.selectbox(
        "Indicateur",
        ["Dossiers", "Total_facture", "Total_encaisse", "Solde"],
        index=0
    )

    fig = px.line(agg, x="Mois", y=metric_choice, markers=True)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------
# TABLEAU DETAIL
# ---------------------------------------------------------
st.subheader("📋 Dossiers (détail)")

cols = [
    "Dossier N", "Nom", "Date", "Categories", "Sous-categories", "Visa",
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Total facturé", "Total encaissé", "Solde",
    "Dossier envoye", "Dossier accepte", "Dossier refuse", "Dossier Annule", "RFE",
]
cols_display = [c for c in cols if c in df_filt.columns]

st.dataframe(
    df_filt.sort_values(["Date", "Dossier N"], ascending=[False, True])[cols_display],
    use_container_width=True,
)