import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

st.set_page_config(page_title="Liste des dossiers", page_icon="📁", layout="wide")

st.title("📁 Liste des dossiers")
st.write("Visualisation, analyse et filtres avancés basés sur Visa.xlsx.")

# -------------------------------------------------------------
# 🔄 CHARGEMENT BASE & TABLE VISA
# -------------------------------------------------------------
db = load_database()

clients = db.get("clients", [])
visa_table = db.get("visa", [])

if not clients:
    st.warning("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)
df_visa = pd.DataFrame(visa_table) if len(visa_table) else pd.DataFrame()

# -------------------------------------------------------------
# 🔧 NORMALISATION VISA (Ultra sécurisé)
# -------------------------------------------------------------
def normalize_visa(dfv):
    if dfv is None or dfv.empty:
        return pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

    rename_map = {}

    for col in dfv.columns:
        key = col.lower().replace("é", "e").replace("è", "e").strip()

        if key in ["categories", "categorie"]:
            rename_map[col] = "Categories"
        elif key in ["sous-categories", "sous-categorie", "sous-categ"]:
            rename_map[col] = "Sous-categories"
        elif key in ["visa", "visas"]:
            rename_map[col] = "Visa"

    dfv = dfv.rename(columns=rename_map)

    # colonnes obligatoires
    for c in ["Categories", "Sous-categories", "Visa"]:
        if c not in dfv.columns:
            dfv[c] = ""

    return dfv

df_visa = normalize_visa(df_visa)

# -------------------------------------------------------------
# 🔧 NORMALISATION CLIENTS
# -------------------------------------------------------------
df["Date"] = pd.to_datetime(df.get("Date"), errors="coerce")

for col in ["Montant honoraires (US $)", "Autres frais (US $)"]:
    df[col] = pd.to_numeric(df.get(col, 0), errors="coerce").fillna(0)

df["Montant encaissé"] = (
    pd.to_numeric(df.get("Acompte 1", 0), errors="coerce").fillna(0)
    + pd.to_numeric(df.get("Acompte 2", 0), errors="coerce").fillna(0)
    + pd.to_numeric(df.get("Acompte 3", 0), errors="coerce").fillna(0)
    + pd.to_numeric(df.get("Acompte 4", 0), errors="coerce").fillna(0)
)

df["Total facturé"] = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
df["Solde"] = df["Total facturé"] - df["Montant encaissé"]

# -------------------------------------------------------------
# 📌 KPI
# -------------------------------------------------------------
st.subheader("📌 Indicateurs")

k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("Dossiers", len(df))
k2.metric("Honoraires", f"${df['Montant honoraires (US $)'].sum():,.2f}")
k3.metric("Autres frais", f"${df['Autres frais (US $)'].sum():,.2f}")
k4.metric("Facturé", f"${df['Total facturé'].sum():,.2f}")
k5.metric("Encaissé", f"${df['Montant encaissé'].sum():,.2f}")
k6.metric("Solde", f"${df['Solde'].sum():,.2f}")

st.markdown("---")

# -------------------------------------------------------------
# 🎛️ FILTRES INTELLIGENTS
# -------------------------------------------------------------
st.subheader("🎛️ Filtres")

colA, colB, colC, colD, colE = st.columns(5)

# --- Filtre Catégorie ---
cat_list = ["Toutes"] + sorted(df_visa["Categories"].dropna().unique().tolist())
cat = colA.selectbox("Catégorie", cat_list)

# --- Filtre Sous-catégorie ---
if cat != "Toutes":
    souscat_list = ["Toutes"] + sorted(
        df_visa[df_visa["Categories"] == cat]["Sous-categories"].dropna().unique().tolist()
    )
else:
    souscat_list = ["Toutes"] + sorted(df_visa["Sous-categories"].dropna().unique().tolist())

souscat = colB.selectbox("Sous-catégorie", souscat_list)

# --- Filtre Visa ---
if souscat != "Toutes":
    visa_list = ["Tous"] + sorted(
        df_visa[df_visa["Sous-categories"] == souscat]["Visa"].dropna().unique().tolist()
    )
elif cat != "Toutes":
    visa_list = ["Tous"] + sorted(
        df_visa[df_visa["Categories"] == cat]["Visa"].dropna().unique().tolist()
    )
else:
    visa_list = ["Tous"] + sorted(df_visa["Visa"].dropna().unique().tolist())

visa_filter = colC.selectbox("Visa", visa_list)

# --- Filtre Année ---
df["Année"] = df["Date"].dt.year
annee_list = ["Toutes"] + sorted(df["Année"].dropna().unique().tolist())
annee = colD.selectbox("Année", annee_list)

# --- Filtre date à date ---
date_debut = colE.date_input("Date début", value=None)
date_fin = colE.date_input("Date fin", value=None)

# -------------------------------------------------------------
# 🔎 APPLICATION FILTRES
# -------------------------------------------------------------
filtered = df.copy()

if cat != "Toutes":
    filtered = filtered[filtered["Catégories"] == cat]

if souscat != "Toutes":
    filtered = filtered[filtered["Sous-catégories"] == souscat]

if visa_filter != "Tous":
    filtered = filtered[filtered["Visa"] == visa_filter]

if annee != "Toutes":
    filtered = filtered[filtered["Année"] == annee]

if date_debut:
    filtered = filtered[filtered["Date"] >= pd.to_datetime(date_debut)]

if date_fin:
    filtered = filtered[filtered["Date"] <= pd.to_datetime(date_fin)]

# -------------------------------------------------------------
# 📋 TABLEAU FINAL
# -------------------------------------------------------------
st.subheader("📋 Dossiers filtrés")

colonnes = [
    "Dossier N", "Nom", "Catégories", "Sous-catégories", "Visa",
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Total facturé", "Montant encaissé", "Solde", "Date"
]

colonnes = [c for c in colonnes if c in filtered.columns]

st.dataframe(filtered[colonnes], use_container_width=True, height=600)
