# pages/12_📁_Fiche_groupe_dossier.py
import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(page_title="📁 Fiche groupe dossier", page_icon="📁", layout="wide")
render_sidebar()
st.title("📁 Fiche groupe dossier (parent + fils)")

# =====================================================
# LOAD DATABASE
# =====================================================
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.error("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients).copy()

# =====================================================
# HIERARCHIE DOSSIER (robuste)
# - Parent: partie avant '-'
# - Index: partie après '-' si existe sinon 0
# =====================================================
df["Dossier N"] = df.get("Dossier N", "").astype(str).fillna("").str.strip()

def parse_parent_num(dossier_n: str) -> str:
    if not dossier_n:
        return ""
    return dossier_n.split("-")[0].strip()

def parse_index(dossier_n: str) -> int:
    if not dossier_n or "-" not in dossier_n:
        return 0
    part = dossier_n.split("-", 1)[1].strip()
    try:
        return int(part)
    except Exception:
        return 0

df["Dossier Parent"] = df["Dossier N"].apply(parse_parent_num)
df["Dossier Index"] = df["Dossier N"].apply(parse_index)
df["Est Parent"] = df["Dossier Index"].eq(0)

# Liste des parents (uniquement)
parents = (
    df[df["Est Parent"] & df["Dossier Parent"].ne("")]["Dossier Parent"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)
parents = sorted(parents, key=lambda x: (int(x) if x.isdigit() else 10**18, x))

if not parents:
    st.warning("Aucun dossier parent détecté. Vérifie le format de 'Dossier N'.")
    st.stop()

# =====================================================
# SELECTION PARENT
# =====================================================
st.subheader("🎯 Sélectionner un dossier parent")
parent_selected = st.selectbox("Dossier parent", parents)

# =====================================================
# CONSTRUCTION GROUPE (IMPORTANT : on ne filtre PAS avant)
# Groupe = parent + tous les fils qui commencent par parent-
# =====================================================
group_df = df[df["Dossier Parent"] == parent_selected].copy()

# Sécurités de tri
group_df["Dossier Parent Num"] = pd.to_numeric(group_df["Dossier Parent"], errors="coerce")
group_df = group_df.sort_values(
    by=["Dossier Parent Num", "Dossier Parent", "Dossier Index", "Dossier N"],
    ascending=[True, True, True, True],
)

# Parent et fils
parent_row = group_df[group_df["Est Parent"]].head(1)
children_df = group_df[~group_df["Est Parent"]].copy()

# =====================================================
# AFFICHAGE
# =====================================================
if parent_row.empty:
    st.error(
        "Le parent n'a pas été trouvé dans la base (ou a été transformé). "
        "Vérifie que le parent existe bien en 'xxxxx' sans suffixe."
    )
    st.stop()

p = parent_row.iloc[0].to_dict()

st.markdown("---")
st.subheader(f"📄 Parent : {p.get('Dossier N','')} — {p.get('Nom','')}")

c1, c2, c3 = st.columns(3)
c1.write(f"**Date** : {p.get('Date','')}")
c2.write(f"**Catégorie** : {p.get('Categories','')}")
c3.write(f"**Sous-catégorie** : {p.get('Sous-categories','')}")

c4, c5, c6 = st.columns(3)
c4.write(f"**Visa** : {p.get('Visa','')}")
c5.write(f"**Honoraires (US $)** : {p.get('Montant honoraires (US $)', 0)}")
c6.write(f"**Autres frais (US $)** : {p.get('Autres frais (US $)', 0)}")

commentaire_parent = p.get("Commentaire", "")
if str(commentaire_parent).strip():
    st.markdown("**📝 Commentaire (parent)**")
    st.write(commentaire_parent)

st.markdown("---")
st.subheader("📎 Sous-dossiers (fils)")

if children_df.empty:
    st.info("Aucun sous-dossier (fils) pour ce parent.")
else:
    # Colonnes d'affichage (robuste : uniquement celles qui existent)
    wanted_cols = [
        "Dossier N", "Nom", "Date",
        "Categories", "Sous-categories", "Visa",
        "Montant honoraires (US $)", "Autres frais (US $)",
        "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4",
        "Escrow", "Escrow_a_reclamer", "Escrow_reclame",
        "Dossier envoye", "Dossier accepte", "Dossier refuse", "Dossier Annule", "RFE",
        "Commentaire"
    ]
    cols_display = [c for c in wanted_cols if c in children_df.columns]

    st.dataframe(children_df[cols_display], use_container_width=True)

# =====================================================
# KPI GROUPE (parent + fils)
# =====================================================
st.markdown("---")
st.subheader("📊 KPI du groupe (parent + fils)")

def to_float(v):
    try:
        return float(v or 0)
    except Exception:
        return 0.0

hon = group_df.get("Montant honoraires (US $)", pd.Series([0]*len(group_df))).apply(to_float).sum()
frais = group_df.get("Autres frais (US $)", pd.Series([0]*len(group_df))).apply(to_float).sum()
total_facture = hon + frais

total_encaisse = 0.0
for i in range(1, 5):
    col = f"Acompte {i}"
    if col in group_df.columns:
        total_encaisse += group_df[col].apply(to_float).sum()

solde = total_facture - total_encaisse

# Escrow = Acompte 1 uniquement, dossiers ayant un des flags escrow à True
escrow_flags = pd.Series([False] * len(group_df))
for k in ["Escrow", "Escrow_a_reclamer", "Escrow_reclame"]:
    if k in group_df.columns:
        escrow_flags = escrow_flags | group_df[k].astype(str).str.lower().isin(["true", "1", "yes", "oui"])

escrow_total = 0.0
if "Acompte 1" in group_df.columns:
    escrow_total = group_df.loc[escrow_flags, "Acompte 1"].apply(to_float).sum()

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Dossiers (groupe)", len(group_df))
k2.metric("Honoraires", f"${hon:,.2f}")
k3.metric("Autres frais", f"${frais:,.2f}")
k4.metric("Total facturé", f"${total_facture:,.2f}")
k5.metric("Total encaissé", f"${total_encaisse:,.2f}")
k6.metric("Escrow total (Acompte 1)", f"${escrow_total:,.2f}")
st.info(f"Solde dû (groupe) : ${solde:,.2f}")