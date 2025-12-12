import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database


# ---------------------------------------------------------
# CONFIG & SIDEBAR
# ---------------------------------------------------------
st.set_page_config(page_title="🏠 Dashboard", page_icon="🏠", layout="wide")
render_sidebar()
st.title("🏠 Dashboard — Berenbaum Law App")


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def normalize_bool(x) -> bool:
    if isinstance(x, bool):
        return x
    if x is None:
        return False
    s = str(x).strip().lower()
    return s in ["true", "1", "1.0", "yes", "oui", "y", "vrai"]


def to_float(x) -> float:
    try:
        if x is None or x == "":
            return 0.0
        return float(x)
    except Exception:
        return 0.0


def ensure_cols(df: pd.DataFrame, cols_defaults: dict) -> pd.DataFrame:
    df = df.copy()
    for col, default in cols_defaults.items():
        if col not in df.columns:
            df[col] = default
    return df


# ---------------------------------------------------------
# LOAD DB
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
df = pd.DataFrame(clients)

if df.empty:
    st.info("Aucun dossier trouvé.")
    st.stop()

# Colonnes minimales
df = ensure_cols(
    df,
    {
        "Dossier N": None,
        "Nom": "",
        "Date": "",
        "Categories": "",
        "Sous-categories": "",
        "Visa": "",
        "Montant honoraires (US $)": 0.0,
        "Autres frais (US $)": 0.0,
        "Acompte 1": 0.0,
        "Escrow": False,
        "Escrow_a_reclamer": False,
        "Escrow_reclame": False,
        "Dossier envoye": False,
        "Dossier_envoye": False,
        "Dossier accepte": False,
        "Dossier refuse": False,
        "Dossier Annule": False,
        "RFE": False,
    },
)

# Normalisations
df["Dossier N"] = pd.to_numeric(df["Dossier N"], errors="coerce").astype("Int64")
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

for bcol in [
    "Escrow",
    "Escrow_a_reclamer",
    "Escrow_reclame",
    "Dossier envoye",
    "Dossier_envoye",
    "Dossier accepte",
    "Dossier refuse",
    "Dossier Annule",
    "RFE",
]:
    df[bcol] = df[bcol].apply(normalize_bool)

for ncol in ["Montant honoraires (US $)", "Autres frais (US $)", "Acompte 1"]:
    df[ncol] = df[ncol].apply(to_float)

# Harmonisation: si certains enregistrements ont Dossier_envoye au lieu de Dossier envoye
# (on ne supprime rien ici, on aligne seulement le calcul)
df["Dossier envoye"] = df["Dossier envoye"] | df["Dossier_envoye"]

# ---------------------------------------------------------
# KPI GLOBALS
# ---------------------------------------------------------
st.subheader("📌 Indicateurs clés")

total_dossiers = int(df["Dossier N"].dropna().nunique())
ca_total = float((df["Montant honoraires (US $)"] + df["Autres frais (US $)"]).sum())

envoyes = int(df["Dossier envoye"].sum())
acceptes = int(df["Dossier accepte"].sum())
refuses = int(df["Dossier refuse"].sum())
rfe = int(df["RFE"].sum())

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("📁 Dossiers", f"{total_dossiers}")
k2.metric("💰 CA total", f"${ca_total:,.0f}")
k3.metric("📤 Envoyés", f"{envoyes}")
k4.metric("✅ Acceptés", f"{acceptes}")
k5.metric("❌ Refusés", f"{refuses}")
k6.metric("📌 RFE", f"{rfe}")

# ---------------------------------------------------------
# KPI ESCROW (Acompte 1 uniquement) — SUR DASHBOARD
# ---------------------------------------------------------
st.subheader("💼 Escrow — KPI (Acompte 1)")

escrow_actif_total = float(df.loc[df["Escrow"] == True, "Acompte 1"].sum())
escrow_areclamer_total = float(df.loc[df["Escrow_a_reclamer"] == True, "Acompte 1"].sum())
escrow_reclame_total = float(df.loc[df["Escrow_reclame"] == True, "Acompte 1"].sum())

e1, e2, e3 = st.columns(3)
e1.metric("💼 Escrow actif", f"${escrow_actif_total:,.2f}")
e2.metric("📤 Escrow à réclamer", f"${escrow_areclamer_total:,.2f}")
e3.metric("✅ Escrow réclamé", f"${escrow_reclame_total:,.2f}")

st.caption("Règle appliquée : les montants Escrow correspondent à Acompte 1 uniquement, ventilés par état.")

# ---------------------------------------------------------
# TABLEAU RAPIDE
# ---------------------------------------------------------
st.subheader("📋 Aperçu dossiers (extrait)")

cols = [
    "Dossier N",
    "Nom",
    "Date",
    "Categories",
    "Sous-categories",
    "Visa",
    "Montant honoraires (US $)",
    "Autres frais (US $)",
    "Acompte 1",
    "Escrow",
    "Escrow_a_reclamer",
    "Escrow_reclame",
    "Dossier envoye",
    "Dossier accepte",
    "Dossier refuse",
    "Dossier Annule",
    "RFE",
]
cols = [c for c in cols if c in df.columns]

st.dataframe(
    df[cols].sort_values(by="Date", ascending=False, na_position="last").head(200),
    height=520,
    use_container_width=True,
)
