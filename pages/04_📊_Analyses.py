import streamlit as st
import pandas as pd
import plotly.express as px
import io

from backend.dropbox_utils import load_database
from utils.visa_filters import clean_visa_df
from components.export_pdf import generate_pdf_from_dataframe

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="Analyses", page_icon="📊", layout="wide")
st.title("📊 Analyses & Statistiques")

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
# NORMALISATION CLIENTS
# ---------------------------------------------------------
df["Date"] = pd.to_datetime(df.get("Date"), errors="coerce")

num_cols = [
    "Montant honoraires (US $)",
    "Autres frais (US $)",
    "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4",
]

for col in num_cols:
    df[col] = pd.to_numeric(df.get(col, 0), errors="coerce").fillna(0)

df["Total facturé"] = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
df["Montant encaissé"] = df["Acompte 1"] + df["Acompte 2"] + df["Acompte 3"] + df["Acompte 4"]
df["Solde"] = df["Total facturé"] - df["Montant encaissé"]
df["Année"] = df["Date"].dt.year

# ---------------------------------------------------------
# KPI FUNCTION
# ---------------------------------------------------------
def display_kpis(data):
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Dossiers", len(data))
    k2.metric("Honoraires", f"${data['Montant honoraires (US $)'].sum():,.0f}")
    k3.metric("Autres frais", f"${data['Autres frais (US $)'].sum():,.0f}")
    k4.metric("Facturé", f"${data['Total facturé'].sum():,.0f}")
    k5.metric("Encaissé", f"${data['Montant encaissé'].sum():,.0f}")
    k6.metric("Solde", f"${data['Solde'].sum():,.0f}")

st.subheader("📌 Indicateurs globaux")
display_kpis(df)

st.markdown("---")

# ---------------------------------------------------------
# FILTRES
# ---------------------------------------------------------
st.subheader("🎛️ Filtres")

colA, colB, colC, colD, colE, colF = st.columns(6)

# Catégories réelles
real_categories = sorted(
    set(visa_table["Categories"]) -
    set(visa_table["Sous-categories"])
)

cat_list = ["Toutes"] + real_categories
cat = colA.selectbox("Catégorie", cat_list)

# Sous-catégories
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
annees = ["Toutes"] + sorted(df["Année"].dropna().unique().tolist())
annee = colD.selectbox("Année", annees)

# Dates
date_debut = colE.date_input("Date début", value=None)
date_fin = colF.date_input("Date fin", value=None)

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
# KPI AFTER FILTERS
# ---------------------------------------------------------
st.markdown("### 🔎 Indicateurs après filtres")
display_kpis(filtered)

st.markdown("---")

# ---------------------------------------------------------
# 📊 GRAPHIQUES
# ---------------------------------------------------------

st.subheader("📈 Analyses graphiques")

# Dossiers par année
if not filtered.empty:
    df_year = filtered.groupby("Année")["Dossier N"].count().reset_index()
    st.plotly_chart(px.bar(df_year, x="Année", y="Dossier N", title="Dossiers par année"), use_container_width=True)

# Répartition par catégorie
if "Categories" in filtered.columns:
    st.plotly_chart(
        px.pie(filtered, names="Categories", title="Répartition par catégorie"),
        use_container_width=True
    )

# ---------------------------------------------------------
# EXPORTS
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📤 Export")

# -------- EXPORT EXCEL --------
buffer = io.BytesIO()
filtered.to_excel(buffer, index=False, engine="openpyxl")
buffer.seek(0)

st.download_button(
    label="📥 Télécharger Excel",
    data=buffer,
    file_name="analyses.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# -------- EXPORT PDF --------
pdf_bytes = generate_pdf_from_dataframe(filtered)

st.download_button(
    label="📄 Télécharger PDF",
    data=pdf_bytes,
    file_name="analyses.pdf",
    mime="application/pdf"
)

# -------- TABLEAU FINAL --------
st.markdown("---")
st.subheader("📋 Dossiers filtrés")
st.dataframe(filtered, use_container_width=True, height=600)
