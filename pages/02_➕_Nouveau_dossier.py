import streamlit as st
from components.database import load_database, save_database
from datetime import datetime
import uuid

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Nouveau dossier",
    page_icon="➕",
    layout="wide"
)

st.title("➕ Nouveau dossier")
st.write("Créez un nouveau dossier client dans la base Dropbox.")

# ---------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------
db = load_database()
clients = db.get("clients", [])

# ---------------------------------------------------
# AUTOMATIC DOSSIER NUMBER
# ---------------------------------------------------
def generate_dossier_number():
    now = datetime.now()
    number = f"D{now.strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
    return number

dossier_number = generate_dossier_number()

# ---------------------------------------------------
# FORMULAIRE
# ---------------------------------------------------
st.subheader("📝 Informations générales")

col1, col2 = st.columns(2)

with col1:
    nom = st.text_input("Nom du client *")
    date = st.date_input("Date d'ouverture", datetime.now())

with col2:
    categorie = st.selectbox(
        "Catégorie *",
        ["Immigration", "Visa", "Consultation", "Autre"]
    )

    sous_categorie = st.text_input("Sous-catégorie")


st.subheader("🛂 Informations Visa")

visa_type = st.text_input("Type de Visa (si applicable)")

st.subheader("💰 Paiements & Finances")

colf1, colf2 = st.columns(2)

with colf1:
    honoraires = st.number_input("Montant honoraires (USD)", min_value=0.0, format="%.2f")
    frais_divers = st.number_input("Autres frais (USD)", min_value=0.0, format="%.2f")

with colf2:
    acompte1 = st.number_input("Acompte 1 (USD)", min_value=0.0, format="%.2f")
    date_acompte1 = st.date_input("Date Acompte 1", datetime.now())
    mode_paiement = st.text_input("Mode de paiement")

st.subheader("📦 Suivi du dossier")

dossier_envoye = st.checkbox("Dossier envoyé")
date_envoi = st.date_input("Date d'envoi", datetime.now())

dossier_accepte = st.checkbox("Dossier accepté")
date_acceptation = st.date_input("Date d'acceptation", datetime.now())

dossier_refuse = st.checkbox("Dossier refusé")
date_refus = st.date_input("Date de refus", datetime.now())

commentaires = st.text_area("Commentaires")

# ---------------------------------------------------
# SUBMIT BUTTON
# ---------------------------------------------------
st.markdown("---")
create = st.button("💾 Enregistrer le dossier", type="primary")

if create:
    if not nom.strip():
        st.error("Le nom du client est obligatoire.")
        st.stop()

    new_entry = {
        "Dossier N": dossier_number,
        "Nom": nom,
        "Date": str(date),
        "Catégories": categorie,
        "Sous-catégories": sous_categorie,
        "Visa": visa_type,
        "Montant honoraires (US $)": honoraires,
        "Autres frais (US $)": frais_divers,
        "Acompte 1": acompte1,
        "Date Acompte 1": str(date_acompte1),
        "mode de paiement": mode_paiement,
        "Dossier envoyé": dossier_envoye,
        "Date envoi": str(date_envoi),
        "Dossier accepté": dossier_accepte,
        "Date acceptation": str(date_acceptation),
        "Dossier refusé": dossier_refuse,
        "Date refus": str(date_refus),
        "Commentaires": commentaires,
    }

    clients.append(new_entry)
    db["clients"] = clients
    save_database(db)

    st.success(f"🎉 Le dossier **{dossier_number}** a été créé avec succès !")
    st.balloons()
