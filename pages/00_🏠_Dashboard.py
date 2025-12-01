import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database


# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Berenbaum Law App",
    page_icon="📁",
    layout="wide"
)

st.title("📊 Tableau de bord – Berenbaum Law App")
st.write("Bienvenue dans l'application professionnelle de gestion des dossiers.")


# ---------------------------------------------------
# LOAD DATABASE (Dropbox)
# ---------------------------------------------------
db = load_database()

clients = db.get("clients", [])
visa_table = db.get("visa", [])

if not clients:
    st.warning("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)

# Convertir en DataFrame propre
df_visa = pd.DataFrame(visa_table) if len(visa_table) else pd.DataFrame()


# ---------------------------------------------------
# NORMALISATION COLONNES VISA (automatique)
# ---------------------------------------------------
def normalize_columns(df):
    if df.empty:
        return df

    rename_map = {}

    for col in df.columns:
        col_clean = (
            col.lower()
               .replace("é", "e")
               .replace("è", "e")
               .replace("_", "-")
               .strip()
        )

        if col_clean in ["categories", "categorie"]:
            rename_map[col] = "Categories"

        elif col_clean in ["sous-categories", "sous-categorie", "sous-cats", "sous-categ", "souscategories"]:
            rename_map[col] = "Sous-categories"

        elif col_clean == "visa":
            rename_map[col] = "Visa"

    return df.rename(columns=rename_map)


df_visa = normalize_columns(df_visa)


# ---------------------------------------------------
# NORMALISATION CLIENTS
# ---------------------------------------------------
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

for montant_col in [
    "Montant honoraires (US $)",
    "Autres frais (US $)"
]:
    df[montant_col] = pd.to_numeric(df.get(montant_col, 0), errors="coerce").fillna(0)

# Total facturé
df["Total facturé"] = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]

# Montant encaissé
df["Montant encaissé"] = (
    pd.to_numeric(df.get("Acompte 1", 0), errors="coerce").fillna(0)
    + pd.to_numeric(df.get("Acompte 2", 0), errors="coerce").fillna(0)
    + pd.to_numeric(df.get("Acompte 3", 0), errors="coerce").fillna(0)
    + pd.to_numeric(df.get("Acompte 4", 0), errors="coerce").fillna(0)
)

df["Solde"] = df["Total facturé"] - df["Montant encaissé"]


# ---------------------------------------------------
# KPI — Version compacte et lisible en mode sombre
# ---------------------------------------------------
st.subheader("📌 Indicateurs")

c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("Dossiers", len(df))
c2.metric("Honoraires", f"${df['Montant honoraires (US $)'].sum():,.2f}")
c3.metric("Autres frais", f"${df['Autres frais (US $)'].sum():,.2f}")
c4.metric("Facturé", f"${df['Total facturé'].sum():,.2f}")
c5.metric("Encaissé", f"${df['Montant encaissé'].sum():,.2f}")
c6.metric("Solde", f"${df['Solde'].sum():,.2f}")

st.markdown("---")


# ---------------------------------------------------
# FILTRES INTELLIGENTS
# ---------------------------------------------------
st.subheader("🎛️ Filtres")

colA, colB, colC, colD, colE = st.columns(5)


# ---- FILTRE Catégorie ----
cat_list = ["Toutes"]
if not df_visa.empty and "Categories" in df_visa.columns:
    cat_list += sorted(df_visa["Categories"].dropna().unique().tolist())

categorie = colA.selectbox("Catégorie", cat_list)


# ---- FILTRE Sous-catégorie ----
if categorie != "Toutes" and not df_visa.empty:
    souscat_list = ["Toutes"] + sorted(
        df_visa[df_visa["Categories"] == categorie]["Sous-categories"].dropna().unique().tolist()
    )
else:
    souscat_list = ["Toutes"]
    if "Sous-categories" in df.columns:
        souscat_list += sorted(df["Sous-catégories"].dropna().unique().tolist())

souscat = colB.selectbox("Sous-catégorie", souscat_list)


# ---- FILTRE Visa ----
if souscat != "Toutes" and not df_visa.empty:
    visa_list = ["Tous"] + sorted(
        df_visa[df_visa["Sous-categories"] == souscat]["Visa"].dropna().unique().tolist()
    )
elif categorie != "Toutes" and not df_visa.empty:
    visa_list = ["Tous"] + sorted(
        df_visa[df_visa["Categories"] == categorie]["Visa"].dropna().unique().tolist()
    )
else:
    visa_list = ["Tous"]
    if "Visa" in df.columns:
        visa_list += sorted(df["Visa"].dropna().unique().tolist())

visa_filter = colC.selectbox("Visa", visa_list)


# ---- FILTRE Année ----
df["Année"] = df["Date"].dt.year
annee_list = ["Toutes"] + sorted(df["Année"].dropna().unique().tolist())

annee_filter = colD.selectbox("Année", annee_list)


# ---- FILTRE Date à Date ----
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

if visa_filter != "Tous":
    filtered = filtered[filtered["Visa"] == visa_filter]

if annee_filter != "Toutes":
    filtered = filtered[filtered["Année"] == annee_filter]

if date_debut:
    filtered = filtered[filtered["Date"] >= pd.to_datetime(date_debut)]

if date_fin:
    filtered = filtered[filtered["Date"] <= pd.to_datetime(date_fin)]


# ---------------------------------------------------
# TABLEAU FINAL
# ---------------------------------------------------
st.subheader("📋 Dossiers filtrés")

colonnes = [
    "Dossier N", "Nom", "Catégories", "Sous-catégories", "Visa",
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Total facturé", "Montant encaissé", "Solde", "Date"
]

colonnes = [c for c in colonnes if c in filtered.columns]

st.dataframe(filtered[colonnes], use_container_width=True, height=600)
