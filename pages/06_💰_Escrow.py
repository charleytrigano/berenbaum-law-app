import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database
from utils.status_utils import normalize_bool

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
    st.info("Aucun dossier disponible.")
    st.stop()

df = pd.DataFrame(clients).copy()

# Normalisation
df["Dossier N"] = df["Dossier N"].astype(str)

for col in [
    "Dossier accepte",
    "Dossier refuse",
    "Dossier Annule",
    "Escrow",
    "Escrow_a_reclamer",
    "Escrow_reclame",
]:
    if col not in df.columns:
        df[col] = False
    df[col] = df[col].apply(normalize_bool)

# =====================================================
# CALCUL ESCROW (NOUVELLE RÈGLE VALIDÉE)
# =====================================================
def calc_escrow_amount(row):
    """
    Tant que le dossier n'est PAS accepté / refusé / annulé :
    → tous les acomptes sont en escrow
    """
    if row["Dossier accepte"] or row["Dossier refuse"] or row["Dossier Annule"]:
        return 0.0

    total = 0.0
    for i in range(1, 5):
        try:
            total += float(row.get(f"Acompte {i}", 0) or 0)
        except:
            pass
    return total


df["Escrow Montant"] = df.apply(calc_escrow_amount, axis=1)

# =====================================================
# FILTRAGE PAR ÉTAT ESCROW
# =====================================================
tab1, tab2, tab3 = st.tabs([
    "💼 Escrow actif",
    "📤 Escrow à réclamer",
    "✅ Escrow réclamé",
])

# =====================================================
# AFFICHAGE FONCTION
# =====================================================
def render_table(df_view, action=None):
    if df_view.empty:
        st.info("Aucun dossier dans cet état.")
        return

    for _, row in df_view.iterrows():
        with st.container():
            c1, c2, c3, c4, c5 = st.columns([2, 3, 2, 2, 2])

            c1.write(f"**{row['Dossier N']}**")
            c2.write(row.get("Nom", ""))
            c3.write(f"${row['Escrow Montant']:,.2f}")

            if action == "to_reclamer":
                if c4.button("➡️ Passer à réclamer", key=f"reclamer_{row.name}"):
                    df.loc[row.name, "Escrow"] = False
                    df.loc[row.name, "Escrow_a_reclamer"] = True
                    df.loc[row.name, "Escrow_reclame"] = False

            elif action == "to_reclame":
                if c4.button("✅ Marquer réclamé", key=f"reclame_{row.name}"):
                    df.loc[row.name, "Escrow"] = False
                    df.loc[row.name, "Escrow_a_reclamer"] = False
                    df.loc[row.name, "Escrow_reclame"] = True

            else:
                c4.write("—")

            c5.write("")

            st.markdown("---")


# =====================================================
# TAB 1 — ESCROW ACTIF
# =====================================================
with tab1:
    st.subheader("💼 Escrow actif")

    view = df[
        (df["Escrow"])
        & (df["Escrow Montant"] > 0)
    ]

    render_table(view, action="to_reclamer")

# =====================================================
# TAB 2 — ESCROW À RÉCLAMER
# =====================================================
with tab2:
    st.subheader("📤 Escrow à réclamer")

    view = df[
        (df["Escrow_a_reclamer"])
        & (df["Escrow Montant"] > 0)
    ]

    render_table(view, action="to_reclame")

# =====================================================
# TAB 3 — ESCROW RÉCLAMÉ
# =====================================================
with tab3:
    st.subheader("✅ Escrow réclamé")

    view = df[
        (df["Escrow_reclame"])
    ]

    render_table(view)

# =====================================================
# SAVE CHANGES
# =====================================================
if st.button("💾 Enregistrer les changements Escrow", type="primary"):
    db["clients"] = df.drop(columns=["Escrow Montant"]).to_dict(orient="records")
    save_database(db)
    st.success("✔ États Escrow mis à jour avec succès.")
    st.rerun()