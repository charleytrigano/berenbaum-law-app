import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database
import plotly.express as px

st.set_page_config(page_title="Analyses", page_icon="📊", layout="wide")
st.title("📊 Analyses & Statistiques")
st.write("Visualisez les performances globales du cabinet.")

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------
db = load_database()

clients = pd.DataFrame(db.get("clients", []))
visa = pd.DataFrame(db.get("visa", []))
escrow = pd.DataFrame(db.get("escrow", []))

if clients.empty:
    st.info("Aucun dossier client trouvé.")
    st.stop()

# ---------------------------------------------------
# 📌 INDICATEURS PRINCIPAUX (sécurisés)
# ---------------------------------------------------
st.subheader("📌 Indicateurs principaux")

total_dossiers = len(clients)

def safe_boolean(colname):
    if colname not in clients.columns:
        return pd.Series([False] * len(clients))
    return clients[colname].astype(str).str.strip().str.len() > 0

acceptes = safe_boolean("Date acceptation")
refuses = safe_boolean("Date refus")
annules = safe_boolean("Date annulation")

taux_accept = (acceptes.sum() / total_dossiers) * 100
taux_refus = (refuses.sum() / total_dossiers) * 100
taux_annul = (annules.sum() / total_dossiers) * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total dossiers", total_dossiers)
col2.metric("Acceptés", f"{taux_accept:.1f}%")
col3.metric("Refusés", f"{taux_refus:.1f}%")
col4.metric("Annulés", f"{taux_annul:.1f}%")

st.markdown("---")

# ---------------------------------------------------
# 📁 Répartition par catégorie
# ---------------------------------------------------
st.subheader("📁 Répartition par catégorie")

if "Catégories" in clients.columns:
    fig_cat = px.pie(
        clients,
        names="Catégories",
        title="Répartition des dossiers par catégorie",
    )
    st.plotly_chart(fig_cat, use_container_width=True)
else:
    st.info("Aucune catégorie trouvée.")

st.markdown("---")

# ---------------------------------------------------
# 🛂 Répartition des visas
# ---------------------------------------------------
st.subheader("🛂 Répartition des types de Visa")

if "Visa" in clients.columns:
    fig_visa = px.pie(
        clients,
        names="Visa",
        title="Répartition des dossiers Visa",
    )
    st.plotly_chart(fig_visa, use_container_width=True)
else:
    st.info("Aucun Visa enregistré.")

st.markdown("---")

# ---------------------------------------------------
# 📆 Dossiers envoyés par mois
# ---------------------------------------------------
st.subheader("📆 Volume de dossiers par mois")

if "Date envoi" in clients.columns:
    df_months = clients.copy()
    df_months["Date envoi"] = pd.to_datetime(df_months["Date envoi"], errors="coerce")
    df_months["Mois"] = df_months["Date envoi"].dt.to_period("M")

    df_count = df_months["Mois"].value_counts().sort_index()

    fig_mois = px.bar(
        df_count,
        title="Nombre de dossiers envoyés par mois",
        labels={'value': 'Nombre de dossiers', 'index': 'Mois'},
    )
    st.plotly_chart(fig_mois, use_container_width=True)
else:
    st.info("Aucune date d'envoi disponible.")

st.markdown("---")

# ---------------------------------------------------
# 💰 Analyse ESCROW
# ---------------------------------------------------
st.subheader("💰 Mouvements Escrow")

if not escrow.empty:

    if "Montant" not in escrow.columns:
        st.info("Aucun montant Escrow enregistré.")
    else:
        escrow["Montant"] = pd.to_numeric(escrow["Montant"], errors="coerce").fillna(0)
        total_escrow = escrow["Montant"].sum()

        st.metric("Total Escrow enregistré", f"${total_escrow:,.2f}")

        if "Date envoi" in escrow.columns:
            escrow["Date envoi"] = pd.to_datetime(escrow["Date envoi"], errors="coerce")
            escrow["Mois"] = escrow["Date envoi"].dt.to_period("M")

            df_escrow_mois = escrow.groupby("Mois")["Montant"].sum()

            fig_escrow = px.line(
                df_escrow_mois,
                title="Évolution mensuelle des fonds Escrow",
                labels={"value": "Montant", "index": "Mois"},
                markers=True,
            )
            st.plotly_chart(fig_escrow, use_container_width=True)
else:
    st.info("Aucun mouvement Escrow enregistré.")
