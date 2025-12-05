import streamlit as st
import pandas as pd
import plotly.express as px
from backend.dropbox_utils import load_database
from utils.visa_filters import clean_visa_df
from components.export_pdf import generate_pdf_from_dataframe

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="Analyses", page_icon="📊", layout="wide")
st.title("📊 Analyses avancées du cabinet")

db = load_database()
clients = pd.DataFrame(db.get("clients", []))
visa_raw = pd.DataFrame(db.get("visa", []))
visa_table = clean_visa_df(visa_raw)

if clients.empty:
    st.warning("Aucun dossier disponible.")
    st.stop()

# ---------------------------------------------------------
# NORMALISATION
# ---------------------------------------------------------
df = clients.copy()

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

num_cols = [
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4"
]

for col in num_cols:
    df[col] = pd.to_numeric(df.get(col, 0), errors="coerce").fillna(0)

df["Total facturé"] = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
df["Montant encaissé"] = df["Acompte 1"] + df["Acompte 2"] + df["Acompte 3"] + df["Acompte 4"]
df["Solde"] = df["Total facturé"] - df["Montant encaissé"]
df["Année"] = df["Date"].dt.year

# ---------------------------------------------------------
# FILTRES
# ---------------------------------------------------------
st.subheader("🎛️ Filtres généraux")

colA, colB, colC, colD, colE, colF = st.columns(6)

# Catégories réelles
real_categories = sorted(
    set(visa_table["Categories"]) - set(visa_table["Sous-categories"])
)
cat = colA.selectbox("Catégorie", ["Toutes"] + real_categories)

# Sous-catégories dépendantes
if cat != "Toutes":
    souscat_list = sorted(visa_table[visa_table["Categories"] == cat]["Sous-categories"].unique())
else:
    souscat_list = sorted(visa_table["Sous-categories"].unique())

souscat = colB.selectbox("Sous-catégorie", ["Toutes"] + souscat_list)

# Visa dépendant
if souscat != "Toutes":
    visa_list = sorted(visa_table[visa_table["Sous-categories"] == souscat]["Visa"].unique())
elif cat != "Toutes":
    visa_list = sorted(visa_table[visa_table["Categories"] == cat]["Visa"].unique())
else:
    visa_list = sorted(visa_table["Visa"].unique())

visa_choice = colC.selectbox("Visa", ["Tous"] + visa_list)

# Année
annees = sorted(df["Année"].dropna().unique().tolist())
annee = colD.selectbox("Année", ["Toutes"] + annees)

# Dates
date_debut = colE.date_input("Date début", value=None)
date_fin = colF.date_input("Date fin", value=None)

# ---------------------------------------------------------
# APPLICATION DES FILTRES
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
# KPIs FINANCIERS
# ---------------------------------------------------------
st.subheader("📌 KPIs financiers")

k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("Dossiers", len(filtered))
k2.metric("Honoraires", f"${filtered['Montant honoraires (US $)'].sum():,.0f}")
k3.metric("Autres frais", f"${filtered['Autres frais (US $)'].sum():,.0f}")
k4.metric("Facturé", f"${filtered['Total facturé'].sum():,.0f}")
k5.metric("Encaissé", f"${filtered['Montant encaissé'].sum():,.0f}")
k6.metric("Solde", f"${filtered['Solde'].sum():,.0f}")

st.markdown("---")

# ---------------------------------------------------------
# F1 — Chiffre d’affaires mensuel
# ---------------------------------------------------------
st.subheader("💰 Évolution mensuelle du chiffre d’affaires")

df_month = filtered.copy()
df_month["Mois"] = df_month["Date"].dt.to_period("M")

month_sum = df_month.groupby("Mois")[["Total facturé", "Montant encaissé"]].sum().reset_index()

fig = px.line(
    month_sum,
    x="Mois",
    y=["Total facturé", "Montant encaissé"],
    markers=True,
    title="Chiffre d’affaires mensuel"
)
st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# F2 — Solde mensuel
# ---------------------------------------------------------
st.subheader("📉 Solde mensuel")

df_month["Solde"] = df_month["Solde"].astype(float)
month_solde = df_month.groupby("Mois")["Solde"].sum().reset_index()

fig = px.bar(month_solde, x="Mois", y="Solde", title="Solde total par mois")
st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# F3 — Taux d’encaissement
# ---------------------------------------------------------
st.subheader("📈 Taux d’encaissement (%)")

