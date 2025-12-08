import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")
st.title("🏠 Dashboard — Berenbaum Law App")

# ---------------------------------------------------------
# 🔹 Charger la base JSON
# ---------------------------------------------------------
db = load_database()
clients = pd.DataFrame(db.get("clients", []))

if clients.empty:
    st.warning("Aucun dossier trouvé.")
    st.stop()

# Convertir dates
clients["Date"] = pd.to_datetime(clients["Date"], errors="coerce")

# ---------------------------------------------------------
# 🔹 KPIs
# ---------------------------------------------------------
total_dossiers = len(clients)
dossiers_envoyes = clients["Dossier envoye"].sum()
escrow_en_cours = clients["Escrow"].sum()
escrow_a_reclamer = clients["Escrow_a_reclamer"].sum()
escrow_reclame = clients["Escrow_reclame"].sum()

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("📁 Total dossiers", total_dossiers)
col2.metric("📨 Dossiers envoyés", dossiers_envoyes)
col3.metric("💰 Escrow en cours", escrow_en_cours)
col4.metric("🟧 Escrow à réclamer", escrow_a_reclamer)
col5.metric("🟩 Escrow réclamé", escrow_reclame)

st.markdown("---")

# ---------------------------------------------------------
# 🔹 Alerte : Escrow à réclamer
# ---------------------------------------------------------
if escrow_a_reclamer > 0:
    st.warning(f"⚠️ {escrow_a_reclamer} dossier(s) ont un Escrow à réclamer.")

# ---------------------------------------------------------
# 🔹 Alerte : dossiers sans visa
# ---------------------------------------------------------
missing_visa = clients[clients["Visa"] == ""]
if not missing_visa.empty:
    st.error(f"❗ {len(missing_visa)} dossier(s) sans Visa renseigné.")

# ---------------------------------------------------------
# 🔹 Graphique — Dossiers par mois
# ---------------------------------------------------------
st.subheader("📅 Dossiers créés par mois")

clients["Mois"] = clients["Date"].dt.to_period("M").astype(str)

df_month = clients.groupby("Mois").size().reset_index(name="Nombre")

st.line_chart(df_month, x="Mois", y="Nombre")

st.markdown("---")

# ---------------------------------------------------------
# 🔹 Répartition par Visa
# ---------------------------------------------------------
st.subheader("🛂 Répartition des dossiers par type de Visa")

df_visa = clients["Visa"].value_counts().reset_index()
df_visa.columns = ["Visa", "Nombre"]

st.bar_chart(df_visa, x="Visa", y="Nombre")

st.markdown("---")

# ---------------------------------------------------------
# 🔹 Répartition par Catégorie
# ---------------------------------------------------------
st.subheader("🧩 Répartition par catégorie")

df_cat = clients["Categories"].value_counts().reset_index()
df_cat.columns = ["Catégorie", "Nombre"]

st.bar_chart(df_cat, x="Catégorie", y="Nombre")

st.markdown("---")

# ---------------------------------------------------------
# 🔹 Tableau des alertes Escrow
# ---------------------------------------------------------
st.subheader("⚠️ Détails : Escrow à réclamer")

if escrow_a_reclamer == 0:
    st.info("Aucun Escrow à réclamer.")
else:
    st.dataframe(
        clients[clients["Escrow_a_reclamer"] == True][
            ["Dossier N", "Nom", "Date", "Visa", "Montant honoraires (US $)"]
        ],
        use_container_width=True
    )

