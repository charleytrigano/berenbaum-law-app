import streamlit as st
from components.database import load_database, save_database
from datetime import datetime

# ---------------------------------------------------
# PAGE SETUP
# ---------------------------------------------------
st.set_page_config(page_title="Nouveau dossier", page_icon="➕", layout="wide")

st.title("➕ Nouveau dossier")
st.write("Créer un nouveau dossier client.")

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------
db = load_database()
if "clients" not in db:
    db["clients"] = []

clients = db["clients"]

# ---------------------------------------------------
# FONCTION POUR GÉNÉRER AUTOMATIQUEMENT UN NUMÉRO DE DOSSIER
# ---------------------------------------------------
def generer_dossier_numero():
    if not clients:
        return "1001"
    numeros = [int(c["Dossier N"]) for c in clients if c["Dossier N"].isdigit()]
    return str(max(numeros) + 1)

dossier_num = generer_dossier_numero()

# ---------------------------------------------------
# FORMULAIRE
# ---------------------------------------------------
st.subheader("📄 Informations du dossier")

col1, col2 = st.columns(2)

with col1:
    nom = st.text_input("Nom du client", "")
    categorie = st.text_input("Catégories", "")
    sous_categorie = st.text_input("Sous-catégories", "")
    visa = st.text_input("Visa", "")

with col2:
    montant = st.number_input("Montant honoraires (USD)", min_value=0.0, format="%.2f")
    autres_frais = st.number_input("Autres frais (USD)", min_value=0.0, format="%.2f")
    acompte1 = st.number_input("Acompte 1 (USD)", min_value=0.0, format="%.2f")
    date_acompte1 = st.date_input("Date Acompte 1", datetime.now())
    mode_paiement = st.text_input("Mode de paiement", "")

st.markdown("---")
st.subheader("📅 Dates et statut")

colA, colB = st.columns(2)

with colA:
    date_envoi = st.date_input("Date envoi", None)
    date_accept = st.date_input("Date acceptation", None)
with colB:
    date_refus = st.date_input("Date refus", None)
    date_annulation = st.date_input("Date annulation", None)

rfe = st.text_area("RFE", "")
commentaires = st.text_area("Commentaires", "")

# ---------------------------------------------------
# BOUTON SAUVEGARDE
# ---------------------------------------------------
st.markdown("---")
if st.button("💾 Enregistrer le dossier", type="primary"):

    if nom.strip() == "":
        st.error("Le nom du client est obligatoire.")
        st.stop()

    nouveau_dossier = {
        "Dossier N": dossier_num,
        "Nom": nom,
        "Date": str(datetime.now().date()),
        "Catégories": categorie,
        "Sous-catégories": sous_categorie,
        "Visa": visa,
        "Montant honoraires (US $)": montant,
        "Autres frais (US $)": autres_frais,
        "Acompte 1": acompte1,
        "Date Acompte 1": str(date_acompte1),
        "mode de paiement": mode_paiement,
        "Escrow": "",
        "Acompte 2": "",
        "Date Acompte 2": "",
        "Acompte 3": "",
        "Date Acompte 3": "",
        "Acompte 4": "",
        "Date Acompte 4": "",
        "Dossier envoyé": "",
        "Date envoi": str(date_envoi) if date_envoi else "",
        "Dossier accepté": "",
        "Date acceptation": str(date_accept) if date_accept else "",
        "Dossier refusé": "",
        "Date refus": str(date_refus) if date_refus else "",
        "Dossier Annulé": "",
        "Date annulation": str(date_annulation) if date_annulation else "",
        "RFE": rfe,
        "Commentaires": commentaires,
        "Escrow_final": "",
        "Date réclamation": ""
    }

    db["clients"].append(nouveau_dossier)
    save_database(db)

    st.success(f"✔️ Dossier {dossier_num} enregistré avec succès !")
    st.balloons()

    st.info("💡 Vous pouvez maintenant modifier le dossier dans la page dédiée.")
    st.stop()
