import streamlit as st
import pandas as pd
from datetime import datetime

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database

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
history = db.get("escrow_history", [])

if not clients:
    st.warning("Aucun dossier.")
    st.stop()

df = pd.DataFrame(clients).copy()
df["Dossier N"] = df["Dossier N"].astype(str)

# =====================================================
# UTILS
# =====================================================
def to_float(v):
    try:
        return float(v or 0)
    except Exception:
        return 0.0

def total_acomptes(row):
    return sum(to_float(row.get(f"Acompte {i}", 0)) for i in range(1, 5))

def log_history(dossier, old, new, amount, action):
    history.append({
        "Dossier N": dossier.get("Dossier N"),
        "Nom": dossier.get("Nom"),
        "Ancien_etat": old,
        "Nouvel_etat": new,
        "Montant": round(amount, 2),
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Action": action
    })

# =====================================================
# CLASSIFICATION ESCROW
# =====================================================
escrow_actif = []
escrow_a_reclamer = []
escrow_reclame = []

for _, r in df.iterrows():
    if r.get("Escrow_reclame"):
        escrow_reclame.append(r)
    elif r.get("Escrow_a_reclamer"):
        escrow_a_reclamer.append(r)
    elif r.get("Escrow"):
        escrow_actif.append(r)

# =====================================================
# ONGLET ESCROW ACTIF
# =====================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "💼 Escrow actif",
    "📤 Escrow à réclamer",
    "✅ Escrow réclamé",
    "🕓 Historique"
])

# -----------------------------------------------------
# ESCROW ACTIF
# -----------------------------------------------------
with tab1:
    st.subheader("💼 Escrow actif")

    for i, r in enumerate(escrow_actif):
        amount = total_acomptes(r)
        st.markdown(f"**{r['Dossier N']} — {r.get('Nom','')}** — ${amount:,.2f}")

        if st.button(f"➡️ Passer en Escrow à réclamer ({r['Dossier N']})", key=f"to_recl_{i}"):
            idx = df[df["Dossier N"] == r["Dossier N"]].index[0]
            df.loc[idx, "Escrow"] = False
            df.loc[idx, "Escrow_a_reclamer"] = True

            log_history(r, "Escrow actif", "Escrow à réclamer", amount, "Changement manuel")

            db["clients"] = df.to_dict(orient="records")
            db["escrow_history"] = history
            save_database(db)
            st.rerun()

# -----------------------------------------------------
# ESCROW À RÉCLAMER
# -----------------------------------------------------
with tab2:
    st.subheader("📤 Escrow à réclamer")

    for i, r in enumerate(escrow_a_reclamer):
        amount = total_acomptes(r)
        st.markdown(f"**{r['Dossier N']} — {r.get('Nom','')}** — ${amount:,.2f}")

        if st.button(f"✅ Marquer comme réclamé ({r['Dossier N']})", key=f"to_done_{i}"):
            idx = df[df["Dossier N"] == r["Dossier N"]].index[0]
            df.loc[idx, "Escrow_a_reclamer"] = False
            df.loc[idx, "Escrow_reclame"] = True

            log_history(r, "Escrow à réclamer", "Escrow réclamé", amount, "Réclamation effectuée")

            db["clients"] = df.to_dict(orient="records")
            db["escrow_history"] = history
            save_database(db)
            st.rerun()

# -----------------------------------------------------
# ESCROW RÉCLAMÉ
# -----------------------------------------------------
with tab3:
    st.subheader("✅ Escrow réclamé")

    if not escrow_reclame:
        st.info("Aucun escrow réclamé.")
    else:
        df_done = pd.DataFrame(escrow_reclame)
        df_done["Montant"] = df_done.apply(total_acomptes, axis=1)
        st.dataframe(
            df_done[["Dossier N", "Nom", "Montant"]],
            use_container_width=True
        )

# -----------------------------------------------------
# HISTORIQUE
# -----------------------------------------------------
with tab4:
    st.subheader("🕓 Historique des escrows")

    if not history:
        st.info("Aucun historique.")
    else:
        hist_df = pd.DataFrame(history)
        st.dataframe(
            hist_df.sort_values("Date", ascending=False),
            use_container_width=True
        )

        st.download_button(
            "⬇️ Export Excel historique Escrow",
            data=hist_df.to_csv(index=False).encode("utf-8"),
            file_name="historique_escrow.csv",
            mime="text/csv"
        )