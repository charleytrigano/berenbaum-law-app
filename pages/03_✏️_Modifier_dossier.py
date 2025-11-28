import streamlit as st
from components.database import load_database, save_database
from datetime import datetime

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Modifier un dossier",
    page_icon="✏️",
    layout="wide"
)

st.title("✏️ Modifier un dossier")
st.write("Modifiez les informations d’un dossier existant.")

# ---------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.error("Aucun dossier trouvé dans la base Dropbox.")
    st.stop()

# ---------------------------------------------------
# LISTE DES DOSSIERS
# ---------------------------------------------------
dossier_list = [c["Dossier N"] for c in clients if "Dossier N" in c]

selected_dossier = st.selectbox("📁 Sélectionnez un dossier", dossier_list)

# Trouver l’entrée sélectionnée
client = next(c for c in clients if c["Dossier N"] == selected_dossier)

# ---------------------------------------------------
# FORMULAIRE AVEC AUTO-FILL
# ---------------------------------------------------
st.subheader("📝 Informations générales")

col1, col2 = st.columns(2)

with col1:
    nom = st.text_input("Nom du client", client.get("Nom", ""))
    date = st.date_input(
        "Date d'ouverture",
        datetime.fromisoformat(client["Date"]) if client.get("Date") else datetime.now()
    )

with col2:
    categorie = st.text_input("Catégorie", client.get("Catégories", ""))
    sous_categorie = st.text_input("Sous-catégorie", client.get("Sous-catégories", ""))

st.subheader("🛂 Informations Visa")

visa_type = st.text_input("Type de Visa", client.get("Visa", ""))

st.subheader("💰 Paiements & Finances")

colf1, colf2 = st.columns(2)

with colf1:
    honoraires = st.number_input(
        "Montant honoraires (USD)",
        min_value=0.0,
        value=float(client.get("Montant honoraires (US $)", 0)),
        format="%.2f"
    )
    frais_divers = st.number_input(
        "Autres frais (USD)",
        min_value=0.0,
        value=float(client.get("Autres frais (US $)", 0)),
        format="%.2f"
    )

with colf2:
    acompte1 = st.number_input(
        "Acompte 1 (USD)",
        min_value=0.0,
        value=float(client.get("Acompte 1", 0)),
        format="%.2f"
    )

    date_acompte1 = st.date_input(
        "Date Acompte 1",
        datetime.fromisoformat(client["Date Acompte 1"]) if client.get("Date Acompte 1") else datetime.now()
    )

    mode_paiement = st.text_input("Mode de paiement", client.get("mode de paiement", ""))

st.subheader("📦 Suivi du dossier")

dossier_envoye = st.checkbox("Dossier envoyé", client.get("Dossier envoyé", False))
date_envoi = st.date_input(
    "Date d'envoi",
    datetime.fromisoformat(client["Date envoi"]) if client.get("Date envoi") else datetime.now()
)

dossier_accepte = st.checkbox("Dossier accepté", client.get("Dossier accepté", False))
date_acceptation = st.date_input(
    "Date d'acceptation",
    datetime.fromisoformat(client["Date acceptation"]) if client.get("Date acceptation") else datetime.now()
)

dossier_refuse = st.checkbox("Dossier refusé", client.get("Dossier refusé", False))
date_refus = st.date_input(
    "Date de refus",
    datetime.fromisoformat(client["Date refus"]) if client.get("Date refus") else datetime.now()
)

commentaires = st.text_area("Commentaires", client.get("Commentaires", ""))

# ---------------------------------------------------
# SAUVEGARDER LES MODIFICATIONS
# ---------------------------------------------------
st.markdown("---")
save_btn = st.button("💾 Enregistrer les modifications", type="primary")

if save_btn:

    # Mise à jour de l'objet client
    client.update({
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
    })

    db["clients"] = clients
    save_database(db)

    st.success("✔️ Les modifications ont été enregistrées avec succès !")
    st.balloons()
