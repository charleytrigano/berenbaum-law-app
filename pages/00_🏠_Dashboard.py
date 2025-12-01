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

# ---------------------------------------------------
# ⭐ KPI — Mode sombre + Couleurs + Icônes + Glass
# ---------------------------------------------------

def kpi_glass(title, value, bg, icon):
    st.markdown(f"""
        <div style="
            background: {bg};
            backdrop-filter: blur(6px);
            padding: 18px;
            border-radius: 16px;
            text-align: center;
            width: 100%;
            border: 1px solid rgba(255,255,255,0.15);
            box-shadow: 0 4px 12px rgba(0,0,0,0.35);
        ">
            <div style="font-size: 26px; margin-bottom: 6px;">{icon}</div>
            <div style="font-size: 22px; font-weight: 700; color: white;">
                {value}
            </div>
            <div style="font-size: 14px; margin-top: 4px; color: #e0e0e0;">
                {title}
            </div>
        </div>
    """, unsafe_allow_html=True)


st.subheader("📌 Indicateurs principaux")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    kpi_glass(
        "Nombre de dossiers",
        len(df),
        "rgba(30,136,229,0.35)",   # bleu transparent
        "📁"
    )

with col2:
    kpi_glass(
        "Total honoraires",
        f"${df['Montant honoraires (US $)'].sum():,.2f}",
        "rgba(142,36,170,0.35)",   # violet transparent
        "💼"
    )

with col3:
    kpi_glass(
        "Total autres frais",
        f"${df['Autres frais (US $)'].sum():,.2f}",
        "rgba(0,150,136,0.35)",     # turquoise
        "🧾"
    )

with col4:
    kpi_glass(
        "Total facturé",
        f"${df['Total facturé'].sum():,.2f}",
        "rgba(121,85,72,0.35)",     # marron clair
        "💰"
    )

with col5:
    kpi_glass(
        "Montant encaissé",
        f"${df['Montant encaissé'].sum():,.2f}",
        "rgba(46,125,50,0.35)",     # vert
        "🏦"
    )

with col6:
    kpi_glass(
        "Solde restant",
        f"${df['Solde'].sum():,.2f}",
        "rgba(251,140,0,0.35)",      # orange
        "📉"
    )

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
