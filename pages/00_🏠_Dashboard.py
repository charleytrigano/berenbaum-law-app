import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database
from utils.visa_filters import get_filtered_lists

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Tableau de bord – Berenbaum Law App")
st.write("Bienvenue dans l'application professionnelle de gestion des dossiers.")

# ---------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------
db = load_database()
clients = db.get("clients", [])
visa_table = db.get("visa", [])

if not clients:
    st.warning("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)
df_visa = pd.DataFrame(visa_table)

# ---------------------------------------------------
# NORMALISATION DES DONNÉES
# ---------------------------------------------------
df["Date"] = pd.to_datetime(df.get("Date"), errors="coerce")

# Numériques nécessaires
for col in [
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4"
]:
    df[col] = pd.to_numeric(df.get(col, 0), errors="coerce").fillna(0)

# Calculs
df["Total facturé"] = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
df["Montant encaissé"] = df["Acompte 1"] + df["Acompte 2"] + df["Acompte 3"] + df["Acompte 4"]
df["Solde"] = df["Total facturé"] - df["Montant encaissé"]

df["Année"] = df["Date"].dt.year

# ---------------------------------------------------
# KPIs DESIGN (DARK MODE FRIENDLY)
# ---------------------------------------------------
st.subheader("📌 Indicateurs principaux")

def kpi(title, value, color):
    st.markdown(
        f"""
        <div style="
            background:{color};
            padding:22px;
            border-radius:12px;
            text-align:center;
            color:white;
            font-size:23px;
            font-weight:600;">
            {value}<br>
            <span style="font-size:15px; opacity:0.85">{title}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.kpi = kpi("Dossiers", len(df), "#1E88E5")
k2.kpi = kpi("Honoraires", f"${df['Montant honoraires (US $)'].sum():,.2f}", "#6A1B9A")
k3.kpi = kpi("Autres frais", f"${df['Autres frais (US $)'].sum():,.2f}", "#00897B")
k4.kpi = kpi("Facturé", f"${df['Total facturé'].sum():,.2f}", "#F4511E")
k5.kpi = kpi("Encaissé", f"${df['Montant encaissé'].sum():,.2f}", "#3949AB")
k6.kpi = kpi("Solde", f"${df['Solde'].sum():,.2f}", "#D81B60")

st.markdown("---")

# ---------------------------------------------------
# 🎛️ FILTRES AVANCÉS
# ---------------------------------------------------
st.subheader("🎛️ Filtres")

colA, colB, colC, colD, colE = st.columns(5)

# Filtres intelligents Visa
from utils.visa_filters import get_filtered_lists, clean_visa_df

df_visa = clean_visa_df(df_visa)

cat_list, souscat_list, visa_list = get_filtered_lists(df_visa)


categorie = colA.selectbox("Catégorie", ["Toutes"] + cat_list)
souscat = colB.selectbox("Sous-catégorie", ["Toutes"] + souscat_list)

# Visa dynamique
visa_list_filtered = get_filtered_lists(df_visa, categorie, souscat)[2]
visa_choice = colC.selectbox("Visa", ["Tous"] + visa_list_filtered)

# Année
annees = sorted(df["Année"].dropna().unique().tolist())
annee = colD.selectbox("Année", ["Toutes"] + annees)

# Date à Date
date_debut = colE.date_input("Date début")
date_fin = colE.date_input("Date fin")

# ---------------------------------------------------
# APPLICATION DES FILTRES
# ---------------------------------------------------
filtered = df.copy()

if categorie != "Toutes":
    filtered = filtered[filtered["Catégories"] == categorie]

if souscat != "Toutes":
    filtered = filtered[filtered["Sous-catégories"] == souscat]

if visa_choice != "Tous":
    filtered = filtered[filtered["Visa"] == visa_choice]

if annee != "Toutes":
    filtered = filtered[filtered["Année"] == annee]

if date_debut:
    filtered = filtered[filtered["Date"] >= pd.to_datetime(date_debut)]

if date_fin:
    filtered = filtered[filtered["Date"] <= pd.to_datetime(date_fin)]

# ---------------------------------------------------
# AFFICHAGE TABLEAU
# ---------------------------------------------------
st.subheader("📋 Dossiers filtrés")

colonnes = [
    "Dossier N", "Nom", "Catégories", "Sous-catégories", "Visa",
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Total facturé", "Montant encaissé", "Solde", "Date"
]

colonnes = [c for c in colonnes if c in filtered.columns]

st.dataframe(filtered[colonnes], use_container_width=True, height=620)
