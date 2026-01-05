# pages/12_📁_Fiche_groupe_dossier.py

import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database
from utils.status_utils import normalize_bool
from utils.pdf_export_groupe import export_groupe_pdf

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(
    page_title="📁 Fiche groupe dossier",
    page_icon="📁",
    layout="wide"
)
render_sidebar()
st.title("📁 Fiche groupe dossier (parent + sous-dossiers)")

# =====================================================
# LOAD DATABASE
# =====================================================
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.error("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients).copy()
df["Dossier N"] = df["Dossier N"].astype(str).str.strip()

# =====================================================
# HIERARCHIE DOSSIERS
# =====================================================
def get_parent(dn: str) -> str:
    return dn.split("-", 1)[0] if "-" in dn else dn

def get_index(dn: str) -> int:
    if "-" not in dn:
        return 0
    try:
        return int(dn.split("-", 1)[1])
    except:
        return 0

df["Dossier Parent"] = df["Dossier N"].apply(get_parent)
df["Dossier Index"] = df["Dossier N"].apply(get_index)
df["Est Parent"] = df["Dossier Index"] == 0
df["Est Fils"] = df["Dossier Index"] > 0

# =====================================================
# PARENTS AYANT AU MOINS UN FILS
# =====================================================
parents_avec_fils = (
    df[df["Est Fils"]]["Dossier Parent"]
    .dropna()
    .unique()
    .tolist()
)

def sort_parent(x):
    return int(x) if x.isdigit() else x

parents_avec_fils = sorted(parents_avec_fils, key=sort_parent)

if not parents_avec_fils:
    st.info("Aucun groupe parent + fils détecté.")
    st.stop()

# =====================================================
# LABELS FILTRE : Dossier N + Nom
# =====================================================
def label_parent(pid):
    parent = df[(df["Dossier N"] == pid) & (df["Est Parent"])]
    if not parent.empty:
        nom = parent.iloc[0].get("Nom", "")
        return f"{pid} — {nom}" if nom else pid

    fils = df[(df["Dossier Parent"] == pid) & (df["Est Fils"])]
    if not fils.empty:
        nom = fils.iloc[0].get("Nom", "")
        return f"{pid} — {nom}" if nom else pid

    return pid

parent_selected = st.selectbox(
    "Sélectionner un groupe (Dossier N + Nom)",
    parents_avec_fils,
    format_func=label_parent
)

# =====================================================
# GROUPE SELECTIONNE
# =====================================================
group_df = df[df["Dossier Parent"] == parent_selected].copy()
group_df = group_df.sort_values(["Dossier Index", "Dossier N"])

parent_df = group_df[group_df["Est Parent"]]
children_df = group_df[group_df["Est Fils"]]

# =====================================================
# FONCTION ESCROW — REGLE OFFICIELLE
# =====================================================
def compute_escrow(row):
    if (
        normalize_bool(row.get("Dossier accepte"))
        or normalize_bool(row.get("Dossier refuse"))
        or normalize_bool(row.get("Dossier Annule"))
    ):
        return 0.0

    total = 0.0
    for i in range(1, 5):
        try:
            total += float(row.get(f"Acompte {i}", 0) or 0)
        except:
            pass
    return total

group_df["Escrow Montant"] = group_df.apply(compute_escrow, axis=1)

# =====================================================
# AFFICHAGE PARENT
# =====================================================
st.markdown("---")
st.subheader(f"📄 Groupe {parent_selected}")

parent_dict = None
if not parent_df.empty:
    parent_dict = parent_df.iloc[0].to_dict()

    c1, c2, c3 = st.columns(3)
    c1.write(f"**Dossier parent** : {parent_dict.get('Dossier N','')}")
    c2.write(f"**Nom** : {parent_dict.get('Nom','')}")
    c3.write(f"**Date** : {parent_dict.get('Date','')}")

    c4, c5, c6 = st.columns(3)
    c4.write(f"**Catégorie** : {parent_dict.get('Categories','')}")
    c5.write(f"**Sous-catégorie** : {parent_dict.get('Sous-categories','')}")
    c6.write(f"**Visa** : {parent_dict.get('Visa','')}")

    if parent_dict.get("Commentaire"):
        st.markdown("**📝 Commentaire (parent)**")
        st.write(parent_dict.get("Commentaire"))

# =====================================================
# AFFICHAGE FILS
# =====================================================
st.markdown("---")
st.subheader("📎 Sous-dossiers")

if children_df.empty:
    st.info("Aucun sous-dossier pour ce parent.")
else:
    display_cols = [
        "Dossier N", "Nom", "Visa",
        "Montant honoraires (US $)", "Autres frais (US $)",
        "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4",
        "Date Acompte 1", "Date Acompte 2", "Date Acompte 3", "Date Acompte 4",
        "Escrow Montant",
        "Dossier envoye", "Dossier accepte", "Dossier refuse", "Dossier Annule",
        "Commentaire"
    ]
    cols = [c for c in display_cols if c in children_df.columns]

    st.dataframe(
        children_df[cols],
        use_container_width=True
    )

# =====================================================
# KPI GROUPE
# =====================================================
st.markdown("---")
st.subheader("📊 KPI du groupe")

def to_float(v):
    try:
        return float(v or 0)
    except:
        return 0.0

hon = group_df["Montant honoraires (US $)"].apply(to_float).sum()
frais = group_df["Autres frais (US $)"].apply(to_float).sum()
total_facture = hon + frais

total_encaisse = sum(
    group_df.get(f"Acompte {i}", 0).apply(to_float).sum()
    for i in range(1, 5)
)

solde = total_facture - total_encaisse
escrow_total = group_df["Escrow Montant"].sum()

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Dossiers (groupe)", len(group_df))
k2.metric("Honoraires", f"${hon:,.2f}")
k3.metric("Autres frais", f"${frais:,.2f}")
k4.metric("Total facturé", f"${total_facture:,.2f}")
k5.metric("Total encaissé", f"${total_encaisse:,.2f}")
k6.metric("Escrow total", f"${escrow_total:,.2f}")

st.info(f"💡 Solde global du groupe : ${solde:,.2f}")

# =====================================================
# EXPORT PDF GROUPE
# =====================================================
st.markdown("---")
st.subheader("📄 Export PDF")

if st.button("📄 Exporter la fiche groupe en PDF", type="primary"):
    try:
        parent_data = parent_dict if parent_dict else {}
        children_data = children_df.to_dict(orient="records")

        output = f"/tmp/groupe_{parent_selected}.pdf"
        export_groupe_pdf(parent_data, children_data, output)

        with open(output, "rb") as f:
            st.download_button(
                "⬇️ Télécharger le PDF",
                f,
                file_name=f"Groupe_{parent_selected}.pdf",
                mime="application/pdf"
            )

        st.success("✔ PDF généré avec succès.")

    except Exception as e:
        st.error(f"❌ Erreur export PDF groupe : {e}")