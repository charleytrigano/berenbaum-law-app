import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(page_title="Berenbaum Law App", page_icon="📁", layout="wide")
st.title("📊 Tableau de bord – Berenbaum Law App")
st.write("Bienvenue dans l'application professionnelle de gestion des dossiers.")

# ---------------------------------------------------
# DÉPENDANCES CATÉGORIE → SOUS-CATÉGORIE → VISA
# ---------------------------------------------------
dependencies = {
    "Affaires / Tourisme": {
        "B-1": ["1-COS", "2-EOS"],
        "B-2": ["1-COS", "2-EOS"]
    },
    "Professionnel": {
        "P-1": ["1-Inv.", "2-CP", "3-USCIS"],
        "P-2": ["1-CP", "2-USCIS"]
    },
    "Travailleur temporaire": {
        "H-1B": ["1-Initial", "2-Extension", "3-Transfer", "4-CP"],
        "H-2B": ["2-CP.1"],
        "E-3": ["1-Employement"]
    },
    "Immigration permanente - EB": {
        "EB1": ["1-I-140", "2-AOS", "3-I-140 & AOS", "4-CP.1"],
        "EB2": ["4-Perm", "5-CP"],
        "EB5": ["1-I-526", "2-AOS.1", "3-I527 & AOS", "4-CP.2", "I-829"]
    },
    "Immigration familiale": {
        "I-130": ["2-I-130", "3-AOS", "4-I-130 & AOS", "5-CP.1"],
        "K-1": ["1-CP.1", "2-AOS.2"]
    },
    "Autres": {
        "Traditional": ["Traditional"],
        "Marriage": ["Marriage"],
        "Derivatives": ["Derivatives"],
        "Travel Permit": ["Travel Permit"],
        "Work Permit": ["Work Permit"],
        "I-751": ["I-751"],
        "Re-entry Permit": ["Re-entry Permit"],
        "I-90": ["I-90"],
        "Consultation": ["Consultation"],
        "Analysis": ["Analysis"],
        "Referral": ["Referral"],
        "I-407": ["I-407"]
    }
}

# ---------------------------------------------------
# CHARGEMENT BASE
# ---------------------------------------------------
try:
    db = load_database()
    st.success("Base de données chargée depuis Dropbox ✔")
except Exception as e:
    st.error(f"Erreur Dropbox : {e}")
    st.stop()

clients = db.get("clients", [])

if not clients:
    st.info("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)

# ---------------------------------------------------
# NORMALISATION MONTANTS
# ---------------------------------------------------
montants = [
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4"
]

for col in montants:
    if col not in df.columns:
        df[col] = 0
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

df["Total facturé"] = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
df["Montant encaissé"] = df["Acompte 1"] + df["Acompte 2"] + df["Acompte 3"] + df["Acompte 4"]
df["Solde"] = df["Total facturé"] - df["Montant encaissé"]

# ---------------------------------------------------
# KPI
# ---------------------------------------------------
st.subheader("📌 Indicateurs principaux")

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Nombre de dossiers", len(df))
col2.metric("Total honoraires", f"${df['Montant honoraires (US $)'].sum():,.2f}")
col3.metric("Total autres frais", f"${df['Autres frais (US $)'].sum():,.2f}")
col4.metric("Total facturé", f"${df['Total facturé'].sum():,.2f}")
col5.metric("Montant encaissé", f"${df['Montant encaissé'].sum():,.2f}")
col6.metric("Solde restant", f"${df['Solde'].sum():,.2f}")

st.markdown("---")

# ---------------------------------------------------
# FILTRES DYNAMIQUES
# ---------------------------------------------------
st.subheader("🎛️ Filtres")

colA, colB, colC = st.columns(3)

# --- Catégories ---
categorie = colA.selectbox("Catégorie", ["Toutes"] + list(dependencies.keys()))

# --- Sous-catégories dépendantes ---
if categorie != "Toutes":
    sous_cats = ["Toutes"] + list(dependencies[categorie].keys())
else:
    sous_cats = ["Toutes"]
sous_categorie = colB.selectbox("Sous-catégorie", sous_cats)

# --- Visa dépendant ---
if categorie != "Toutes" and sous_categorie != "Toutes":
    visas = ["Tous"] + dependencies[categorie][sous_categorie]
else:
    visas = ["Tous"]
visa = colC.selectbox("Visa", visas)

# ---------------------------------------------------
# APPLICATION DES FILTRES
# ---------------------------------------------------
filtered = df.copy()

if categorie != "Toutes":
    filtered = filtered[filtered["Catégories"] == categorie]

if sous_categorie != "Toutes":
    filtered = filtered[filtered["Sous-catégories"] == sous_categorie]

if visa != "Tous":
    filtered = filtered[filtered["Visa"] == visa]

# ---------------------------------------------------
# AFFICHAGE
# ---------------------------------------------------
st.subheader("📋 Dossiers filtrés")

st.dataframe(
    filtered[
        [
            "Dossier N", "Nom", "Catégories", "Sous-catégories",
            "Visa", "Total facturé", "Montant encaissé", "Solde"
        ]
    ],
    use_container_width=True,
    height=500
)
