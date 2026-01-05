# pages/08_📤_Export_Excel.py

import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database
from utils.status_utils import normalize_bool

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(
    page_title="📤 Export Excel",
    page_icon="📤",
    layout="wide"
)
render_sidebar()
st.title("📤 Export JSON → Excel (multi-feuilles)")

st.info(
    "Cet export génère un fichier Excel **complet, horodaté**, "
    "fidèle à la base JSON, prêt pour audit ou archivage."
)

# =====================================================
# LOAD DATABASE
# =====================================================
db = load_database()

clients = pd.DataFrame(db.get("clients", []))
visa = pd.DataFrame(db.get("visa", []))
tarifs = pd.DataFrame(db.get("tarifs", []))
tarifs_history = pd.DataFrame(db.get("tarifs_history", []))

if clients.empty:
    st.error("Aucun dossier à exporter.")
    st.stop()

# =====================================================
# NORMALISATION DOSSIERS (parents / fils)
# =====================================================
clients["Dossier N"] = clients["Dossier N"].astype(str).str.strip()

def get_parent(dn):
    return dn.split("-", 1)[0] if "-" in dn else dn

def get_index(dn):
    if "-" not in dn:
        return 0
    try:
        return int(dn.split("-", 1)[1])
    except:
        return 0

clients["Dossier Parent"] = clients["Dossier N"].apply(get_parent)
clients["Dossier Index"] = clients["Dossier N"].apply(get_index)
clients["Est Parent"] = clients["Dossier Index"] == 0
clients["Est Fils"] = clients["Dossier Index"] > 0

# =====================================================
# ESCROW — REGLE METIER OFFICIELLE
# Montant = somme des acomptes tant que dossier
# NON accepté / refusé / annulé
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

clients["Escrow Montant"] = clients.apply(compute_escrow, axis=1)

# =====================================================
# FEUILLE GROUPES (parent + fils)
# =====================================================
groups = []
for parent in clients.loc[clients["Est Fils"], "Dossier Parent"].unique():
    subset = clients[clients["Dossier Parent"] == parent]
    groups.append({
        "Dossier Parent": parent,
        "Nombre dossiers": len(subset),
        "Honoraires total": subset["Montant honoraires (US $)"].fillna(0).sum(),
        "Autres frais total": subset["Autres frais (US $)"].fillna(0).sum(),
        "Total encaissé": sum(
            subset.get(f"Acompte {i}", 0).fillna(0).sum() for i in range(1, 5)
        ),
        "Escrow total": subset["Escrow Montant"].sum()
    })

groups_df = pd.DataFrame(groups)

# =====================================================
# FEUILLE ESCROW
# =====================================================
escrow_df = clients[
    clients["Escrow Montant"] > 0
][[
    "Dossier N", "Nom", "Visa",
    "Escrow Montant",
    "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4"
]]

# =====================================================
# EXPORT EXCEL
# =====================================================
st.markdown("---")
st.subheader("📥 Générer le fichier Excel")

if st.button("📤 Générer et télécharger l’Excel", type="primary"):

    buffer = BytesIO()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"Export_Cabinet_{timestamp}.xlsx"

    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        clients.to_excel(writer, sheet_name="Clients", index=False)
        groups_df.to_excel(writer, sheet_name="Groupes", index=False)
        escrow_df.to_excel(writer, sheet_name="Escrow", index=False)
        visa.to_excel(writer, sheet_name="Visa", index=False)
        tarifs.to_excel(writer, sheet_name="Tarifs", index=False)
        tarifs_history.to_excel(writer, sheet_name="Historique Tarifs", index=False)

    buffer.seek(0)

    st.download_button(
        label="⬇️ Télécharger le fichier Excel",
        data=buffer,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.success("✔ Export Excel généré avec succès.")