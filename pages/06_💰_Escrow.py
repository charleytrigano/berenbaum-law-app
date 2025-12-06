import streamlit as st
import pandas as pd
from datetime import date
from backend.dropbox_utils import load_database, save_database

st.set_page_config(page_title="Escrow", page_icon="💰", layout="wide")
st.title("💰 Gestion des Escrow")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

df = pd.DataFrame(clients)

# Normalisation
df["Acompte 1"] = pd.to_numeric(df.get("Acompte 1", 0), errors="coerce").fillna(0)
df["Dossier envoye"] = df["Dossier envoye"].fillna(0).astype(float)
df["Escrow"] = df["Escrow"].fillna(False)

# Réclamé existe ?
if "Escrow_reclame" not in df.columns:
    df["Escrow_reclame"] = False

if "Date_reclamation" not in df.columns:
    df["Date_reclamation"] = ""

# ---------------------------------------------------------
# TABLEAU 1 — ESCROW EN COURS
# ---------------------------------------------------------
st.subheader("📌 Escrow en cours")

escrow_en_cours = df[(df["Escrow"] == True) & (df["Dossier envoye"] == 0)]

st.dataframe(
    escrow_en_cours[["Dossier N", "Nom", "Acompte 1"]],
    use_container_width=True
)

# ---------------------------------------------------------
# AUTOMATISME :
# Si dossier envoyé → Escrow à réclamer + décoche le Escrow
# ---------------------------------------------------------
df.loc[(df["Dossier envoye"] == 1) & (df["Escrow"] == True), "Escrow"] = False


# ---------------------------------------------------------
# TABLEAU 2 — ESCROW À RÉCLAMER
# ---------------------------------------------------------
st.subheader("📌 Escrow à réclamer")

escrow_a_reclamer = df[
    (df["Dossier envoye"] == 1) &
    (df["Escrow_reclame"] == False)
]

# Affichage
for idx, row in escrow_a_reclamer.iterrows():
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

    col1.write(f"**{row['Dossier N']}** – {row['Nom']}")
    col2.write(f"Montant : **${row['Acompte 1']:,.2f}**")
    col3.write("Prêt à réclamer")

    # Bouton réclamer
    action = col4.button("Réclamer", key=f"reclamer_{idx}")

    if action:
        df.at[idx, "Escrow_reclame"] = True
        df.at[idx, "Date_reclamation"] = str(date.today())
        st.success(f"Escrow réclamé pour dossier {row['Dossier N']} ✔")
        save_database({"clients": df.to_dict(orient="records")})
        st.experimental_rerun()

# ---------------------------------------------------------
# TABLEAU 3 — ESCROW RÉCLAMÉ
# ---------------------------------------------------------
st.subheader("📌 Escrow réclamé")

escrow_reclame = df[df["Escrow_reclame"] == True]

st.dataframe(
    escrow_reclame[["Dossier N", "Nom", "Acompte 1", "Date_reclamation"]],
    use_container_width=True
)

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------
save_database({"clients": df.to_dict(orient="records")})
