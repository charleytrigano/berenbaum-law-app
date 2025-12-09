import streamlit as st
import pandas as pd
import plotly.express as px
from backend.dropbox_utils import load_database

st.set_page_config(page_title="📊 Analyses", page_icon="📊", layout="wide")
st.title("📊 Analyses & Comparaisons")


# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = pd.DataFrame(db.get("clients", []))

if clients.empty:
    st.error("Aucun dossier trouvé.")
    st.stop()


# ---------------------------------------------------------
# CLEAN DATES
# ---------------------------------------------------------
clients["Date"] = pd.to_datetime(clients["Date"], errors="coerce")
clients = clients.dropna(subset=["Date"])


# ---------------------------------------------------------
# BUILDER : PERIODE
# ---------------------------------------------------------
def get_period_label(date, mode):
    if mode == "Mois":
        return date.strftime("%Y-%m")
    if mode == "Trimestre":
        q = (date.month - 1) // 3 + 1
        return f"{date.year}-T{q}"
    if mode == "Semestre":
        s = 1 if date.month <= 6 else 2
        return f"{date.year}-S{s}"
    if mode == "Année":
        return str(date.year)
    return ""


# ---------------------------------------------------------
# FILTRES UTILISATEUR
# ---------------------------------------------------------
st.subheader("🔎 Filtres de comparaison")

colA, colB = st.columns(2)

mode = colA.selectbox(
    "Type de période",
    ["Mois", "Trimestre", "Semestre", "Année", "Date à date"],
)

n_periods = colB.slider(
    "Nombre de périodes à comparer", min_value=2, max_value=5, value=2
)

period_inputs = []

if mode == "Date à date":
    st.info("Sélectionnez 2 à 5 intervalles de dates personnalisés.")

    for i in range(n_periods):
        st.markdown(f"### Période {i+1}")
        d1 = st.date_input(f"Début P{i+1}")
        d2 = st.date_input(f"Fin P{i+1}")
        period_inputs.append((d1, d2))

else:
    st.info("Sélectionnez les périodes (2 à 5).")
    unique_periods = sorted(
        clients["Date"].apply(lambda d: get_period_label(d, mode)).unique()
    )

    for i in range(n_periods):
        p = st.selectbox(f"Période {i+1}", unique_periods, key=f"p{i}")
        period_inputs.append(p)


# ---------------------------------------------------------
# EXTRACTION DES DONNEES PAR PERIODE
# ---------------------------------------------------------
def filter_period(df, period, mode):
    if mode == "Date à date":
        start, end = period
        if not (start and end):
            return pd.DataFrame()
        return df[(df["Date"] >= pd.Timestamp(start)) & (df["Date"] <= pd.Timestamp(end))]

    mask = df["Date"].apply(lambda d: get_period_label(d, mode) == period)
    return df[mask]


period_data = []
period_labels = []

for p in period_inputs:
    dfp = filter_period(clients, p, mode)
    period_data.append(dfp)

    if mode == "Date à date":
        period_labels.append(f"{p[0]} → {p[1]}")
    else:
        period_labels.append(p)


# ---------------------------------------------------------
# KPIs & TABLEAU RÉCAP
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📘 Tableau comparatif")

kpi_table = []

for label, dfp in zip(period_labels, period_data):
    hon = dfp["Montant honoraires (US $)"].astype(float).sum()
    frais = dfp["Autres frais (US $)"].astype(float).sum()

    paid = (
        dfp["Acompte 1"].astype(float).sum()
        + dfp["Acompte 2"].astype(float).sum()
        + dfp["Acompte 3"].astype(float).sum()
        + dfp["Acompte 4"].astype(float).sum()
    )

    solde = (hon + frais) - paid

    escrow = dfp["Escrow"].sum() if "Escrow" in dfp else 0

    kpi_table.append(
        {
            "Période": label,
            "Nb dossiers": len(dfp),
            "Honoraires": hon,
            "Frais": frais,
            "Payé": paid,
            "Solde restant": solde,
            "Escrow en cours": escrow,
        }
    )

kpi_df = pd.DataFrame(kpi_table)
st.dataframe(kpi_df, width="stretch")

# ---------------------------------------------------------
# GRAPH 1 : BARRES COMPARATIVES
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📊 Comparatif par période (Barres)")

bar_df = kpi_df.melt(id_vars="Période", var_name="Indicateur", value_name="Valeur")

fig1 = px.bar(
    bar_df,
    x="Période",
    y="Valeur",
    color="Indicateur",
    barmode="group",
    title="Comparaison des indicateurs par période",
    text_auto=".2s",
)

st.plotly_chart(fig1, use_container_width=True)


# ---------------------------------------------------------
# GRAPH 2 : ÉVOLUTION MULTI-PÉRIODE
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📈 Évolution des dossiers par période")

evol_df = pd.DataFrame(
    {
        "Période": period_labels,
        "Nb dossiers": [len(dfp) for dfp in period_data],
    }
)

fig2 = px.line(
    evol_df,
    x="Période",
    y="Nb dossiers",
    markers=True,
    title="Évolution du nombre de dossiers",
)

st.plotly_chart(fig2, use_container_width=True)
