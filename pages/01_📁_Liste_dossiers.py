import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

st.set_page_config(page_title="Liste des dossiers", page_icon="📁", layout="wide")

st.title("📁 Liste des dossiers")

db = load_database()
clients = pd.DataFrame(db.get("clients", []))
visa_df = pd.DataFrame(db.get("visa", []))

if clients.empty:
    st.info("Aucun dossier enregistré.")
    st.stop()

clients["Date"] = pd.to_datetime(clients["Date"], errors="coerce")

# KPI
st.subheader("📌 Indicateurs")
c1, c2, c3 = st.columns(3)
c1.metric("Total", len(clients))
c2.metric("Total facturé", f"${clients['Montant honoraires (US $)'].sum():,.2f}")
c3.metric("Solde", f"${(clients['Montant honoraires (US $)'].sum() - clients['Acompte 1'].sum()):,.2f}")

st.markdown("---")

# Filtres basés sur la grille VISAS
cat_list = ["Toutes"] + sorted(visa_df["Categories"].dropna().unique().tolist())
f_cat = st.selectbox("Catégorie", cat_list)

if f_cat != "Toutes":
    scat_list = ["Toutes"] + sorted(visa_df[visa_df["Categories"] == f_cat]["Sous-categories"].unique())
else:
    scat_list = ["Toutes"] + sorted(visa_df["Sous-categories"].unique())

f_scat = st.selectbox("Sous-catégorie", scat_list)

if f_scat != "Toutes":
    visa_list = ["Tous"] + sorted(visa_df[visa_df["Sous-categories"] == f_scat]["Visa"].unique())
else:
    visa_list = ["Tous"] + sorted(visa_df["Visa"].unique())

f_visa = st.selectbox("Visa", visa_list)

filtered = clients.copy()
if f_cat != "Toutes":
    filtered = filtered[filtered["Catégories"] == f_cat]
if f_scat != "Toutes":
    filtered = filtered[filtered["Sous-catégories"] == f_scat]
if f_visa != "Tous":
    filtered = filtered[filtered["Visa"] == f_visa]

st.dataframe(filtered, use_container_width=True, height=700)
