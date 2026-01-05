import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database


# =====================================================
# HELPERS
# =====================================================
def to_float(v):
    try:
        return float(v or 0)
    except Exception:
        return 0.0


def sum_acomptes(row):
    return sum(to_float(row.get(f"Acompte {i}", 0)) for i in range(1, 5))


def dossier_est_cloture(row):
    return (
        bool(row.get("Dossier accepte", False))
        or bool(row.get("Dossier refuse", False))
        or bool(row.get("Dossier Annule", False))
    )


# =====================================================
# CONFIG
# =====================================================
st.set_page_config(page_title="💰 Escrow", page_icon="💰", layout="wide")
render_sidebar()
st.title("💰 Gestion des Escrows")

# =====================================================
# LOAD DATABASE
# =====================================================
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.error("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients).copy()
df["Dossier N"] = df["Dossier N"].astype(str)

# =====================================================
# CALCUL LOGIQUE ESCROW (CENTRALISÉ)
# =====================================================
df["Montant Escrow"] = df.apply(sum_acomptes, axis=1)

df["Etat Escrow"] = "Aucun"

df.loc[
    (df["Montant Escrow"] > 0) & (~df.apply(dossier_est_cloture, axis=1)),
    "Etat Escrow",
] = "Escrow actif"

df.loc[
    (df["Montant Escrow"] > 0) & (df.apply(dossier_est_cloture, axis=1)),
    "Etat Escrow",
] = "Escrow à réclamer"

df.loc[df.get("Escrow_reclame", False) == True, "Etat Escrow"] = "Escrow réclamé"

# =====================================================
# FILTRE ÉTAT
# =====================================================
st.subheader("🎯 Filtrer les escrows")

etat_filtre = st.multiselect(
    "État Escrow",
    options=["Escrow actif", "Escrow à réclamer", "Escrow réclamé"],
    default=["Escrow actif", "Escrow à réclamer"],
)

df_view = df[df["Etat Escrow"].isin(etat_filtre)].copy()

# =====================================================
# KPI
# =====================================================
st.markdown("---")
k1, k2, k3 = st.columns(3)

k1.metric("Dossiers", len(df_view))
k2.metric(
    "Montant total Escrow",
    f"${df_view['Montant Escrow'].sum():,.2f}",
)
k3.metric(
    "Dossiers à réclamer",
    len(df_view[df_view["Etat Escrow"] == "Escrow à réclamer"]),
)

# =====================================================
# TABLEAU DES DOSSIERS EN ESCROW
# =====================================================
st.markdown("---")
st.subheader("📋 Dossiers en Escrow")

if df_view.empty:
    st.info("Aucun dossier correspondant aux filtres.")
else:
    cols = [
        "Dossier N",
        "Nom",
        "Visa",
        "Etat Escrow",
        "Montant Escrow",
        "Acompte 1",
        "Acompte 2",
        "Acompte 3",
        "Acompte 4",
        "Date",
    ]

    cols_display = [c for c in cols if c in df_view.columns]

    st.dataframe(
        df_view.sort_values("Dossier N")[cols_display],
        use_container_width=True,
    )

# =====================================================
# ACTIONS (TRANSITIONS)
# =====================================================
st.markdown("---")
st.subheader("⚙️ Actions Escrow")

selected = st.selectbox(
    "Sélectionner un dossier",
    df_view["Dossier N"].unique().tolist() if not df_view.empty else [],
)

if selected:
    row_idx = df[df["Dossier N"] == selected].index[0]

    c1, c2 = st.columns(2)

    if c1.button("📤 Marquer comme Escrow à réclamer"):
        df.loc[row_idx, "Escrow"] = False
        df.loc[row_idx, "Escrow_a_reclamer"] = True
        df.loc[row_idx, "Escrow_reclame"] = False

        db["clients"] = df.to_dict(orient="records")
        save_database(db)
        st.success("✔ Dossier passé en Escrow à réclamer")
        st.rerun()

    if c2.button("✅ Marquer comme Escrow réclamé"):
        df.loc[row_idx, "Escrow"] = False
        df.loc[row_idx, "Escrow_a_reclamer"] = False
        df.loc[row_idx, "Escrow_reclame"] = True

        db["clients"] = df.to_dict(orient="records")
        save_database(db)
        st.success("✔ Dossier passé en Escrow réclamé")
        st.rerun()

st.markdown("---")
st.subheader("🕓 Historique des escrows")

history = db.get("escrow_history", [])

if not history:
    st.info("Aucun historique escrow pour le moment.")
else:
    hist_df = pd.DataFrame(history)
    st.dataframe(
        hist_df.sort_values("Date", ascending=False),
        use_container_width=True
    )

st.download_button(
    "⬇️ Exporter l’historique Escrow (CSV)",
    data=hist_df.to_csv(index=False),
    file_name="historique_escrow.csv",
    mime="text/csv"
)