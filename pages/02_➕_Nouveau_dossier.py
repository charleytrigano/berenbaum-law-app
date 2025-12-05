import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database
from utils.visa_filters import clean_visa_df

st.set_page_config(page_title="Nouveau dossier", page_icon="➕", layout="wide")
st.title("➕ Nouveau dossier")

# ---------------------------------------------------------
# CHARGER DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
visa_raw = pd.DataFrame(db.get("visa", []))

# Nettoyage complet du tableau Visa
visa_table = clean_visa_df(visa_raw)

# ---------------------------------------------------------
# GENERATION NUMÉRO DE DOSSIER
# ---------------------------------------------------------
def nouveau_numero():
    if not clients:
        return 10000
    nums = [c.get("Dossier N") for c in clients if str(c.get("Dossier N")).isdigit()]
    if not nums:
        return 10000
    return max(nums) + 1

new_id = nouveau_numero()

# ---------------------------------------------------------
# FORMULAIRE
# ---------------------------------------------------------

st.subheader("📌 Informations principales")

col1, col2, col3 = st.columns(3)
dossier_num = col1.text_input("Dossier N", new_id)
nom = col2.text_input("Nom du client")
date_creation = col3.date_input("Date de création")

# ---------------------------------------------------------
# FILTRES INTELLIGENTS VISA
# ---------------------------------------------------------
st.subheader("🧩 Catégories & Visa")

# Liste réelle des catégories (exclut les sous-catégories)
real_categories = sorted(
    set(visa_table["Categories"]) - set(visa_table["Sous-categories"])
)

colA, colB, colC = st.columns(3)

categorie = colA.selectbox("Catégorie", [""] + real_categories)

# Sous-catégories dépendantes
if categorie:
    souscats = [""] + sorted(
        visa_table.loc[visa_table["Categories"] == categorie, "Sous-categories"].unique()
    )
else:
    souscats = [""]

souscat = colB.selectbox("Sous-catégorie", souscats)

# Visa dépendant
if souscat:
    visas = [""] + sorted(
        visa_table.loc[visa_table["Sous-categories"] == souscat, "Visa"].unique()
    )
elif categorie:
    visas = [""] + sorted(
        visa_table.loc[visa_table["Categories"] == categorie, "Visa"].unique()
    )
else:
    visas = [""]

visa_choice = colC.selectbox("Visa", visas)

# ---------------------------------------------------------
# HONORAIRES & FRAIS
# ---------------------------------------------------------
st.subheader("💰 Honoraires & Frais")

colH1, colH2, colH3 = st.columns(3)

honoraires = colH1.number_input("Montant honoraires (US $)", min_value=0.0, step=100.0)
autres_frais = colH2.number_input("Autres frais (US $)", min_value=0.0, step=10.0)

facture = honoraires + autres_frais
colH3.number_input("Total facturé", value=facture, disabled=True)

# ---------------------------------------------------------
# ACOMPTE + MODE DE REGLEMENT
# ---------------------------------------------------------
st.subheader("💵 Paiement")

colP1, colP2, colP3 = st.columns(3)

acompte1 = colP1.number_input("Acompte 1", min_value=0.0, step=50.0)

mode_reglement = colP2.selectbox(
    "Mode de règlement",
    ["", "Chèque", "CB", "Virement", "Venmo"]
)

escrow = colP3.checkbox("Escrow ?")

# ---------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------
if st.button("💾 Enregistrer le dossier", type="primary"):

    dossier = {
        "Dossier N": dossier_num,
        "Nom": nom,
        "Date": str(date_creation),

        "Categories": categorie,
        "Sous-categories": souscat,
        "Visa": visa_choice,

        "Montant honoraires (US $)": honoraires,
        "Autres frais (US $)": autres_frais,
        "Acompte 1": acompte1,
        "mode de paiement": mode_reglement,
        "Escrow": escrow,

        "Total facturé": facture,
        "Montant encaissé": acompte1,
        "Solde": facture - acompte1,
    }

    clients.append(dossier)
    db["clients"] = clients
    save_database(db)

    st.success("🎉 Dossier créé et sauvegardé avec succès !")
    st.balloons()
