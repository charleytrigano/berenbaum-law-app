import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Tableau de bord – Berenbaum Law App")
db = load_database()

clients = pd.DataFrame(db.get("clients", []))
visa_df = pd.DataFrame(db.get("visa", []))

if clients.empty:
    st.info("Aucun dossier trouvé.")
    st.stop()

# Normalisation dates et montants
clients["Date"] = pd.to_datetime(clients["Date"], errors="coerce")
for col in [
    "Montant honoraires (US $)",
    "Autres frais (US $)",
    "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4"
]:
    clients[col] = pd.to_numeric(clients.get(col, 0), errors="coerce").fillna(0)

clients["Total facturé"] = clients["Montant honoraires (US $)"] + clients["Autres frais (US $)"]
clients["Montant encaissé"] = (
    clients["Acompte 1"] + clients["Acompte 2"] + clients["Acompte 3"] + clients["Acompte 4"]
)
clients["Solde"] = clients["Total facturé"] - clients["Montant encaissé"]

# KPIs en 1 ligne
st.subheader("📌 Indicateurs")
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Dossiers", len(clients))
c2.metric("Honoraires", f"${clients['Montant honoraires (US $)'].sum():,.2f}")
c3.metric("Autres frais", f"${clients['Autres frais (US $)'].sum():,.2f}")
c4.metric("Facturé", f"${clients['Total facturé'].sum():,.2f}")
c5.metric("Encaissé", f"${clients['Montant encaissé'].sum():,.2f}")
c6.metric("Solde", f"${clients['Solde'].sum():,.2f}")

st.markdown("---")

# Filtres simples
st.subheader("🎛️ Filtres rapides")

cat_list = ["Toutes"] + sorted(clients["Catégories"].dropna().unique().tolist())
souscat_list = ["Toutes"] + sorted(clients["Sous-catégories"].dropna().unique().tolist())
visa_list = ["Tous"] + sorted(clients["Visa"].dropna().unique().tolist())

colA, colB, colC = st.columns(3)
f_cat = colA.selectbox("Catégorie", cat_list)
f_scat = colB.selectbox("Sous-catégorie", souscat_list)
f_visa = colC.selectbox("Visa", visa_list)

filtered = clients.copy()
if f_cat != "Toutes":
    filtered = filtered[filtered["Catégories"] == f_cat]
if f_scat != "Toutes":
    filtered = filtered[filtered["Sous-catégories"] == f_scat]
if f_visa != "Tous":
    filtered = filtered[filtered["Visa"] == f_visa]

st.subheader("📋 Aperçu des dossiers")
cols = ["Dossier N", "Nom", "Catégories", "Sous-catégories", "Visa", "Date"]
show_cols = [c for c in cols if c in filtered.columns]
st.dataframe(filtered[show_cols], use_container_width=True, height=450)
