import streamlit as st
import pandas as pd
import plotly.express as px
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

numeric_cols = [
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4"
]

for col in numeric_cols:
    df[col] = pd.to_numeric(df.get(col, 0), errors="coerce").fillna(0)

df["Total facturé"] = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
df["Montant encaissé"] = df["Acompte 1"] + df["Acompte 2"] + df["Acompte 3"] + df["Acompte 4"]
df["Solde"] = df["Total facturé"] - df["Montant encaissé"]

# ---------------------------------------------------------
# ONGLET - NAVIGATION
# ---------------------------------------------------------
tabs = st.tabs([
    "📌 KPI & Vue générale",
    "📈 Performance",
    "💰 Finance",
    "👥 Productivité",
    "📤 Export"
])


# ======================================================================
# 📌 TAB 1 : KPI & VUE GLOBALE
# ======================================================================
with tabs[0]:

    st.subheader("🎛️ Filtres globaux")

    colA, colB, colC, colD = st.columns(4)

    cat = colA.selectbox("Catégorie", ["Toutes"] + sorted(df["Categories"].dropna().unique()))
    souscat = colB.selectbox("Sous-catégorie", ["Toutes"] + sorted(df["Sous-categories"].dropna().unique()))
    visa_choice = colC.selectbox("Visa", ["Tous"] + sorted(df["Visa"].dropna().unique()))
    annee = colD.selectbox("Année", ["Toutes"] + sorted(df["Année"].dropna().unique()))

    # ---- Application filtres ----
    filtered = df.copy()

    if cat != "Toutes":
        filtered = filtered[filtered["Categories"] == cat]
    if souscat != "Toutes":
        filtered = filtered[filtered["Sous-categories"] == souscat]
    if visa_choice != "Tous":
        filtered = filtered[filtered["Visa"] == visa_choice]
    if annee != "Toutes":
        filtered = filtered[filtered["Année"] == annee]

    st.markdown("---")
    st.subheader("📌 KPI après filtres")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("Dossiers", len(filtered))
    col2.metric("Honoraires", f"${filtered['Montant honoraires (US $)'].sum():,.0f}")
    col3.metric("Autres frais", f"${filtered['Autres frais (US $)'].sum():,.0f}")
    col4.metric("Facturé", f"${filtered['Total facturé'].sum():,.0f}")
    col5.metric("Encaissé", f"${filtered['Montant encaissé'].sum():,.0f}")
    col6.metric("Solde", f"${filtered['Solde'].sum():,.0f}")

    st.markdown("---")
    st.subheader("📋 Données filtrées")

    st.dataframe(filtered, use_container_width=True, height=600)


# ======================================================================
# 📈 TAB 2 : PERFORMANCE
# ======================================================================
with tabs[1]:

    st.subheader("📈 Évolution annuelle")
    yearly = filtered.groupby("Année")["Total facturé"].sum().reset_index()
    st.plotly_chart(px.bar(yearly, x="Année", y="Total facturé"), use_container_width=True)

    # -------- 2. Évolution mensuelle --------
st.subheader("📅 Évolution mensuelle")

# Sécurisation colonne Mois dans filtered
filtered["Mois"] = filtered["Date"].dt.to_period("M").astype(str)

monthly = filtered.groupby("Mois")["Total facturé"].sum().reset_index()

fig = px.line(monthly, x="Mois", y="Total facturé", title="Facturation mensuelle")
st.plotly_chart(fig, use_container_width=True)

    st.subheader("🔥 Heatmap Catégorie × Année")
    heat1 = pd.pivot_table(filtered, values="Dossier N", index="Categories",
                           columns="Année", aggfunc="count", fill_value=0)

    st.plotly_chart(px.imshow(heat1, text_auto=True), use_container_width=True)

    st.subheader("🔥 Heatmap Visa × Année")
    heat2 = pd.pivot_table(filtered, values="Dossier N", index="Visa",
                           columns="Année", aggfunc="count", fill_value=0)

    st.plotly_chart(px.imshow(heat2, text_auto=True), use_container_width=True)


# ======================================================================
# 💰 TAB 3 : FINANCE
# ======================================================================
with tabs[2]:

    st.subheader("💰 Total facturé par année")
    filtered["Mois"] = filtered["Date"].dt.to_period("M").astype(str)
    st.plotly_chart(
        px.bar(df.groupby("Année")["Total facturé"].sum().reset_index(),
               x="Année", y="Total facturé"),
        use_container_width=True
    )

    st.subheader("💸 Total encaissé par année")
    st.plotly_chart(
        px.line(df.groupby("Année")["Montant encaissé"].sum().reset_index(),
                x="Année", y="Montant encaissé"),
        use_container_width=True
    )

    st.subheader("📉 Solde par année")
    st.plotly_chart(
        px.bar(df.groupby("Année")["Solde"].sum().reset_index(),
               x="Année", y="Solde"),
        use_container_width=True
    )


# ======================================================================
# 👥 TAB 4 : PRODUCTIVITÉ
# ======================================================================
with tabs[3]:

    st.subheader("🏷️ Dossiers par catégorie")
    st.plotly_chart(
        px.bar(df["Categories"].value_counts().reset_index(),
               x="index", y="Categories", labels={"index": "Catégorie", "Categories": "Nb"}),
        use_container_width=True
    )

    st.subheader("🏷️ Dossiers par sous-catégorie")
    st.plotly_chart(
        px.bar(df["Sous-categories"].value_counts().reset_index(),
               x="index", y="Sous-categories",
               labels={"index": "Sous-catégorie", "Sous-categories": "Nb"}),
        use_container_width=True
    )

    st.subheader("👥 Top 10 clients")
    st.dataframe(df[["Nom", "Total facturé"]].sort_values("Total facturé", ascending=False).head(10))

    st.subheader("🛂 Top 10 Visas")
    st.dataframe(df["Visa"].value_counts().head(10))


# ======================================================================
# 📤 TAB 5 : EXPORT
# ======================================================================
with tabs[4]:

    st.subheader("📤 Export des données filtrées")

    col1, col2, col3 = st.columns(3)

    # ---- EXPORT EXCEL ----
    excel_bytes = filtered.to_csv(index=False).encode("utf-8")
    col1.download_button(
        "📄 Export Excel",
        data=excel_bytes,
        file_name="analyse.xlsx",
        mime="text/csv"
    )

    # ---- EXPORT CSV ----
    col2.download_button(
        "📄 Export CSV",
        data=excel_bytes,
        file_name="analyse.csv",
        mime="text/csv"
    )

    # ---- EXPORT PDF ----
    pdf_bytes = generate_pdf_from_dataframe(filtered)
    col3.download_button(
        "📕 Export PDF",
        data=pdf_bytes,
        file_name="analyse.pdf",
        mime="application/pdf"
    )
