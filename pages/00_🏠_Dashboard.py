import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database
from utils.visa_filters import clean_visa_df, get_souscats, get_visas, get_all_lists

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("📊 Tableau de bord – Berenbaum Law App")



# ---------------- LOAD DB ----------------
db = load_database()
df = pd.DataFrame(db.get("clients", []))
visa_raw = pd.DataFrame(db.get("visa", []))
st.error("DEBUG VISA RAW COLUMNS → " + str(list(visa_raw.columns)))
st.dataframe(visa_raw.head(), use_container_width=True)
st.stop()


# Nettoyage Visa
visa_table = clean_visa_df(visa_raw)

# ---------------- STOP SI VIDE ----------------
if df.empty:
    st.warning("Aucun dossier trouvé.")
    st.stop()

# ---------------- NORMALISATION ----------------
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
for col in ["Montant honoraires (US $)", "Autres frais (US $)",
            "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4"]:
    df[col] = pd.to_numeric(df.get(col, 0), errors="coerce").fillna(0)

df["Total facturé"] = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
df["Montant encaissé"] = df["Acompte 1"] + df["Acompte 2"] + df["Acompte 3"] + df["Acompte 4"]
df["Solde"] = df["Total facturé"] - df["Montant encaissé"]
df["Année"] = df["Date"].dt.year

# ---------------- KPI ----------------
st.subheader("📌 Indicateurs")
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Dossiers", len(df))
c2.metric("Honoraires", f"{df['Montant honoraires (US $)'].sum():,.0f} $")
c3.metric("Autres frais", f"{df['Autres frais (US $)'].sum():,.0f} $")
c4.metric("Facturé", f"{df['Total facturé'].sum():,.0f} $")
c5.metric("Encaissé", f"{df['Montant encaissé'].sum():,.0f} $")
c6.metric("Solde", f"{df['Solde'].sum():,.0f} $")

st.markdown("---")

# ---------------- FILTRES ----------------
st.subheader("🎛️ Filtres")
colA, colB, colC, colD, colE = st.columns(5)

cat_list, souscat_all, visa_all = get_all_lists(visa_table)

cat = colA.selectbox("Catégorie", ["Toutes"] + cat_list)

if cat != "Toutes":
    souscat_list = ["Toutes"] + get_souscats(visa_table, cat)
else:
    souscat_list = ["Toutes"] + souscat_all

sous = colB.selectbox("Sous-catégorie", souscat_list)

if sous != "Toutes":
    visa_list = ["Tous"] + get_visas(visa_table, sous)
else:
    visa_list = ["Tous"] + visa_all

visa_choice = colC.selectbox("Visa", visa_list)
annee = colD.selectbox("Année", ["Toutes"] + sorted(df["Année"].dropna().unique()))

date_deb = colE.date_input("Date début")
date_fin = colE.date_input("Date fin")

# ---------------- APPLY FILTERS ----------------
filtered = df.copy()

if cat != "Toutes":
    filtered = filtered[filtered["Categories"] == cat]

if sous != "Toutes":
    filtered = filtered[filtered["Sous-categories"] == sous]

if visa_choice != "Tous":
    filtered = filtered[filtered["Visa"] == visa_choice]

if annee != "Toutes":
    filtered = filtered[filtered["Année"] == annee]

if date_deb:
    filtered = filtered[filtered["Date"] >= pd.to_datetime(date_deb)]

if date_fin:
    filtered = filtered[filtered["Date"] <= pd.to_datetime(date_fin)]

# ---------------- TABLE ----------------
st.subheader("📋 Dossiers filtrés")
st.dataframe(filtered, use_container_width=True, height=600)
