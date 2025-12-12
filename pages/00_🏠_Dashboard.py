import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database


# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="🏠 Dashboard", page_icon="🏠", layout="wide")
render_sidebar()
st.title("🏠 Dashboard — Berenbaum Law App")


# =========================================================
# HELPERS
# =========================================================
def normalize_bool(x):
    if isinstance(x, bool):
        return x
    if x is None:
        return False
    s = str(x).strip().lower()
    return s in ["true", "1", "1.0", "yes", "oui", "y", "vrai"]


def to_float(x):
    try:
        if x is None or x == "" or str(x).strip().lower() == "none":
            return 0.0
        return float(x)
    except Exception:
        return 0.0


def to_date(x):
    try:
        d = pd.to_datetime(x, errors="coerce")
        return pd.NaT if pd.isna(d) else d
    except Exception:
        return pd.NaT


def split_dossier_id(dossier_n: str) -> str:
    """
    Retourne l'identifiant 'principal' :
    - '12937-1' -> '12937'
    - '12937'   -> '12937'
    """
    s = str(dossier_n).strip()
    if "-" in s:
        return s.split("-", 1)[0].strip()
    return s


def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Colonnes minimales
    needed_text = ["Dossier N", "Nom", "Categories", "Sous-categories", "Visa", "Commentaire"]
    for c in needed_text:
        if c not in df.columns:
            df[c] = ""
        df[c] = df[c].fillna("").astype(str)

    if "Date" not in df.columns:
        df["Date"] = ""
    df["Date_dt"] = df["Date"].apply(to_date)

    # Montants
    for c in ["Montant honoraires (US $)", "Autres frais (US $)"]:
        if c not in df.columns:
            df[c] = 0.0
        df[c] = df[c].apply(to_float)

    for i in range(1, 5):
        c = f"Acompte {i}"
        if c not in df.columns:
            df[c] = 0.0
        df[c] = df[c].apply(to_float)

    # Statuts (tolérant : alias historiques)
    alias_map = {
        "Dossier envoye": ["Dossier envoye", "Dossier_envoye", "Dossier envoyé", "Dossier Envoye"],
        "Dossier accepte": ["Dossier accepte", "Dossier accepté", "Dossier Accepte", "Dossier_accepté"],
        "Dossier refuse": ["Dossier refuse", "Dossier refusé", "Dossier Refuse", "Dossier_refuse"],
        "Dossier Annule": ["Dossier Annule", "Dossier annulé", "Dossier Annulé", "Dossier_annule"],
        "RFE": ["RFE"],
    }

    for canonical, aliases in alias_map.items():
        vals = None
        for a in aliases:
            if a in df.columns:
                s = df[a].apply(normalize_bool)
                vals = s if vals is None else (vals | s)
        df[canonical] = vals if vals is not None else False

    # Escrow
    for c in ["Escrow", "Escrow_a_reclamer", "Escrow_reclame"]:
        if c not in df.columns:
            df[c] = False
        df[c] = df[c].apply(normalize_bool)

    # Dossier principal
    df["Dossier ID"] = df["Dossier N"].apply(split_dossier_id)

    # Année
    df["Année"] = df["Date_dt"].dt.year

    return df


