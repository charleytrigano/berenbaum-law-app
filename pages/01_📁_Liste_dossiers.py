# pages/01_📁_Liste_dossiers.py
import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database
from utils.status_utils import normalize_status_columns, normalize_bool

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="📁 Liste des dossiers", page_icon="📁", layout="wide")
render_sidebar()
st.title("📁 Liste complète des dossiers")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients).copy()

# ---------------------------------------------------------
# NORMALISATION
# ---------------------------------------------------------
# Dossier N (support xxxxx-1)
df["Dossier N"] = df.get("Dossier N", "").astype(str).fillna("").str.strip()

# Statuts
df = normalize_status_columns(df)

# Dates
df["Date"] = pd.to_datetime(df.get("Date"), errors="coerce")
df["Année"] = df["Date"].dt.year

# Textes
for col in ["Nom", "Categories", "Sous-categories", "Visa"]:
    if col not in df.columns:
        df[col] = ""
    df[col] = df[col].astype(str).fillna("").str.strip()

# Numériques
def to_float(x):
    try:
        return float(x or 0)
    except:
        return 0.0

for c in ["Montant honoraires (US $)", "Autres frais (US $)"]:
    if c not in df.columns:
        df[c] = 0.0
    df[c] = df[c].apply(to_float)

for i in range(1, 5):
    col = f"Acompte {i}"
    if col not in df.columns:
        df[col] = 0.0
    df[col] = df[col].apply(to_float)

df["Total facturé"] = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
df["Total encaissé"] = df[[f"Acompte {i}" for i in range(1, 5)]].sum(axis=1)
df["Solde"] = df["Total facturé"] - df["Total encaissé"]

# ---------------------------------------------------------
# FILTRES (UNE SEULE LIGNE)
# ---------------------------------------------------------
st.subheader("🧰 Filtres")

f1, f2, f3, f4, f5 = st.columns(5)

# Année
years = sorted([int(y) for y in df["Année"].dropna().unique().tolist()])
annee_sel = f1.selectbox("Année", options=["Toutes"] + years)

# Catégorie
cat_list = ["Toutes"] + sorted([c for c in df["Categories"].unique().tolist() if c])
categorie_sel = f2.selectbox("Catégorie", options=cat_list)

# Sous-catégorie (dépendante)
df_cat = df[df["Categories"] == categorie_sel] if categorie_sel != "Toutes" else df
sous_list = ["Toutes"] + sorted([s for s in df_cat["Sous-categories"].unique().tolist() if s])
sous_sel = f3.selectbox("Sous-catégorie", options=sous_list)

# Visa (dépendant)
df_sous = df_cat[df_cat["Sous-categories"] == sous_sel] if sous_sel != "Toutes" else df_cat
visa_list = ["Tous"] + sorted([v for v in df_sous["Visa"].unique().tolist() if v])
visa_sel = f4.selectbox("Visa", options=visa_list)

# 🔍 NOUVEAU FILTRE NOM
nom_recherche = f5.text_input("Nom (recherche)", placeholder="Ex: DUPONT")

# ---------------------------------------------------------
# APPLICATION DES FILTRES
# ---------------------------------------------------------
df_filt = df.copy()

if annee_sel != "Toutes":
    df_filt = df_filt[df_filt["Année"] == annee_sel]

if categorie_sel != "Toutes":
    df_filt = df_filt[df_filt["Categories"] == categorie_sel]

if sous_sel != "Toutes":
    df_filt = df_filt[df_filt["Sous-categories"] == sous_sel]

if visa_sel != "Tous":
    df_filt = df_filt[df_filt["Visa"] == visa_sel]

# 🔍 Filtre Nom (contient, insensible à la casse)
if nom_recherche.strip():
    df_filt = df_filt[
        df_filt["Nom"].str.contains(nom_recherche.strip(), case=False, na=False)
    ]

# ---------------------------------------------------------
# TABLEAU DES DOSSIERS
# ---------------------------------------------------------
st.markdown("---")
st.subheader(f"📋 Dossiers trouvés : {len(df_filt)}")

cols = [
    "Dossier N", "Nom", "Date",
    "Categories", "Sous-categories", "Visa",
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Total facturé", "Total encaissé", "Solde",
    "Dossier envoye", "Dossier accepte", "Dossier refuse", "Dossier Annule", "RFE",
]

cols_display = [c for c in cols if c in df_filt.columns]

st.dataframe(
    df_filt.sort_values(["Date", "Dossier N"], ascending=[False, True])[cols_display],
    use_container_width=True,
)