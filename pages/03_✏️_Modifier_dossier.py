import streamlit as st
from backend.dropbox_utils import load_database, save_database


from datetime import datetime

# ---------------------------------------------------
# PAGE SETUP
# ---------------------------------------------------
st.set_page_config(page_title="Modifier dossier", page_icon="✏️", layout="wide")

st.title("✏️ Modifier un dossier")
st.write("Recherchez un dossier existant puis modifiez ses informations.")

# ---------------------------------------------------
# LOAD DB
# ---------------------------------------------------
db = load_database()

if "clients" not in db:
    st.error("⚠️ Aucun client dans la base Dropbox.")
    st.stop()

clients = db["clients"]

# ---------------------------------------------------
# CHOIX DU DOSSIER
# ---------------------------------------------------
st.subheader("🔎 Sélectionner un dossier")

liste_dossiers = [c["Dossier N"] for c in clients]

selected = st.selectbox("Choisir un numéro de dossier", [""] + liste_dossiers)

if not selected:
    st.info("Sélectionnez un dossier pour commencer.")
    st.stop()

# Trouver le dossier dans la liste
index = next(i for i, c in enumerate(clients) if c["Dossier N"] == selected)
dossier = clients[index]

# ---------------------------------------------------
# FORMULAIRE
# ---------------------------------------------------
st.subheader(f"📄 Dossier {selected}")

col1, col2 = st.columns(2)

with col1:
    nom = st.text_input("Nom", dossier.get("Nom", ""))
    categorie = st.text_input("Catégories", dossier.get("Catégories", ""))
    sous_categorie = st.text_input("Sous-catégories", dossier.get("Sous-catégories", ""))
    visa = st.text_input("Visa", dossier.get("Visa", ""))

with col2:
    montant = st.number_input("Montant honoraires (USD)", value=float(dossier.get("Montant honoraires (US $)", 0)), format="%.2f")
    autres_frais = st.number_input("Autres frais (USD)", value=float(dossier.get("Autres frais (US $)", 0)), format="%.2f")
    acompte1 = st.number_input("Acompte 1 (USD)", value=float(dossier.get("Acompte 1", 0)), format="%.2f")
    date_acompte1 = st.date_input("Date Acompte 1", datetime.fromisoformat(dossier["Date Acompte 1"]) if dossier.get("Date Acompte 1") else datetime.now())
    mode_paiement = st.text_input("Mode de paiement", dossier.get("mode de paiement", ""))

st.markdown("---")

# DATES / STATUT
st.subheader("📅 Dates & Suivi")

colA, colB = st.columns(2)

with colA:
    date_envoi = st.date_input("Date envoi", datetime.fromisoformat(dossier["Date envoi"]) if dossier.get("Date envoi") else None)
    date_accepte = st.date_input("Date acceptation", datetime.fromisoformat(dossier["Date acceptation"]) if dossier.get("Date acceptation") else None)

with colB:
    date_refus = st.date_input("Date refus", datetime.fromisoformat(dossier["Date refus"]) if dossier.get("Date refus") else None)
    date_annulation = st.date_input("Date annulation", datetime.fromisoformat(dossier["Date annulation"]) if dossier.get("Date annulation") else None)

rfe = st.text_area("RFE", dossier.get("RFE", ""))
commentaires = st.text_area("Commentaires", dossier.get("Commentaires", ""))

st.markdown("---")

# ---------------------------------------------------
# SAUVEGARDER
# ---------------------------------------------------
if st.button("💾 Enregistrer les modifications", type="primary"):

    dossier_modifie = {
        "Dossier N": selected,
        "Nom": nom,
        "Date": dossier.get("Date", str(datetime.now().date())),
        "Catégories": categorie,
        "Sous-catégories": sous_categorie,
        "Visa": visa,
        "Montant honoraires (US $)": montant,
        "Autres frais (US $)": autres_frais,
        "Acompte 1": acompte1,
        "Date Acompte 1": str(date_acompte1),
        "mode de paiement": mode_paiement,
        "Escrow": dossier.get("Escrow", ""),
        "Acompte 2": dossier.get("Acompte 2", ""),
        "Date Acompte 2": dossier.get("Date Acompte 2", ""),
        "Acompte 3": dossier.get("Acompte 3", ""),
        "Date Acompte 3": dossier.get("Date Acompte 3", ""),
        "Acompte 4": dossier.get("Acompte 4", ""),
        "Date Acompte 4": dossier.get("Date Acompte 4", ""),
        "Dossier envoyé": "",
        "Date envoi": str(date_envoi) if date_envoi else "",
        "Dossier accepté": "",
        "Date acceptation": str(date_accepte) if date_accepte else "",
        "Dossier refusé": "",
        "Date refus": str(date_refus) if date_refus else "",
        "Dossier Annulé": "",
        "Date annulation": str(date_annulation) if date_annulation else "",
        "RFE": rfe,
        "Commentaires": commentaires,
        "Escrow_final": dossier.get("Escrow_final", ""),
        "Date réclamation": dossier.get("Date réclamation", "")
    }

    db["clients"][index] = dossier_modifie
    save_database(db)

    st.success("✔️ Le dossier a été mis à jour.")
    st.balloons()

# ---------------------------------------------------
# SUPPRESSION
# ---------------------------------------------------
st.markdown("---")
st.subheader("🗑️ Suppression")

if st.button("⚠️ Supprimer définitivement ce dossier"):
    del db["clients"][index]
    save_database(db)
    st.warning("❌ Dossier supprimé définitivement.")
    st.balloons()
    st.stop()