def kpi(label: str, value: str, help_text: str = ""):
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(145deg, #1C1C1C, #0F0F0F);
            padding: 14px 14px;
            border-radius: 14px;
            border: 1px solid #3a3a3a;
            box-shadow: 0 0 12px rgba(255,215,0,0.10);
            color: #FFD777;
            width: 100%;
        ">
            <div style="font-size:13px; font-weight:600; color:#D8B86A; margin-bottom:6px; white-space:nowrap;">
                {label}
            </div>
            <div style="font-size:22px; font-weight:800; color:#FFD777; line-height:1.1;">
                {value}
            </div>
            <div style="font-size:12px; color:#9a9a9a; margin-top:6px;">
                {help_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def fmt_money(x: float) -> str:
    try:
        return f"{x:,.2f}"
    except Exception:
        return str(x)


# =========================================================
# LOAD
# =========================================================
db = load_database()
clients = pd.DataFrame(db.get("clients", []))

if clients.empty:
    st.info("Aucun dossier trouvé.")
    st.stop()

clients = ensure_columns(clients)

# =========================================================
# FILTRES (dans la page, pas sidebar)
# =========================================================
st.subheader("🎛️ Filtres")

colA, colB, colC, colD, colE = st.columns([1.0, 1.2, 1.2, 1.0, 1.2])

# 1) Année
years = sorted([int(y) for y in clients["Année"].dropna().unique() if str(y) != "nan"])
year_choice = colA.selectbox("1) Filtrer par année", ["Toutes"] + years)

# 2) Catégories
cats = sorted([c for c in clients["Categories"].dropna().unique() if str(c).strip() != ""])
cat_choice = colB.selectbox("2) Catégories", ["Toutes"] + cats)

# 3) Sous-catégories (dépend de catégorie)
if cat_choice != "Toutes":
    subcats = sorted(
        [c for c in clients.loc[clients["Categories"] == cat_choice, "Sous-categories"].dropna().unique() if str(c).strip() != ""]
    )
else:
    subcats = sorted([c for c in clients["Sous-categories"].dropna().unique() if str(c).strip() != ""])
sub_choice = colC.selectbox("3) Sous-catégories", ["Toutes"] + subcats)

# 4) Visa (dépend de sous-catégorie)
if sub_choice != "Toutes":
    visas = sorted(
        [v for v in clients.loc[clients["Sous-categories"] == sub_choice, "Visa"].dropna().unique() if str(v).strip() != ""]
    )
else:
    visas = sorted([v for v in clients["Visa"].dropna().unique() if str(v).strip() != ""])
visa_choice = colD.selectbox("4) Visa", ["Tous"] + visas)

# 5) Statut
status_choice = colE.selectbox(
    "5) Statut",
    ["Tous", "Envoyé", "Accepté", "Refusé", "Annulé", "RFE"]
)

# =========================================================
# APPLY FILTERS
# =========================================================
df = clients.copy()

if year_choice != "Toutes":
    df = df[df["Année"] == int(year_choice)]

if cat_choice != "Toutes":
    df = df[df["Categories"] == cat_choice]

if sub_choice != "Toutes":
    df = df[df["Sous-categories"] == sub_choice]

if visa_choice != "Tous":
    df = df[df["Visa"] == visa_choice]

if status_choice != "Tous":
    status_map = {
        "Envoyé": "Dossier envoye",
        "Accepté": "Dossier accepte",
        "Refusé": "Dossier refuse",
        "Annulé": "Dossier Annule",
        "RFE": "RFE",
    }
    df = df[df[status_map[status_choice]] == True]


# =========================================================
# KPI (sur lignes filtrées = sous-dossiers inclus)
# =========================================================
st.subheader("📌 KPI (sur les dossiers filtrés)")

total_dossiers = len(df)  # lignes (inclut 12937-1, 12937-2)
hon = float(df["Montant honoraires (US $)"].sum())
frais = float(df["Autres frais (US $)"].sum())
total_facture = hon + frais
total_encaisse = float(df[[f"Acompte {i}" for i in range(1, 5)]].sum(axis=1).sum())
solde_du = total_facture - total_encaisse

k1, k2, k3, k4, k5, k6 = st.columns(6)

with k1:
    kpi("Nombre de dossiers", f"{total_dossiers}", "Comptage des lignes (inclut -1/-2)")
with k2:
    kpi("Honoraires (US $)", fmt_money(hon), "Somme Montant honoraires")
with k3:
    kpi("Autres frais (US $)", fmt_money(frais), "Somme Autres frais")
with k4:
    kpi("Total facturé (US $)", fmt_money(total_facture), "Honoraires + Autres frais")
with k5:
    kpi("Total encaissé (US $)", fmt_money(total_encaisse), "Acompte 1 + 2 + 3 + 4")
with k6:
    kpi("Solde dû (US $)", fmt_money(solde_du), "Total facturé - Total encaissé")


# =========================================================
# VUE GROUPÉE PAR DOSSIER PRINCIPAL
# =========================================================
st.subheader("📁 Dossiers (groupés par dossier principal)")

if df.empty:
    st.info("Aucun dossier ne correspond aux filtres.")
    st.stop()

# Regroupement : un “principal” peut avoir plusieurs sous-dossiers
groups = []
for did, g in df.groupby("Dossier ID", dropna=False):
    g = g.copy()

    # Tri : principal d'abord, puis suffixes
    def sort_key(v):
        s = str(v)
        if "-" not in s:
            return (0, 0)
        try:
            return (1, int(s.split("-", 1)[1]))
        except Exception:
            return (1, 999999)

    g = g.sort_values(by="Dossier N", key=lambda s: s.map(sort_key))

    # Résumé (somme sur les lignes du groupe)
    hon_g = float(g["Montant honoraires (US $)"].sum())
    frais_g = float(g["Autres frais (US $)"].sum())
    facture_g = hon_g + frais_g
    encaisse_g = float(g[[f"Acompte {i}" for i in range(1, 5)]].sum(axis=1).sum())
    solde_g = facture_g - encaisse_g

    # Statut “résumé”
    env = bool(g["Dossier envoye"].any())
    acc = bool(g["Dossier accepte"].any())
    ref = bool(g["Dossier refuse"].any())
    ann = bool(g["Dossier Annule"].any())
    rfe = bool(g["RFE"].any())

    escrow_actif = bool(g["Escrow"].any())
    escrow_reclamer = bool(g["Escrow_a_reclamer"].any())
    escrow_reclame = bool(g["Escrow_reclame"].any())

    groups.append({
        "Dossier ID": did,
        "Nb lignes": len(g),
        "Nom (1er)": g.iloc[0].get("Nom", ""),
        "Catégorie (1er)": g.iloc[0].get("Categories", ""),
        "Sous-cat (1er)": g.iloc[0].get("Sous-categories", ""),
        "Visa (1er)": g.iloc[0].get("Visa", ""),
        "Total facturé": facture_g,
        "Total encaissé": encaisse_g,
        "Solde dû": solde_g,
        "Envoyé": env,
        "Accepté": acc,
        "Refusé": ref,
        "Annulé": ann,
        "RFE": rfe,
        "Escrow actif": escrow_actif,
        "Escrow à réclamer": escrow_reclamer,
        "Escrow réclamé": escrow_reclame,
        "_df": g,
    })

# Affichage “cards” via expanders
for item in sorted(groups, key=lambda x: str(x["Dossier ID"])):
    did = item["Dossier ID"]
    g = item["_df"]

    header = (
        f"Dossier {did} — {item['Nom (1er)']}  "
        f"(lignes: {item['Nb lignes']})  |  "
        f"Facturé: {fmt_money(item['Total facturé'])}  |  "
        f"Encaissé: {fmt_money(item['Total encaissé'])}  |  "
        f"Solde: {fmt_money(item['Solde dû'])}"
    )

    with st.expander(header, expanded=False):
        # Badges “statut”
        b1, b2, b3, b4, b5 = st.columns(5)
        b1.checkbox("Envoyé", value=item["Envoyé"], disabled=True, key=f"env_{did}")
        b2.checkbox("Accepté", value=item["Accepté"], disabled=True, key=f"acc_{did}")
        b3.checkbox("Refusé", value=item["Refusé"], disabled=True, key=f"ref_{did}")
        b4.checkbox("Annulé", value=item["Annulé"], disabled=True, key=f"ann_{did}")
        b5.checkbox("RFE", value=item["RFE"], disabled=True, key=f"rfe_{did}")

        e1, e2, e3 = st.columns(3)
        e1.checkbox("Escrow actif", value=item["Escrow actif"], disabled=True, key=f"es1_{did}")
        e2.checkbox("Escrow à réclamer", value=item["Escrow à réclamer"], disabled=True, key=f"es2_{did}")
        e3.checkbox("Escrow réclamé", value=item["Escrow réclamé"], disabled=True, key=f"es3_{did}")

        st.markdown("#### Détails des sous-dossiers (lignes)")
        show_cols = [
            "Dossier N", "Nom", "Date", "Categories", "Sous-categories", "Visa",
            "Montant honoraires (US $)", "Autres frais (US $)",
            "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4",
            "Dossier envoye", "Dossier accepte", "Dossier refuse", "Dossier Annule", "RFE",
            "Escrow", "Escrow_a_reclamer", "Escrow_reclame",
        ]
        show_cols = [c for c in show_cols if c in g.columns]
        st.dataframe(g[show_cols], width="stretch", height=220)

# =========================================================
# TABLEAU GLOBAL FILTRÉ (optionnel, utile)
# =========================================================
st.subheader("📋 Tableau — dossiers filtrés (toutes les lignes)")

display_cols = [
    "Dossier N", "Dossier ID", "Nom", "Date", "Categories", "Sous-categories", "Visa",
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4",
    "Dossier envoye", "Dossier accepte", "Dossier refuse", "Dossier Annule", "RFE",
    "Escrow", "Escrow_a_reclamer", "Escrow_reclame",
]
display_cols = [c for c in display_cols if c in df.columns]
st.dataframe(df[display_cols], width="stretch", height=380)
