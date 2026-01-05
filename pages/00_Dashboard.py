import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database
from utils.status_utils import normalize_status_columns

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(
    page_title="🏠 Dashboard – Vue globale",
    page_icon="🏠",
    layout="wide"
)

render_sidebar()
st.title("🏠 Dashboard – Vue globale")

# =====================================================
# LOAD DATABASE
# =====================================================
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier disponible.")
    st.stop()

df = pd.DataFrame(clients)

# =====================================================
# NORMALISATION
# =====================================================
df = normalize_status_columns(df)

df["Dossier N"] = df["Dossier N"].astype(str)

# Dates
df["Date"] = pd.to_datetime(df.get("Date"), errors="coerce")
df["Annee"] = df["Date"].dt.year

# =====================================================
# FILTRES
# =====================================================
st.markdown("### 🎛️ Filtres")

f1, f2, f3, f4, f5 = st.columns(5)

annees = sorted(df["Annee"].dropna().unique().tolist())
annee_sel = f1.multiselect("Année", annees, default=annees)

cats = sorted(df["Categories"].dropna().unique().tolist())
cat_sel = f2.multiselect("Catégorie", cats, default=cats)

souscats = sorted(df["Sous-categories"].dropna().unique().tolist())
sous_sel = f3.multiselect("Sous-catégorie", souscats, default=souscats)

visas = sorted(df["Visa"].dropna().unique().tolist())
visa_sel = f4.multiselect("Visa", visas, default=visas)

statut_sel = f5.multiselect(
    "Statut",
    ["Envoyé", "Accepté", "Refusé", "Annulé", "RFE"],
    default=["Envoyé", "Accepté", "Refusé", "Annulé", "RFE"]
)

# =====================================================
# APPLICATION FILTRES
# =====================================================
df_f = df[
    df["Annee"].isin(annee_sel)
    & df["Categories"].isin(cat_sel)
    & df["Sous-categories"].isin(sous_sel)
    & df["Visa"].isin(visa_sel)
].copy()

# Filtre statuts
mask_statut = False
if "Envoyé" in statut_sel:
    mask_statut |= df_f["Dossier envoye"]
if "Accepté" in statut_sel:
    mask_statut |= df_f["Dossier accepte"]
if "Refusé" in statut_sel:
    mask_statut |= df_f["Dossier refuse"]
if "Annulé" in statut_sel:
    mask_statut |= df_f["Dossier Annule"]
if "RFE" in statut_sel:
    mask_statut |= df_f["RFE"]

df_f = df_f[mask_statut]

# =====================================================
# UTILS FINANCIERS
# =====================================================
def to_float(v):
    try:
        return float(v or 0)
    except Exception:
        return 0.0


def total_acomptes(row):
    return sum(
        to_float(row.get(f"Acompte {i}", 0))
        for i in range(1, 5)
    )

df_f["Total acomptes"] = df_f.apply(total_acomptes, axis=1)

# =====================================================
# KPI GLOBAUX
# =====================================================
honoraires = df_f["Montant honoraires (US $)"].apply(to_float).sum()
frais = df_f["Autres frais (US $)"].apply(to_float).sum()
total_facture = honoraires + frais
total_encaisse = df_f["Total acomptes"].sum()
solde = total_facture - total_encaisse

# =====================================================
# LOGIQUE ESCROW (SOURCE UNIQUE)
# =====================================================
df_f["Etat Escrow"] = "actif"

df_f.loc[
    (df_f["Dossier accepte"])
    | (df_f["Dossier refuse"])
    | (df_f["Dossier Annule"]),
    "Etat Escrow"
] = "a_reclamer"

df_f.loc[
    df_f["Escrow_reclame"] == True,
    "Etat Escrow"
] = "reclame"

escrow_actif = df_f[df_f["Etat Escrow"] == "actif"]
escrow_reclamer = df_f[df_f["Etat Escrow"] == "a_reclamer"]
escrow_reclame = df_f[df_f["Etat Escrow"] == "reclame"]

# =====================================================
# KPI AFFICHAGE
# =====================================================
st.markdown("### 📊 Indicateurs clés")

k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("📁 Dossiers", len(df_f))
k2.metric("💼 Honoraires", f"${honoraires:,.2f}")
k3.metric("💸 Autres frais", f"${frais:,.2f}")
k4.metric("🧾 Total facturé", f"${total_facture:,.2f}")
k5.metric("💰 Total encaissé", f"${total_encaisse:,.2f}")
k6.metric("📉 Solde dû", f"${solde:,.2f}")

st.markdown("---")

k7, k8, k9 = st.columns(3)

k7.metric(
    "💼 Escrow actif",
    f"${escrow_actif['Total acomptes'].sum():,.2f}",
    help=f"{len(escrow_actif)} dossiers"
)

k8.metric(
    "📤 Escrow à réclamer",
    f"${escrow_reclamer['Total acomptes'].sum():,.2f}",
    help=f"{len(escrow_reclamer)} dossiers"
)

k9.metric(
    "✅ Escrow réclamé",
    f"${escrow_reclame['Total acomptes'].sum():,.2f}",
    help=f"{len(escrow_reclame)} dossiers"
)

# =====================================================
# TABLEAU DOSSIERS
# =====================================================
st.markdown("---")
st.subheader("📋 Dossiers (vue synthétique)")

cols = [
    "Dossier N",
    "Nom",
    "Date",
    "Categories",
    "Sous-categories",
    "Visa",
    "Montant honoraires (US $)",
    "Autres frais (US $)",
    "Total acomptes",
    "Etat Escrow",
]

cols = [c for c in cols if c in df_f.columns]

st.dataframe(
    df_f.sort_values(["Date", "Dossier N"], ascending=[False, True])[cols],
    use_container_width=True
)