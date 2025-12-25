# pages/00_🏠_Dashboard.py
import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database
from utils.status_utils import normalize_status_columns, normalize_bool

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="🏠 Dashboard", page_icon="🏠", layout="wide")
render_sidebar()
st.title("🏠 Dashboard – Vue globale")

# ---------------------------------------------------------
# STYLE (KPI plus petits + alignés)
# ---------------------------------------------------------
st.markdown(
    """
    <style>
      [data-testid="stMetricValue"] { font-size: 20px !important; }
      [data-testid="stMetricLabel"] { font-size: 13px !important; }
      [data-testid="stMetricDelta"] { font-size: 12px !important; }
      .block-container { padding-top: 1.2rem; padding-bottom: 1.2rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier trouvé dans la base.")
    st.stop()

df = pd.DataFrame(clients)

# ---------------------------------------------------------
# NORMALISATION COLONNES ESSENTIELLES
# ---------------------------------------------------------
def ensure_col(frame: pd.DataFrame, col: str, default):
    if col not in frame.columns:
        frame[col] = default
    return frame

ensure_col(df, "Dossier N", "")
ensure_col(df, "Nom", "")
ensure_col(df, "Date", "")
ensure_col(df, "Categories", "")
ensure_col(df, "Sous-categories", "")
ensure_col(df, "Visa", "")
ensure_col(df, "Montant honoraires (US $)", 0)
ensure_col(df, "Autres frais (US $)", 0)

for i in range(1, 5):
    ensure_col(df, f"Acompte {i}", 0)

ensure_col(df, "Escrow", False)
ensure_col(df, "Escrow_a_reclamer", False)
ensure_col(df, "Escrow_reclame", False)

# Normalisation statuts (gère alias Dossier_envoye, etc.)
df = normalize_status_columns(df)

# Dates
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Année"] = df["Date"].dt.year

# Numériques
money_cols = ["Montant honoraires (US $)", "Autres frais (US $)"] + [f"Acompte {i}" for i in range(1, 5)]
for c in money_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)

# Booléens
bool_cols = [
    "Escrow", "Escrow_a_reclamer", "Escrow_reclame",
    "Dossier envoye", "Dossier accepte", "Dossier refuse", "Dossier Annule", "RFE"
]
for c in bool_cols:
    ensure_col(df, c, False)
    df[c] = df[c].apply(normalize_bool)

# ---------------------------------------------------------
# DOSSIER PARENT / FILS (supporte 12937-1, 12937-2, etc.)
# ---------------------------------------------------------
df["Dossier N"] = df["Dossier N"].astype(str).fillna("")

def parse_parent(n: str) -> str:
    n = str(n).strip()
    if "-" in n:
        return n.split("-", 1)[0].strip()
    return n

def parse_index(n: str) -> int:
    n = str(n).strip()
    if "-" in n:
        suf = n.split("-", 1)[1].strip()
        try:
            return int(float(suf))
        except Exception:
            return 0
    return 0

def parse_parent_num(n: str) -> float:
    p = parse_parent(n)
    try:
        return float(p)
    except Exception:
        # met les valeurs non numériques à la fin
        return float("inf")

df["Dossier Parent"] = df["Dossier N"].apply(parse_parent)
df["Dossier Index"] = df["Dossier N"].apply(parse_index)
df["Dossier Parent Num"] = df["Dossier N"].apply(parse_parent_num)

# ---------------------------------------------------------
# FILTRES
# ---------------------------------------------------------
st.subheader("🎛️ Filtres")

c1, c2, c3, c4, c5 = st.columns(5)

years = sorted([int(y) for y in df["Année"].dropna().unique() if pd.notna(y)])
year_choice = c1.selectbox("Filtrer par année", ["Toutes"] + years)

cats = sorted([x for x in df["Categories"].dropna().unique().tolist() if str(x).strip() != ""])
cat_choice = c2.selectbox("Catégorie", ["Toutes"] + cats)

if cat_choice != "Toutes":
    souscats = sorted(
        [x for x in df.loc[df["Categories"] == cat_choice, "Sous-categories"].dropna().unique().tolist() if str(x).strip() != ""]
    )
else:
    souscats = sorted([x for x in df["Sous-categories"].dropna().unique().tolist() if str(x).strip() != ""])
sous_choice = c3.selectbox("Sous-catégorie", ["Toutes"] + souscats)

if sous_choice != "Toutes":
    visas = sorted([x for x in df.loc[df["Sous-categories"] == sous_choice, "Visa"].dropna().unique().tolist() if str(x).strip() != ""])
else:
    visas = sorted([x for x in df["Visa"].dropna().unique().tolist() if str(x).strip() != ""])
visa_choice = c4.selectbox("Visa", ["Toutes"] + visas)

statut_choice = c5.selectbox("Statut", ["Tous", "Envoyé", "Accepté", "Refusé", "Annulé", "RFE"])

df_f = df.copy()

if year_choice != "Toutes":
    df_f = df_f[df_f["Année"] == year_choice]

if cat_choice != "Toutes":
    df_f = df_f[df_f["Categories"] == cat_choice]

if sous_choice != "Toutes":
    df_f = df_f[df_f["Sous-categories"] == sous_choice]

if visa_choice != "Toutes":
    df_f = df_f[df_f["Visa"] == visa_choice]

if statut_choice != "Tous":
    statut_map = {
        "Envoyé": "Dossier envoye",
        "Accepté": "Dossier accepte",
        "Refusé": "Dossier refuse",
        "Annulé": "Dossier Annule",
        "RFE": "RFE",
    }
    col = statut_map[statut_choice]
    ensure_col(df_f, col, False)
    df_f = df_f[df_f[col] == True]

# ---------------------------------------------------------
# KPI
# ---------------------------------------------------------
st.subheader("📌 Indicateurs clés")

total_dossiers = int(len(df_f))
total_hono = float(df_f["Montant honoraires (US $)"].sum())
total_frais = float(df_f["Autres frais (US $)"].sum())
total_facture = total_hono + total_frais
total_encaisse = float(sum(df_f[f"Acompte {i}"].sum() for i in range(1, 5)))
solde_du = total_facture - total_encaisse

# Montants escrow = Acompte 1 (même logique sur les 3 états)
escrow_actif_amt = float(df_f.loc[df_f["Escrow"] == True, "Acompte 1"].sum())
escrow_reclamer_amt = float(df_f.loc[df_f["Escrow_a_reclamer"] == True, "Acompte 1"].sum())
escrow_reclame_amt = float(df_f.loc[df_f["Escrow_reclame"] == True, "Acompte 1"].sum())
escrow_total_amt = escrow_actif_amt + escrow_reclamer_amt + escrow_reclame_amt

k1, k2, k3, k4, k5, k6, k7 = st.columns(7)
k1.metric("Nombre de dossiers", f"{total_dossiers}")
k2.metric("Montant honoraires (US $)", f"{total_hono:,.2f}")
k3.metric("Autres frais (US $)", f"{total_frais:,.2f}")
k4.metric("Total facturé", f"{total_facture:,.2f}")
k5.metric("Total encaissé", f"{total_encaisse:,.2f}")
k6.metric("Solde dû", f"{solde_du:,.2f}")
k7.metric("Escrow total (Acompte 1)", f"{escrow_total_amt:,.2f}")

# ---------------------------------------------------------
# TABLEAU – VUE PARENTS / FILS
# ---------------------------------------------------------
st.subheader("📋 Dossiers (parents & fils)")

cols_display = [
    "Dossier N",
    "Dossier Parent",
    "Dossier Index",
    "Nom",
    "Date",
    "Categories",
    "Sous-categories",
    "Visa",
    "Montant honoraires (US $)",
    "Autres frais (US $)",
    "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4",
    "Dossier envoye",
    "Dossier accepte",
    "Dossier refuse",
    "Dossier Annule",
    "RFE",
    "Escrow",
    "Escrow_a_reclamer",
    "Escrow_reclame",
]

# On construit une vue triée en gardant les colonnes de tri, puis on affiche uniquement cols_display
df_view = df_f.copy()

# Sécurise les colonnes de tri
ensure_col(df_view, "Dossier Parent Num", float("inf"))
ensure_col(df_view, "Dossier Parent", "")
ensure_col(df_view, "Dossier Index", 0)
ensure_col(df_view, "Dossier N", "")

df_view = df_view.sort_values(
    ["Dossier Parent Num", "Dossier Parent", "Dossier Index", "Dossier N"],
    ascending=[True, True, True, True],
)

# Sécurise les colonnes d'affichage
for c in cols_display:
    ensure_col(df_view, c, "")

st.dataframe(df_view[cols_display], use_container_width=True, height=520)