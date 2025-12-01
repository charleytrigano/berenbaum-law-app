import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Tableau de bord – Berenbaum Law App")
st.write("Bienvenue dans l'application professionnelle de gestion des dossiers.")

db = load_database()
clients = db.get("clients", [])
visa_table = pd.DataFrame(db.get("visa", []))  # table Visa XLSX structurée

if not clients:
    st.info("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)

# --------------------------------------------
# Normalisation des colonnes financières
# --------------------------------------------
cols_num = [
    "Montant honoraires (US $)",
    "Autres frais (US $)",
    "Acompte 1",
    "Acompte 2",
    "Acompte 3",
    "Acompte 4"
]

for col in cols_num:
    if col not in df.columns:
        df[col] = 0
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

df["Total facturé"] = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
df["Montant encaissé"] = df["Acompte 1"] + df["Acompte 2"] + df["Acompte 3"] + df["Acompte 4"]
df["Solde"] = df["Total facturé"] - df["Montant encaissé"]

# --------------------------------------------
# KPI — version lisible
# --------------------------------------------
def kpi(title, value):
    st.markdown(f"""
        <div style="
            background:#f1f3f6;
            padding:18px;
            border-radius:10px;
            text-align:center;
            width:100%;
        ">
            <div style="font-size:20px; font-weight:700;">{value}</div>
            <div style="font-size:13px; color:#555;">{title}</div>
        </div>
    """, unsafe_allow_html=True)

st.subheader("📌 Indicateurs principaux")

col1, col2, col3, col4, col5, col6 = st.columns(6)
kpi("Nombre de dossiers", len(df))
kpi("Total honoraires", f"${df['Montant honoraires (US $)'].sum():,.2f}")
kpi("Total autres frais", f"${df['Autres frais (US $)'].sum():,.2f}")
kpi("Total facturé", f"${df['Total facturé'].sum():,.2f}")
kpi("Montant encaissé", f"${df['Montant encaissé'].sum():,.2f}")
kpi("Solde restant", f"${df['Solde'].sum():,.2f}")

st.markdown("---")

# --------------------------------------------
# FILTRES DYNAMIQUES
# --------------------------------------------
st.subheader("🎛️ Filtres")

colA, colB, colC = st.columns(3)

# 1️⃣ Catégorie
cat_list = ["Toutes"] + sorted(visa_table["Categories"].dropna().unique().tolist())
cat_filter = colA.selectbox("Catégorie", cat_list)

# 2️⃣ Sous-catégorie dépendante
if cat_filter != "Toutes":
    souscat_list = visa_table[visa_table["Categories"] == cat_filter]["Sous-categorie"].dropna().unique().tolist()
else:
    souscat_list = visa_table["Sous-categorie"].dropna().unique().tolist()

souscat_filter = colB.selectbox("Sous-catégorie", ["Toutes"] + sorted(souscat_list))

# 3️⃣ Visa dépendant des 2 filtres précédents
if cat_filter != "Toutes" and souscat_filter != "Toutes":
    visa_list = visa_table[
        (visa_table["Categories"] == cat_filter) &
        (visa_table["Sous-categorie"] == souscat_filter)
    ]["Visa"].dropna().unique().tolist()
elif cat_filter != "Toutes":
    visa_list = visa_table[visa_table["Categories"] == cat_filter]["Visa"].dropna().unique().tolist()
else:
    visa_list = visa_table["Visa"].dropna().unique().tolist()

visa_filter = colC.selectbox("Visa", ["Tous"] + sorted(visa_list))

# --------------------------------------------
# Application des filtres sur DF clients
# --------------------------------------------
filtered = df.copy()

if cat_filter != "Toutes":
    filtered = filtered[filtered["Catégories"] == cat_filter]

if souscat_filter != "Toutes":
    filtered = filtered[filtered["Sous-catégories"] == souscat_filter]

if visa_filter != "Tous":
    filtered = filtered[filtered["Visa"] == visa_filter]

# --------------------------------------------
# AFFICHAGE RESULTAT
# --------------------------------------------
st.subheader("📋 Dossiers filtrés")

colonnes_aff = [
    "Dossier N", "Nom", "Catégories", "Sous-catégories", "Visa",
    "Montant honoraires (US $)", "Autres frais (US $)", "Total facturé",
    "Montant encaissé", "Solde"
]

colonnes_aff = [c for c in colonnes_aff if c in filtered.columns]

st.dataframe(filtered[colonnes_aff], use_container_width=True, height=500)
