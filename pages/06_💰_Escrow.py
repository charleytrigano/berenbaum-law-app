import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database
from utils.sidebar import render_sidebar

# ---------------------------------------------------------
# Sidebar (Logo + Menu)
# ---------------------------------------------------------
render_sidebar()

st.set_page_config(page_title="💰 Escrow", page_icon="💰", layout="wide")
st.title("💰 Gestion complète de l’Escrow")

# ---------------------------------------------------------
# Charger base
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
df = pd.DataFrame(clients)

if df.empty:
    st.warning("Aucun dossier trouvé.")
    st.stop()

# ---------------------------------------------------------
# Normalisation colonnes
# ---------------------------------------------------------
def normalize_bool(x):
    if isinstance(x, bool):
        return x
    if str(x).lower() in ["1", "true", "yes", "oui"]:
        return True
    return False

for col in ["Escrow", "Escrow_a_reclamer", "Escrow_reclame"]:
    if col not in df.columns:
        df[col] = False
    df[col] = df[col].apply(normalize_bool)

df["Acompte 1"] = pd.to_numeric(df.get("Acompte 1", 0), errors="coerce").fillna(0)
df["Date Acompte 1"] = df.get("Date Acompte 1", "").replace("None", "")

# ---------------------------------------------------------
# Calcul du montant escrow = Acompte 1
# ---------------------------------------------------------
df["Montant Escrow"] = df["Acompte 1"]

# ---------------------------------------------------------
# Séparation des statuts
# ---------------------------------------------------------
df_en_cours = df[(df["Escrow"] == True) & 
                 (df["Escrow_a_reclamer"] == False) & 
                 (df["Escrow_reclame"] == False)].copy()

df_a_reclamer = df[(df["Escrow_a_reclamer"] == True) & 
                   (df["Escrow_reclame"] == False)].copy()

df_reclame = df[df["Escrow_reclame"] == True].copy()

# ---------------------------------------------------------
# Onglets
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["🟡 En cours", "🟠 À réclamer", "🟢 Réclamé"])

# ---------------------------------------------------------
# 🟡 TAB 1 — ESCROW EN COURS
# ---------------------------------------------------------
with tab1:
    st.header("🟡 Escrow en cours")
    if df_en_cours.empty:
        st.info("Aucun dossier en Escrow.")
    else:
        st.dataframe(df_en_cours[[
            "Dossier N", "Nom", "Visa", "Montant Escrow", "Date Acompte 1"
        ]], use_container_width=True)

        # Action : passer à réclamer
        dossier_ids = df_en_cours["Dossier N"].tolist()
        choix = st.selectbox("Sélectionner un dossier à passer en 'À réclamer'", dossier_ids)

        if st.button("➡️ Passer en Escrow À réclamer"):
            idx = df[df["Dossier N"] == choix].index[0]
            df.loc[idx, "Escrow"] = False
            df.loc[idx, "Escrow_a_reclamer"] = True
            df.loc[idx, "Escrow_reclame"] = False
            db["clients"] = df.to_dict(orient="records")
            save_database(db)
            st.success("✔ Statut mis à jour.")
            st.rerun()

# ---------------------------------------------------------
# 🟠 TAB 2 — ESCROW À RÉCLAMER
# ---------------------------------------------------------
with tab2:
    st.header("🟠 Escrow à réclamer")
    if df_a_reclamer.empty:
        st.info("Aucun dossier à réclamer.")
    else:
        st.dataframe(df_a_reclamer[[
            "Dossier N", "Nom", "Visa", "Montant Escrow", "Date Acompte 1"
        ]], use_container_width=True)

        choix2 = st.selectbox("Sélectionner un dossier à marquer comme réclamé", df_a_reclamer["Dossier N"])

        if st.button("✔️ Marquer comme réclamé"):
            idx = df[df["Dossier N"] == choix2].index[0]
            df.loc[idx, "Escrow"] = False
            df.loc[idx, "Escrow_a_reclamer"] = False
            df.loc[idx, "Escrow_reclame"] = True
            db["clients"] = df.to_dict(orient="records")
            save_database(db)
            st.success("✔ Escrow marqué comme réclamé.")
            st.rerun()

# ---------------------------------------------------------
# 🟢 TAB 3 — ESCROW RÉCLAMÉ
# ---------------------------------------------------------
with tab3:
    st.header("🟢 Escrow réclamé")
    if df_reclame.empty:
        st.info("Aucun Escrow réclamé pour l’instant.")
    else:
        st.dataframe(df_reclame[[
            "Dossier N", "Nom", "Visa", "Montant Escrow", "Date Acompte 1"
        ]], use_container_width=True)

        choix3 = st.selectbox("Sélectionner un dossier pour supprimer l'Escrow", df_reclame["Dossier N"])

        if st.button("❌ Supprimer complètement l’Escrow"):
            idx = df[df["Dossier N"] == choix3].index[0]
            df.loc[idx, "Escrow"] = False
            df.loc[idx, "Escrow_a_reclamer"] = False
            df.loc[idx, "Escrow_reclame"] = False
            db["clients"] = df.to_dict(orient="records")
            save_database(db)
            st.success("✔ Escrow supprimé.")
            st.rerun()

# ---------------------------------------------------------
# TOTAL DES ESCROWS
# ---------------------------------------------------------
total = df[df["Escrow"] == True]["Montant Escrow"].sum()
total += df[df["Escrow_a_reclamer"] == True]["Montant Escrow"].sum()

st.markdown(f"""
# 💵 Total Escrow en attente : **${total:,.2f}**
""")
