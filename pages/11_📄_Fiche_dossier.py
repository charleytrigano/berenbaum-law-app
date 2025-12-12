import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database
from utils.consolidation_utils import (
    get_family,
    compute_consolidated_metrics
)

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="📄 Fiche dossier", page_icon="📄", layout="wide")
render_sidebar()
st.title("📄 Fiche dossier")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)
df["Dossier N"] = df["Dossier N"].astype(str)

# ---------------------------------------------------------
# SELECTION DOSSIER
# ---------------------------------------------------------
dossier_ids = sorted(df["Dossier N"].unique())
selected_id = st.selectbox("Sélectionner un dossier", dossier_ids)

dossier = df[df["Dossier N"] == selected_id].iloc[0]

# ---------------------------------------------------------
# INFOS DOSSIER
# ---------------------------------------------------------
st.subheader("📌 Informations principales")

c1, c2, c3 = st.columns(3)
c1.write(f"**Dossier N** : {dossier['Dossier N']}")
c2.write(f"**Nom** : {dossier['Nom']}")
c3.write(f"**Date** : {dossier['Date']}")

c4, c5, c6 = st.columns(3)
c4.write(f"**Catégorie** : {dossier['Categories']}")
c5.write(f"**Sous-catégorie** : {dossier['Sous-categories']}")
c6.write(f"**Visa** : {dossier['Visa']}")

# ---------------------------------------------------------
# CONSOLIDATION PARENT / ENFANTS
# ---------------------------------------------------------
st.markdown("---")
st.subheader("💼 Vue financière consolidée")

family_df = get_family(df, dossier["Dossier N"])
metrics = compute_consolidated_metrics(family_df)

k1, k2, k3 = st.columns(3)
k1.metric("Total facturé", f"${metrics['total_facture']:,.2f}")
k2.metric("Total encaissé", f"${metrics['total_encaisse']:,.2f}")
k3.metric("Solde global dû", f"${metrics['solde_du']:,.2f}")

k4, k5, k6 = st.columns(3)
k4.metric("Escrow total", f"${metrics['escrow_total']:,.2f}")
k5.metric("Escrow à réclamer", f"${metrics['escrow_a_reclamer']:,.2f}")
k6.metric("Escrow réclamé", f"${metrics['escrow_reclame']:,.2f}")

# ---------------------------------------------------------
# DETAILS PAR DOSSIER
# ---------------------------------------------------------
st.markdown("### 📋 Détails par dossier (parent + sous-dossiers)")

st.dataframe(
    family_df[
        [
            "Dossier N",
            "Montant honoraires (US $)",
            "Acompte 1",
            "Acompte 2",
            "Acompte 3",
            "Acompte 4",
            "Escrow",
            "Escrow_a_reclamer",
            "Escrow_reclame",
        ]
    ],
    use_container_width=True,
)
