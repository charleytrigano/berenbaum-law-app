import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database
from utils.dossier_numbering import (
    sort_dossiers,
    next_sub_dossier,
)

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="➕ Nouveau dossier", page_icon="➕", layout="wide")
render_sidebar()
st.title("➕ Nouveau dossier")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
df = pd.DataFrame(clients) if clients else pd.DataFrame(columns=["Dossier N"])

df["Dossier N"] = df["Dossier N"].astype(str)

# ---------------------------------------------------------
# MODE DE CREATION
# ---------------------------------------------------------
st.subheader("📌 Type de dossier")

mode = st.radio(
    "Choisir le type de création",
    ["🆕 Nouveau dossier principal", "➕ Sous-dossier d’un dossier existant"],
)

# ---------------------------------------------------------
# DOSSIER N
# ---------------------------------------------------------
if mode == "🆕 Nouveau dossier principal":
    parents = [
        int(d.split("-")[0])
        for d in df["Dossier N"]
        if d.split("-")[0].isdigit()
    ]
    new_parent_id = max(parents) + 1 if parents else 13000
    dossier_id = str(new_parent_id)

else:
    parents = sorted(
        {d.split("-")[0] for d in df["Dossier N"] if d.split("-")[0].isdigit()},
        key=int,
    )
    parent_id = st.selectbox("Choisir le dossier parent", parents)

    suffix = next_sub_dossier(df["Dossier N"].tolist(), parent_id)
    dossier_id = f"{parent_id}-{suffix}"

st.info(f"📄 **Dossier N attribué : `{dossier_id}`**")

# ---------------------------------------------------------
# FORMULAIRE
# ---------------------------------------------------------
st.subheader("🧾 Informations dossier")

col1, col2, col3 = st.columns(3)
col1.text_input("Dossier N", value=dossier_id, disabled=True)
nom = col2.text_input("Nom du client")
date_dossier = col3.date_input("Date")

# ---------------------------------------------------------
# FINANCES
# ---------------------------------------------------------
st.subheader("💰 Facturation")

f1, f2, f3 = st.columns(3)
honoraires = f1.number_input("Montant honoraires (US $)", min_value=0.0, step=50.0)
frais = f2.number_input("Autres frais (US $)", min_value=0.0, step=10.0)
f3.number_input("Total facturé", value=honoraires + frais, disabled=True)

# ---------------------------------------------------------
# ACOMPTES
# ---------------------------------------------------------
st.subheader("🏦 Paiements")

a1, a2, a3, a4 = st.columns(4)
ac1 = a1.number_input("Acompte 1", min_value=0.0)
ac2 = a2.number_input("Acompte 2", min_value=0.0)
ac3 = a3.number_input("Acompte 3", min_value=0.0)
ac4 = a4.number_input("Acompte 4", min_value=0.0)

# ---------------------------------------------------------
# ESCROW
# ---------------------------------------------------------
escrow = st.checkbox("Mettre en Escrow (Acompte 1 uniquement)")

commentaire = st.text_area("📝 Commentaire")

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------
if st.button("💾 Enregistrer le dossier", type="primary"):
    if not nom.strip():
        st.error("Le nom est obligatoire.")
        st.stop()

    entry = {
        "Dossier N": dossier_id,
        "Nom": nom,
        "Date": str(date_dossier),
        "Categories": "",
        "Sous-categories": "",
        "Visa": "",
        "Montant honoraires (US $)": honoraires,
        "Autres frais (US $)": frais,
        "Acompte 1": ac1,
        "Acompte 2": ac2,
        "Acompte 3": ac3,
        "Acompte 4": ac4,
        "Escrow": bool(escrow),
        "Escrow_a_reclamer": False,
        "Escrow_reclame": False,
        "Dossier envoye": False,
        "Dossier accepte": False,
        "Dossier refuse": False,
        "Dossier Annule": False,
        "RFE": False,
        "Commentaire": commentaire,
    }

    clients.append(entry)
    db["clients"] = clients
    save_database(db)

    st.success(f"✔ Dossier **{dossier_id}** créé avec succès.")
    st.rerun()
