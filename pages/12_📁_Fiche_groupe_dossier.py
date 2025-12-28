# pages/12_📁_Fiche_groupe_dossier.py
import os
import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database

# ✅ EXPORT PDF GROUPE
from utils.pdf_export_groupe import export_groupe_pdf


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
# NORMALISATION Dossier N + HIERARCHIE
# Parent = partie avant '-'
# Index  = partie après '-' si existe, sinon 0
# =====================================================
df["Dossier N"] = df.get("Dossier N", "").astype(str).fillna("").str.strip()


def parse_parent(dossier_n: str) -> str:
    if not dossier_n:
        return ""
    return dossier_n.split("-", 1)[0].strip()


def parse_index(dossier_n: str) -> int:
    if not dossier_n or "-" not in dossier_n:
        return 0
    suffix = dossier_n.split("-", 1)[1].strip()
    try:
        return int(suffix)
    except Exception:
        return 0


df["Dossier Parent"] = df["Dossier N"].apply(parse_parent)
df["Dossier Index"] = df["Dossier N"].apply(parse_index)
df["Est Parent"] = df["Dossier Index"].eq(0)
df["Est Fils"] = df["Dossier Index"].gt(0)

# =====================================================
# IMPORTANT : liste UNIQUEMENT des parents ayant AU MOINS un fils
# =====================================================
parents_avec_fils = (
    df.loc[df["Est Fils"] & df["Dossier Parent"].ne(""), "Dossier Parent"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)


def sort_key_parent(x: str):
    s = str(x).strip()
    return (0, int(s)) if s.isdigit() else (1, s)


parents_avec_fils = sorted(parents_avec_fils, key=sort_key_parent)

st.subheader("🎯 Sélectionner un groupe (parents qui ont des fils)")

if not parents_avec_fils:
    st.info("Aucun sous-dossier détecté (aucun dossier de type xxxxx-1 / xxxxx-2 / ...).")
    st.stop()

# =====================================================
# LABEL "Dossier N + Nom" pour le filtre
# - Nom du parent si la ligne parent existe
# - Sinon, Nom du premier fils
# =====================================================
def get_name_for_parent(parent_id: str) -> str:
    p = df[(df["Dossier N"] == str(parent_id)) & (df["Est Parent"])]
    if not p.empty:
        name = str(p.iloc[0].get("Nom", "") or "").strip()
        if name:
            return name

    kids = df[(df["Dossier Parent"] == str(parent_id)) & (df["Est Fils"])].sort_values(
        ["Dossier Index", "Dossier N"]
    )
    if not kids.empty:
        name = str(kids.iloc[0].get("Nom", "") or "").strip()
        if name:
            return name

    return ""


parent_labels = {}
for p in parents_avec_fils:
    nom = get_name_for_parent(p)
    label = f"{p} — {nom}" if nom else f"{p}"
    parent_labels[p] = label

parent_selected = st.selectbox(
    "Groupe (Dossier N + Nom)",
    options=parents_avec_fils,
    format_func=lambda x: parent_labels.get(x, str(x)),
)

# =====================================================
# CONSTRUCTION GROUPE : parent + tous ses fils
# =====================================================
group_df = df[df["Dossier Parent"] == str(parent_selected)].copy()

parent_df = group_df[group_df["Est Parent"]].copy()
children_df = group_df[group_df["Est Fils"]].copy()

group_df["Parent Num"] = pd.to_numeric(group_df["Dossier Parent"], errors="coerce")
group_df = group_df.sort_values(
    ["Parent Num", "Dossier Parent", "Dossier Index", "Dossier N"],
    ascending=[True, True, True, True],
)

# =====================================================
# AFFICHAGE PARENT
# =====================================================
st.markdown("---")
st.subheader(f"📄 Groupe {parent_selected} (parent + fils)")

parent_dict = None
if parent_df.empty:
    st.warning(
        "Le parent (xxxxx) n'existe pas comme ligne distincte dans le JSON. "
        "Le groupe affichera uniquement les fils."
    )
else:
    parent_dict = parent_df.iloc[0].to_dict()

    c1, c2, c3 = st.columns(3)
    c1.write(f"**Parent** : {parent_dict.get('Dossier N','')}")
    c2.write(f"**Nom** : {parent_dict.get('Nom','')}")
    c3.write(f"**Date** : {parent_dict.get('Date','')}")

    c4, c5, c6 = st.columns(3)
    c4.write(f"**Catégorie** : {parent_dict.get('Categories','')}")
    c5.write(f"**Sous-catégorie** : {parent_dict.get('Sous-categories','')}")
    c6.write(f"**Visa** : {parent_dict.get('Visa','')}")

    commentaire_parent = parent_dict.get("Commentaire", "")
    if str(commentaire_parent).strip():
        st.markdown("**📝 Commentaire (parent)**")
        st.write(commentaire_parent)

# =====================================================
# AFFICHAGE FILS
# =====================================================
st.markdown("---")
st.subheader("📎 Sous-dossiers (fils)")

if children_df.empty:
    st.info("Aucun fils pour ce parent (ce cas ne devrait pas arriver avec ce filtre).")
else:
    wanted_cols = [
        "Dossier N", "Nom", "Date",
        "Categories", "Sous-categories", "Visa",
        "Montant honoraires (US $)", "Autres frais (US $)",
        "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4",
        "Date Acompte 1", "Date Acompte 2", "Date Acompte 3", "Date Acompte 4",
        "Mode Acompte 1", "Mode Acompte 2", "Mode Acompte 3", "Mode Acompte 4",
        "mode de paiement",
        "Escrow", "Escrow_a_reclamer", "Escrow_reclame",
        "Dossier envoye", "Dossier accepte", "Dossier refuse", "Dossier Annule", "RFE",
        "Date envoi", "Date acceptation", "Date refus", "Date annulation", "Date reclamation",
        "Commentaire",
    ]
    cols_display = [c for c in wanted_cols if c in children_df.columns]

    st.dataframe(
        children_df.sort_values(["Dossier Index", "Dossier N"])[cols_display],
        use_container_width=True,
    )

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


hon = group_df.get("Montant honoraires (US $)", pd.Series([0] * len(group_df))).apply(to_float).sum()
frais = group_df.get("Autres frais (US $)", pd.Series([0] * len(group_df))).apply(to_float).sum()
total_facture = hon + frais

total_encaisse = 0.0
for i in range(1, 5):
    col = f"Acompte {i}"
    if col in group_df.columns:
        total_encaisse += group_df[col].apply(to_float).sum()

solde = total_facture - total_encaisse

# Escrow = Acompte 1 uniquement, si un des flags escrow est vrai
escrow_flags = pd.Series([False] * len(group_df))
for k in ["Escrow", "Escrow_a_reclamer", "Escrow_reclame"]:
    if k in group_df.columns:
        escrow_flags = escrow_flags | group_df[k].astype(str).str.strip().str.lower().isin(
            ["true", "1", "yes", "oui"]
        )

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

# =====================================================
# ✅ EXPORT PDF (groupe parent + fils)
# =====================================================
st.markdown("---")
st.subheader("📄 Export PDF (groupe)")

if st.button("📄 Exporter la fiche groupe en PDF", type="primary"):
    try:
        # On exporte le parent (si existe) + les fils
        parent_data = parent_dict if parent_dict else {}
        children_data = children_df.sort_values(["Dossier Index", "Dossier N"]).to_dict(orient="records")

        output = f"/tmp/groupe_{parent_selected}.pdf"
        export_groupe_pdf(parent_data, children_data, output)

        with open(output, "rb") as f:
            st.download_button(
                "⬇️ Télécharger le PDF (groupe)",
                data=f,
                file_name=f"Groupe_{parent_selected}.pdf",
                mime="application/pdf",
            )

        st.success("✔ PDF généré avec succès.")

    except Exception as e:
        st.error(f"❌ Erreur export PDF groupe : {e}")