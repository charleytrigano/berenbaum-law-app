import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from backend.dropbox_utils import load_database
from components.export_pdf import generate_pdf_from_dataframe

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="Analyses", page_icon="📊", layout="wide")
st.title("📊 Analyses & Statistiques — Berenbaum Law App")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.warning("Aucune donnée trouvée dans Dropbox.")
    st.stop()

df = pd.DataFrame(clients)

# ---------------------------------------------------------
# NORMALISATION
# ---------------------------------------------------------
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Année"] = df["Date"].dt.year
df["Mois"] = df["Date"].dt.to_period("M").astype(str)

num_cols = [
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4"
]
for c in num_cols:
    df[c] = pd.to_numeric(df.get(c, 0), errors="coerce").fillna(0)

df["Total facturé"] = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
df["Montant encaissé"] = (
    df["Acompte 1"] + df["Acompte 2"] + df["Acompte 3"] + df["Acompte 4"]
)
df["Solde"] = df["Total facturé"] - df["Montant encaissé"]

# ---------------------------------------------------------
# KPIs GLOBAUX
# ---------------------------------------------------------
st.subheader("📌 Indicateurs globaux")

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Total dossiers", len(df))
col2.metric("Honoraires", f"${df['Montant honoraires (US $)'].sum():,.0f}")
col3.metric("Autres frais", f"${df['Autres frais (US $)'].sum():,.0f}")
col4.metric("Facturé", f"${df['Total facturé'].sum():,.0f}")
col5.metric("Encaissé", f"${df['Montant encaissé'].sum():,.0f}")
col6.metric("Solde", f"${df['Solde'].sum():,.0f}")

st.markdown("---")

# ---------------------------------------------------------
# FILTRES
# ---------------------------------------------------------
st.subheader("🎛️ Filtres")

colA, colB, colC, colD = st.columns(4)

cat = colA.selectbox("Catégorie", ["Toutes"] + sorted(df["Categories"].dropna().unique()))
souscat = colB.selectbox("Sous-catégorie", ["Toutes"] + sorted(df["Sous-categories"].dropna().unique()))
visa_choice = colC.selectbox("Visa", ["Tous"] + sorted(df["Visa"].dropna().unique()))
annee = colD.selectbox("Année", ["Toutes"] + sorted(df["Année"].dropna().unique()))

# ---------------- APPLY FILTERS ----------------
filtered = df.copy()

if cat != "Toutes":
    filtered = filtered[filtered["Categories"] == cat]
if souscat != "Toutes":
    filtered = filtered[filtered["Sous-categories"] == souscat]
if visa_choice != "Tous":
    filtered = filtered[filtered["Visa"] == visa_choice]
if annee != "Toutes":
    filtered = filtered[filtered["Année"] == annee]

# ---------------------------------------------------------
# KPIs FILTRÉS
# ---------------------------------------------------------
st.subheader("📌 Indicateurs après filtres")

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Dossiers", len(filtered))
col2.metric("Honoraires", f"${filtered['Montant honoraires (US $)'].sum():,.0f}")
col3.metric("Autres frais", f"${filtered['Autres frais (US $)'].sum():,.0f}")
col4.metric("Facturé", f"${filtered['Total facturé'].sum():,.0f}")
col5.metric("Encaissé", f"${filtered['Montant encaissé'].sum():,.0f}")
col6.metric("Solde", f"${filtered['Solde'].sum():,.0f}")

st.markdown("---")

# ---------------------------------------------------------
# 📊 GRAPHIQUES
# ---------------------------------------------------------

# -------- 1. Evolution par année --------
st.subheader("📈 Évolution annuelle")
yearly = filtered.groupby("Année")["Total facturé"].sum().reset_index()
fig = px.bar(yearly, x="Année", y="Total facturé", title="Facturation annuelle")
st.plotly_chart(fig, use_container_width=True)

# -------- 2. Evolution mensuelle --------
st.subheader("📆 Évolution mensuelle")
monthly = filtered.groupby("Mois")["Total facturé"].sum().reset_index()
fig = px.line(monthly, x="Mois", y="Total facturé", markers=True, title="Facturation mensuelle")
st.plotly_chart(fig, use_container_width=True)

# -------- 3. Répartition catégorie --------
st.subheader("📊 Répartition par catégorie")
cat_count = filtered["Categories"].value_counts().reset_index()
cat_count.columns = ["Catégorie", "Nb"]
fig = px.pie(cat_count, names="Catégorie", values="Nb", title="Répartition par catégorie")
st.plotly_chart(fig, use_container_width=True)

# -------- 4. Heatmap catégorie × année --------
st.subheader("🔥 Heatmap Catégorie × Année")
cat_heat = pd.pivot_table(
    filtered,
    values="Dossier N",
    index="Categories",
    columns="Année",
    aggfunc="count",
    fill_value=0
)
fig = px.imshow(cat_heat, text_auto=True, title="Heatmap Catégorie × Année")
st.plotly_chart(fig, use_container_width=True)

# -------- 5. Heatmap visa × année --------
st.subheader("🔥 Heatmap Visa × Année")
visa_heat = pd.pivot_table(
    filtered,
    values="Dossier N",
    index="Visa",
    columns="Année",
    aggfunc="count",
    fill_value=0
)
fig = px.imshow(visa_heat, text_auto=True, title="Heatmap Visa × Année")
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------
# 📤 EXPORTS — FIX EXCEL ERROR
# ---------------------------------------------------------

st.subheader("📤 Export des données filtrées")

col1, col2, col3 = st.columns(3)

# -------- Excel --------
excel_buffer = BytesIO()
filtered.to_excel(excel_buffer, index=False, engine="openpyxl")
excel_buffer.seek(0)

with col1:
    st.download_button(
        "📄 Export Excel",
        data=excel_buffer,
        file_name="analyse.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# -------- CSV --------
with col2:
    st.download_button(
        "📄 Export CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="analyse.csv",
        mime="text/csv"
    )

from components.report_builder import build_pdf_report

# KPI pour PDF
kpis_dict = {
    "dossiers": len(filtered),
    "honoraires": f"{filtered['Montant honoraires (US $)'].sum():,.0f} $",
    "autres_frais": f"{filtered['Autres frais (US $)'].sum():,.0f} $",
    "facture": f"{filtered['Total facturé'].sum():,.0f} $",
    "encaisse": f"{filtered['Montant encaissé'].sum():,.0f} $",
    "solde": f"{filtered['Solde'].sum():,.0f} $",
}

charts = [fig]  # tu ajoutes tous les figs que tu veux dans cette liste

pdf_path = build_pdf_report(filtered, charts, kpis_dict)

with open(pdf_path, "rb") as pdf_file:
    st.download_button(
        "📕 Export PDF Professionnel",
        data=pdf_file,
        file_name="rapport_berenbaum.pdf",
        mime="application/pdf"
    )

