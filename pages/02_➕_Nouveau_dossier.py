import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database
from utils.visa_filters import clean_visa_df, get_souscats, get_visas

st.set_page_config(page_title="Nouveau dossier", page_icon="➕", layout="wide")
st.title("➕ Nouveau dossier")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
visa_raw = pd.DataFrame(db.get("visa", []))
visa_table = clean_visa_df(visa_raw)

df_clients = pd.DataFrame(clients)

# ---------------------------------------------------------
# GENERATE NEXT DOSSIER NUMBER
# ---------------------------------------------------------
def nouveau_numero():
    if df_clients.empty:
        return 12000
    nums = pd.to_numeric(df_clients["Dossier N"], errors="coerce")
    nums = nums.dropna()
    return int(nums.max()) + 1 if len(nums) else 12000

dossier_num = nouveau_numero()

# ---------------------------------------------------------
# UI – LIGNE 1 : DOSSIER / NOM / DATE
# ---------------------------------------------------------
st.subheader("🧾 Informations générales")

col1, col2, col3 = st.columns(3)

with col1:
    dossier = st.number_input("Dossier N", value=dossier_num, step=1)

with col2:
    nom = st.text_input("Nom du client")

with col3:
    date_creation = st.date_input("Date de création")

# ---------------------------------------------------------
# UI – LIGNE 2 : CATEGORIE / SOUS-CATEGORIE / VISA
# ---------------------------------------------------------
st.subheader("🗂️ Classification")

all_categories = sorted(visa_table["Categories"].dropna().unique().tolist())
categorie = st.selectbox("Catégorie", [""] + all_categories)

if categorie:
    souscats = get_souscats(visa_table, categorie)
else:
    souscats = []

souscategorie = st.selectbox("Sous-catégorie", [""] + souscats)

if souscategorie:
    visas = get_visas(visa_table, souscategorie)
else:
    visas = []

visa = st.selectbox("Visa", [""] + visas)

# ---------------------------------------------------------
# UI – LIGNE 3 : FEES
# ---------------------------------------------------------
st.subheader("💵 Honoraires")

colA, colB, colC = st.columns(3)

with colA:
    honoraires = st.number_input("Montant honoraires (US $)", min_value=0.0, step=100.0)

with colB:
    autres_frais = st.number_input("Autres frais (US $)", min_value=0.0, step=10.0)

with colC:
    total_facture = honoraires + autres_frais
    st.number_input("Total facturé", value=total_facture, disabled=True)

# ---------------------------------------------------------
# UI – LIGNE 4 : ACOMPTE + PAYEMENT + ESCROW
# ---------------------------------------------------------
st.subheader("💳 Paiements")

colX, colY, colZ = st.columns(3)

with colX:
    acompte1 = st.number_input("Acompte 1", min_value=0.0, step=50.0)

with colY:
    mode_paiement = st.selectbox(
        "Mode de paiement",
        ["", "Chèque", "CB", "Virement", "Venmo"]
    )

with colZ:
    escrow = st.checkbox("Escrow ?")

# ---------------------------------------------------------
# SAVE BUTTON
# ---------------------------------------------------------
if st.button("💾 Enregistrer le dossier", type="primary"):

    nouveau = {
        "Dossier N": dossier,
        "Nom": nom,
        "Date": str(date_creation),
        "Categories": categorie,
        "Sous-categories": souscategorie,
        "Visa": visa,
        "Montant honoraires (US $)": honoraires,
        "Autres frais (US $)": autres_frais,
        "Total facturé": total_facture,
        "Acompte 1": acompte1,
        "mode de paiement": mode_paiement,
        "Escrow": escrow,
        "Acompte 2": 0,
        "Acompte 3": 0,
        "Acompte 4": 0,
        "Commentaires": "",
        "Dossier envoye": "",
        "Dossier accepte": "",
        "Dossier refuse": "",
        "Dossier Annule": "",
        "RFE": "",
        "Date envoi": "",
        "Date acceptation": "",
        "Date refus": "",
        "Date annulation": "",
        "Date Acompte 1": "",
        "Date Acompte 2": "",
        "Date Acompte 3": "",
        "Date Acompte 4": "",
    }

    clients.append(nouveau)
    db["clients"] = clients
    save_database(db)

    st.success("🎉 Dossier enregistré avec succès !")
    st.balloons()
