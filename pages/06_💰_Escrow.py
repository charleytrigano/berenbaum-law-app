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
    st.info("Aucun dossier disponible.")
    st.stop()

df = pd.DataFrame(clients).copy()
df["Dossier N"] = df["Dossier N"].astype(str)

# =====================================================
# OUTILS
# =====================================================
def to_float(v):
    try:
        return float(v or 0)
    except:
        return 0.0

def total_acomptes(row):
    return sum(to_float(row.get(f"Acompte {i}", 0)) for i in range(1, 5))

def statut_escrow(row):
    if row.get("Escrow_reclame"):
        return "reclame"
    if row.get("Dossier accepte") or row.get("Dossier refuse") or row.get("Dossier Annule"):
        return "a_reclamer"
    return "actif"

# =====================================================
# CALCUL ESCROW DYNAMIQUE
# =====================================================
df["Montant Escrow"] = df.apply(total_acomptes, axis=1)
df["Etat Escrow"] = df.apply(statut_escrow, axis=1)

# =====================================================
# TABS
# =====================================================
tab1, tab2, tab3 = st.tabs([
    "🔵 Escrow actif",
    "🟡 Escrow à réclamer",
    "🟢 Escrow réclamé"
])

# =====================================================
# TAB 1 — ESCROW ACTIF
# =====================================================
with tab1:
    actif = df[df["Etat Escrow"] == "actif"]
    if actif.empty:
        st.info("Aucun escrow actif.")
    else:
        st.dataframe(
            actif[[
                "Dossier N", "Nom", "Visa",
                "Montant Escrow"
            ]],
            use_container_width=True
        )

# =====================================================
# TAB 2 — ESCROW À RÉCLAMER
# =====================================================
with tab2:
    a_reclamer = df[df["Etat Escrow"] == "a_reclamer"]
    if a_reclamer.empty:
        st.info("Aucun escrow à réclamer.")
    else:
        for _, row in a_reclamer.iterrows():
            with st.container(border=True):
                st.write(
                    f"**Dossier {row['Dossier N']} — {row.get('Nom','')}**  \n"
                    f"Montant : **${row['Montant Escrow']:,.2f}**"
                )

                if st.button(
                    f"✅ Marquer comme réclamé ({row['Dossier N']})",
                    key=f"reclame_{row['Dossier N']}"
                ):
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    history.append({
                        "Dossier N": row["Dossier N"],
                        "Ancien_etat": "Escrow à réclamer",
                        "Nouvel_etat": "Escrow réclamé",
                        "Montant": row["Montant Escrow"],
                        "Date": now,
                        "Motif": "Action manuelle"
                    })

                    df.loc[df["Dossier N"] == row["Dossier N"], "Escrow_reclame"] = True

                    db["clients"] = df.to_dict(orient="records")
                    db["escrow_history"] = history
                    save_database(db)

                    st.success("✔ Escrow marqué comme réclamé")
                    st.rerun()

# =====================================================
# TAB 3 — ESCROW RÉCLAMÉ
# =====================================================
with tab3:
    reclame = df[df["Etat Escrow"] == "reclame"]
    if reclame.empty:
        st.info("Aucun escrow réclamé.")
    else:
        st.dataframe(
            reclame[[
                "Dossier N", "Nom", "Visa",
                "Montant Escrow"
            ]],
            use_container_width=True
        )

# =====================================================
# HISTORIQUE
# =====================================================
st.markdown("---")
st.subheader("🕓 Historique des escrows")

if history:
    st.dataframe(
        pd.DataFrame(history).sort_values("Date", ascending=False),
        use_container_width=True
    )
else:
    st.info("Aucun historique enregistré.")