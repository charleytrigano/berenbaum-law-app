import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database
from utils.visa_filters import clean_visa_df

st.set_page_config(page_title="Nouveau dossier", page_icon="➕", layout="wide")

st.title("➕ Nouveau dossier")

# ---------------------------------------------------
# Charger la base Dropbox
# ---------------------------------------------------
db = load_database()
clients = db.get("clients", [])

visa_raw = pd.DataFrame(db.get("visa", []))
visa_table = clean_visa_df(visa_raw)

# ---------------------------------------------------
# Fonction pour générer un nouveau numéro
# ---------------------------------------------------
def nouveau_numero():
    if not clients:
        return 12001
    nums = [c.get("Dossier N", 0) for c in clients if isinstance(c.get("Dossier N"), (int, float))]
    return int(max(nums) + 1)

# ---------------------------------------------------
# LIGNE 1 — Infos principales
# ---------------------------------------------------
st.subheader("Informations principales")

col1, col2, col3 = st.columns(3)

dossier_num = col1.number_input("Dossier N", value=nouveau_numero(), step=1)
nom = col2.text_input("Nom du client")
date_dossier = col3.date_input("Date du dossier")

# ---------------------------------------------------
# LIGNE 2 — Catégorie / Sous-catégorie / Visa
# ---------------------------------------------------
st.subheader("Type de dossier")

colA, colB, colC = st.columns(3)

# Catégories
cat_list = sorted(visa_table["Categories"].dropna().unique().tolist())
categorie = colA.selectbox("Catégorie", cat_list)

# Sous-catégories filtrées
souscat_list = sorted(
    visa_table.loc[visa_table["Categories"] == categorie, "Sous-categories"]
    .dropna().unique().tolist()
)
souscat = colB.selectbox("Sous-catégorie", souscat_list)

# Visa filtré
visa_list = sorted(
    visa_table.loc[visa_table["Sous-categories"] == souscat, "Visa"]
    .dropna().unique().tolist()
)
visa_choice = colC.selectbox("Visa", visa_list)

# ---------------------------------------------------
# LIGNE 3 — Honoraires / Frais / Total
# ---------------------------------------------------
st.subheader("Montants")

colH1, colH2, colH3 = st.columns(3)

honoraires = colH1.number_input("Montant honoraires (US $)", min_value=0.0, step=100.0)
autres_frais = colH2.number_input("Autres frais (US $)", min_value=0.0, step=50.0)

total_facture = honoraires + autres_frais
colH3.number_input("Total facturé (US $)", value=total_facture, disabled=True)

# ---------------------------------------------------
# LIGNE 4 — Paiement & Escrow
# ---------------------------------------------------
st.subheader("Paiement")

colP1, colP2, colP3 = st.columns(3)

acompte1 = colP1.number_input("Acompte 1 (US $)", min_value=0.0, step=50.0)

mode_reglement = colP2.selectbox(
    "Mode de règlement",
    ["Chèque", "CB", "Virement", "Venmo"]
)

escrow = colP3.checkbox("Escrow ?")

# ---------------------------------------------------
# VALIDATION
# ---------------------------------------------------
if st.button("💾 Ajouter le dossier", type="primary"):

    new_entry = {
        "Dossier N": dossier_num,
        "Nom": nom,
        "Date": str(date_dossier),

        "Catégories": categorie,
        "Sous-catégories": souscat,
        "Visa": visa_choice,

        "Montant honoraires (US $)": honoraires,
        "Autres frais (US $)": autres_frais,
        "Total facturé": total_facture,

        "Acompte 1": acompte1,
        "mode de paiement": mode_reglement,
        "Escrow": escrow,
    }

    clients.append(new_entry)
    db["clients"] = clients
    save_database(db)

    st.success("✔ Nouveau dossier ajouté avec succès !")
    st.balloons()
