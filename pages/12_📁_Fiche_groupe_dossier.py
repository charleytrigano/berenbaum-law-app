import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database
from utils.pdf_export_groupe import export_groupe_pdf

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(
    page_title="📂 Fiche groupe de dossiers",
    page_icon="📂",
    layout="wide"
)
render_sidebar()
st.title("📂 Fiche groupe de dossiers")

# =====================================================
# LOAD DATABASE
# =====================================================
db = load_database()
df = pd.DataFrame(db.get("clients", []))

def split_dossier(n):
    s = str(n)
    if "-" in s:
        p, i = s.split("-", 1)
        return p, int(i)
    return s, 0

df[["Dossier Parent", "Dossier Index"]] = df["Dossier N"].apply(
    lambda x: pd.Series(split_dossier(x))
)

parents = sorted(
    df[df["Dossier Index"] == 0]["Dossier Parent"].unique(),
    key=lambda x: int(x)
)

parent_id = st.selectbox("📂 Sélectionner un dossier parent", parents)

group = df[df["Dossier Parent"] == parent_id].sort_values("Dossier Index").copy()
parent_row = group[group["Dossier Index"] == 0].iloc[0]
children = group.to_dict(orient="records")

# =====================================================
# KPI CONSOLIDÉS
# =====================================================
st.subheader("📊 Indicateurs consolidés du groupe")

total_facture = (
    group["Montant honoraires (US $)"].sum()
    + group["Autres frais (US $)"].sum()
)

total_encaisse = (
    group["Acompte 1"].sum()
    + group["Acompte 2"].sum()
    + group["Acompte 3"].sum()
    + group["Acompte 4"].sum()
)

solde = total_facture - total_encaisse

escrow_total = group[group["Escrow"] == True]["Acompte 1"].sum()
escrow_a = group[group["Escrow_a_reclamer"] == True]["Acompte 1"].sum()
escrow_r = group[group["Escrow_reclame"] == True]["Acompte 1"].sum()

c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("Dossiers", len(group))
c2.metric("Total facturé", f"${total_facture:,.2f}")
c3.metric("Total encaissé", f"${total_encaisse:,.2f}")
c4.metric("Solde global", f"${solde:,.2f}")
c5.metric("Escrow actif", f"${escrow_total:,.2f}")
c6.metric("Escrow à réclamer", f"${escrow_a:,.2f}")

st.markdown("---")

# =====================================================
# EXPORT PDF
# =====================================================
if st.button("📄 Exporter le groupe en PDF"):
    pdf_buffer = export_groupe_pdf(
        parent_id=parent_id,
        parent_row=parent_row,
        children_rows=children
    )

    st.download_button(
        label="⬇️ Télécharger le PDF",
        data=pdf_buffer,
        file_name=f"Groupe_{parent_id}.pdf",
        mime="application/pdf"
    )

# =====================================================
# DÉTAIL DES DOSSIERS
# =====================================================
st.subheader("📑 Détails des dossiers")

st.dataframe(
    group[
        [
            "Dossier N", "Nom", "Categories", "Sous-categories", "Visa",
            "Montant honoraires (US $)", "Autres frais (US $)",
            "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4",
            "Escrow", "Escrow_a_reclamer", "Escrow_reclame"
        ]
    ],
    use_container_width=True
)