total_facture = filtered["Total facturé"].sum()
total_encaisse = filtered["Montant encaissé"].sum()

taux = (total_encaisse / total_facture * 100) if total_facture > 0 else 0
st.metric("Taux d'encaissement", f"{taux:.1f}%")

# ---------------------------------------------------------
# F5 — Comparaison Période A / Période B
# ---------------------------------------------------------
st.subheader("🆚 Comparaison de périodes")

cA, cB = st.columns(2)

date_A1 = cA.date_input("Début A", key="A1")
date_A2 = cA.date_input("Fin A", key="A2")

date_B1 = cB.date_input("Début B", key="B1")
date_B2 = cB.date_input("Fin B", key="B2")

if date_A1 and date_A2 and date_B1 and date_B2:
    dfA = df[(df["Date"] >= pd.to_datetime(date_A1)) & (df["Date"] <= pd.to_datetime(date_A2))]
    dfB = df[(df["Date"] >= pd.to_datetime(date_B1)) & (df["Date"] <= pd.to_datetime(date_B2))]

    comp = pd.DataFrame({
        "Période": ["A", "B"],
        "Facturé": [dfA["Total facturé"].sum(), dfB["Total facturé"].sum()],
        "Encaissé": [dfA["Montant encaissé"].sum(), dfB["Montant encaissé"].sum()]
    })

    st.dataframe(comp)

    fig = px.bar(comp, x="Période", y=["Facturé", "Encaissé"], barmode="group")
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# O6 — Pipeline des statuts
# ---------------------------------------------------------
st.subheader("📦 Pipeline des dossiers")

pipeline = {
    "Envoyé": filtered["Dossier envoye"].sum(),
    "Accepté": filtered["Dossier accepte"].sum(),
    "Refusé": filtered["Dossier refuse"].sum(),
    "Annulé": filtered["Dossier Annule"].sum(),
    "RFE": filtered["RFE"].sum(),
}

pipe_df = pd.DataFrame(list(pipeline.items()), columns=["Statut", "Nombre"])
fig = px.bar(pipe_df, x="Statut", y="Nombre", title="Pipeline des statuts")
st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# O8 — Taux de réussite
# ---------------------------------------------------------
st.subheader("🏆 Taux de réussite")

acceptes = filtered["Dossier accepte"].sum()
refuses = filtered["Dossier refuse"].sum()

taux = acceptes / (acceptes + refuses) * 100 if (acceptes + refuses) > 0 else 0
st.metric("Taux de réussite", f"{taux:.1f}%")

# ---------------------------------------------------------
# V9 — Répartition par Visa
# ---------------------------------------------------------
st.subheader("🛂 Répartition par Visa")

fig = px.pie(filtered, names="Visa", title="Répartition des visas")
st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# V10 — Performance Catégorie / Sous-cat
# ---------------------------------------------------------
st.subheader("📁 Performance Catégories / Sous-catégories")

df_cat = filtered.groupby(["Categories", "Sous-categories"])[["Total facturé", "Montant encaissé"]].sum().reset_index()

st.dataframe(df_cat)

fig = px.bar(df_cat, x="Categories", y="Total facturé", color="Sous-categories", title="Performance par catégorie")
st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# M1.1 — Heatmap Catégorie × Année
# ---------------------------------------------------------
st.subheader("🔥 Heatmap Catégorie × Année")

cat_heat = pd.pivot_table(filtered, values="Dossier N", index="Categories", columns="Année", aggfunc="count")

fig = px.imshow(cat_heat, text_auto=True, title="Heatmap Catégorie × Année")
st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# M1.2 — Heatmap Visa × Année
# ---------------------------------------------------------
st.subheader("🔥 Heatmap Visa × Année")

visa_heat = pd.pivot_table(filtered, values="Dossier N", index="Visa", columns="Année", aggfunc="count")

fig = px.imshow(visa_heat, text_auto=True, title="Heatmap Visa × Année")
st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# EXPORTS
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📤 Export")

c1, c2 = st.columns(2)

if c1.button("📄 Export PDF"):
    generate_pdf_from_dataframe(filtered)

if c2.download_button(
    "📥 Export Excel",
    data=filtered.to_excel(index=False),
    file_name="analyse.xlsx"
):
    pass
