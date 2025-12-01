import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

st.set_page_config(page_title="Liste des dossiers", page_icon="📁", layout="wide")

st.title("📁 Liste des dossiers")
st.write("Visualisation, recherche et analyse filtrée des dossiers clients.")

# --------------------------------------------------------
# Charger la base
# --------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
visa_table = db.get("visa", [])

if not clients:
    st.warning("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)
df_visa = pd.DataFrame(visa_table) if len(visa_table) else pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

# --------------------------------------------------------
# Conversions & normalisations
# --------------------------------------------------------
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Montant honoraires (US $)"] = pd.to_numeric(df["Montant honoraires (US $)"], errors="coerce").fillna(0)
df["Autres frais (US $)"] = pd.to_numeric(df["Autres frais (US $)"], errors="coerce").fillna(0)

# Totaux
df["Total facturé"] = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
df["Montant encaissé"] = (
    pd.to_numeric(df.get("Acompte 1", 0), errors="coerce").fillna(0)
    + pd.to_numeric(df.get("Acompte 2", 0), errors="coerce").fillna(0)
    + pd.to_numeric(df.get("Acompte 3", 0), errors="coerce").fillna(0)
    + pd.to_numeric(df.get("Acompte 4", 0), errors="coerce").fillna(0)
)
df["Solde"] = df["Total facturé"] - df["Montant encaissé"]

# --------------------------------------------------------
# ➤ KPI (ligne unique + couleurs)
# --------------------------------------------------------
st.subheader("📌 Indicateurs")

k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("Dossiers", len(df))
k2.metric("Honoraires", f"${df['Montant honoraires (US $)'].sum():,.2f}")
k3.metric("Autres frais", f"${df['Autres frais (US $)'].sum():,.2f}")
k4.metric("Facturé", f"${df['Total facturé'].sum():,.2f}")
k5.metric("Encaissé", f"${df['Montant encaissé'].sum():,.2f}")
k6.metric("Solde", f"${df['Solde'].sum():,.2f}")

st.markdown("---")

# --------------------------------------------------------
# 🔍 Filtres intelligents
# --------------------------------------------------------

st.subheader("🎛️ Filtres")

colA, colB, colC, colD, colE = st.columns([1,1,1,1,1])

# --- Filtre Catégorie ---
liste_cat = ["Toutes"] + sorted(df_visa["Categories"].dropna().unique().tolist())
cat = colA.selectbox("Catégorie", liste_cat)

# --- Filtre Sous-catégorie dépendant ---
if cat != "Toutes":
    souscat_list = ["Toutes"] + sorted(df_visa[df_visa["Categories"] == cat]["Sous-categories"].dropna().unique())
else:
    souscat_list = ["Toutes"] + sorted(df_visa["Sous-categories"].dropna().unique())

souscat = colB.selectbox("Sous-catégorie", souscat_list)

# --- Filtre Visa dépendant ---
if souscat != "Toutes":
    visa_list = ["Tous"] + sorted(df_visa[df_visa["Sous-categories"] == souscat]["Visa"].dropna().unique())
elif cat != "Toutes":
    visa_list = ["Tous"] + sorted(df_visa[df_visa["Categories"] == cat]["Visa"].dropna().unique())
else:
    visa_list = ["Tous"] + sorted(df_visa["Visa"].dropna().unique())

visa_choice = colC.selectbox("Visa", visa_list)

# --- Filtre Année ---
df["Année"] = df["Date"].dt.year
annee_list = ["Toutes"] + sorted(df["Année"].dropna().unique().tolist())
annee = colD.selectbox("Année", annee_list)

# --- Filtre date à date ---
date_debut = colE.date_input("Date début")
date_fin = colE.date_input("Date fin")

# --------------------------------------------------------
# Application des filtres
# --------------------------------------------------------
filtered = df.copy()

if cat != "Toutes":
    filtered = filtered[filtered["Catégories"] == cat]

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

# --------------------------------------------------------
# ➤ Tableau final
# --------------------------------------------------------
st.subheader("📋 Dossiers filtrés")

colonnes = [
    "Dossier N", "Nom", "Catégories", "Sous-catégories", "Visa",
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Total facturé", "Montant encaissé", "Solde", "Date"
]

colonnes = [c for c in colonnes if c in filtered.columns]

st.dataframe(filtered[colonnes], use_container_width=True, height=600)
