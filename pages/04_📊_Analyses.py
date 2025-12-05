import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database
from components.export_pdf import generate_pdf_from_dataframe

st.set_page_config(page_title="Analyses", page_icon="📊", layout="wide")
st.title("📊 Analyses des dossiers")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
df = pd.DataFrame(clients)

if df.empty:
    st.warning("Aucun dossier trouvé.")
    st.stop()

# ---------------------------------------------------------
# NORMALISATION
# ---------------------------------------------------------
df["Date"] = pd.to_datetime(df.get("Date"), errors="coerce")
df["Année"] = df["Date"].dt.year

num_cols = [
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4"
]
for col in num_cols:
    df[col] = pd.to_numeric(df.get(col, 0), errors="coerce").fillna(0)

df["Total facturé"] = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
df["Montant encaissé"] = df["Acompte 1"] + df["Acompte 2"] + df["Acompte 3"] + df["Acompte 4"]
df["Solde"] = df["Total facturé"] - df["Montant encaissé"]

# Nettoyage statuts
status_cols = ["Dossier envoye", "Dossier accepte", "Dossier refuse", "Dossier Annule", "RFE"]
for c in status_cols:
    df[c] = pd.to_numeric(df.get(c, 0), errors="coerce").fillna(0).astype(int)

# ---------------------------------------------------------
# FILTRES
# ---------------------------------------------------------
st.subheader("🎛️ Filtres")

colA, colB, colC, colD = st.columns(4)

categories = ["Toutes"] + sorted(df["Categories"].fillna("").unique().tolist())
cat = colA.selectbox("Catégorie", categories)

souscats = ["Toutes"] + sorted(df["Sous-categories"].fillna("").unique().tolist())
souscat = colB.selectbox("Sous-catégorie", souscats)

visas = ["Tous"] + sorted(df["Visa"].fillna("").unique().tolist())
visa = colC.selectbox("Visa", visas)

annees = ["Toutes"] + sorted(df["Année"].dropna().unique().tolist())
annee = colD.selectbox("Année", annees)

# Filtre dates
colD1, colD2 = st.columns(2)
date_debut = colD1.date_input("Date début", value=None)
date_fin = colD2.date_input("Date fin", value=None)

# Période 2 (comparaison)
st.markdown("### 📅 Comparaison de période")
colP1, colP2 = st.columns(2)
period2_start = colP1.date_input("Période 2 – début", value=None)
period2_end = colP2.date_input("Période 2 – fin", value=None)

# ---------------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------------
filtered = df.copy()

if cat != "Toutes":
    filtered = filtered[filtered["Categories"] == cat]

if souscat != "Toutes":
    filtered = filtered[filtered["Sous-categories"] == souscat]

if visa != "Tous":
    filtered = filtered[filtered["Visa"] == visa]

if annee != "Toutes":
    filtered = filtered[filtered["Année"] == annee]

if date_debut:
    filtered = filtered[filtered["Date"] >= pd.to_datetime(date_debut)]
if date_fin:
    filtered = filtered[filtered["Date"] <= pd.to_datetime(date_fin)]

# ---------------------------------------------------------
# KPI DYNAMIQUES
# ---------------------------------------------------------
st.subheader("📌 Indicateurs")

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Dossiers", len(filtered))
k2.metric("Honoraires", f"${filtered['Montant honoraires (US $)'].sum():,.0f}")
k3.metric("Autres frais", f"${filtered['Autres frais (US $)'].sum():,.0f}")
k4.metric("Facturé", f"${filtered['Total facturé'].sum():,.0f}")
k5.metric("Encaissé", f"${filtered['Montant encaissé'].sum():,.0f}")
k6.metric("Solde", f"${filtered['Solde'].sum():,.0f}")

# ---------------------------------------------------------
# STATUTS
# ---------------------------------------------------------
st.markdown("### 📌 Statuts")

stat_df = pd.DataFrame({
    "Statut": ["Envoyé", "Accepté", "Refusé", "Annulé", "RFE"],
    "Total": [
        filtered["Dossier envoye"].sum(),
        filtered["Dossier accepte"].sum(),
        filtered["Dossier refuse"].sum(),
        filtered["Dossier Annule"].sum(),
        filtered["RFE"].sum()
    ]
})

st.dataframe(stat_df, use_container_width=True, height=200)

# ---------------------------------------------------------
# COMPARAISON PÉRIODE 1 vs PÉRIODE 2
# ---------------------------------------------------------
if period2_start and period2_end:
    st.markdown("### 📊 Comparaison de périodes")

    df1 = df[(df["Date"] >= pd.to_datetime(date_debut)) & (df["Date"] <= pd.to_datetime(date_fin))]
    df2 = df[(df["Date"] >= pd.to_datetime(period2_start)) & (df["Date"] <= pd.to_datetime(period2_end))]

    comp = pd.DataFrame({
        "Indicateur": ["Dossiers", "Honoraires", "Autres frais", "Facturé", "Encaissé", "Solde"],
        "Période 1": [
            len(df1),
            df1["Montant honoraires (US $)"].sum(),
            df1["Autres frais (US $)"].sum(),
            df1["Total facturé"].sum(),
            df1["Montant encaissé"].sum(),
            df1["Solde"].sum()
        ],
        "Période 2": [
            len(df2),
            df2["Montant honoraires (US $)"].sum(),
            df2["Autres frais (US $)"].sum(),
            df2["Total facturé"].sum(),
            df2["Montant encaissé"].sum(),
            df2["Solde"].sum()
        ]
    })

    st.dataframe(comp, use_container_width=True, height=300)

# ---------------------------------------------------------
# EXPORTS
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📤 Export")

colExp1, colExp2 = st.columns(2)

with colExp1:
    st.download_button(
        "📥 Télécharger Excel",
        data=filtered.to_excel(index=False, engine="openpyxl"),
        file_name="analyses.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with colExp2:
    pdf_bytes = generate_pdf_from_dataframe(filtered)
    st.download_button(
        "📄 Télécharger PDF",
        data=pdf_bytes,
        file_name="analyses.pdf",
        mime="application/pdf"
    )
