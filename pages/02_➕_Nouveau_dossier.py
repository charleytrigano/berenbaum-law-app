import streamlit as st
from backend.dropbox_utils import load_database, save_database

st.title("➕ Nouveau dossier")

# Chargement base
try:
    db = load_database()
except:
    db = {"clients": [], "visa": [], "escrow": [], "compta": []}

clients = db.get("clients", [])

# ------------------------------------------------------
# FONCTION : Générer automatiquement le prochain Dossier N
# ------------------------------------------------------
def generer_dossier_numero():
    numeros = []

    for c in clients:
        num = c.get("Dossier N")

        # Cas 1 : nombre en texte ("123")
        if isinstance(num, str) and num.strip().isdigit():
            numeros.append(int(num.strip()))

        # Cas 2 : nombre déjà en int
        elif isinstance(num, int):
            numeros.append(num)

        # Autres : ignoré
        else:
            continue

    # Si aucun numéro → commencer à 1
    nouveau_num = max(numeros) + 1 if numeros else 1
    return str(nouveau_num)


# ------------------------------------------------------
# FORMULAIRE UTILISATEUR
# ------------------------------------------------------

st.subheader("Création d'un nouveau dossier")

col1, col2 = st.columns(2)

with col1:
    dossier_num = st.text_input("Numéro de dossier", generer_dossier_numero())
    nom = st.text_input("Nom du client")
    categorie = st.text_input("Catégorie")
    sous_categorie = st.text_input("Sous-catégorie")

with col2:
    visa = st.text_input("Visa")
    autres_commentaires = st.text_area("Commentaires")

# ------------------------------------------------------
# BOUTON DE VALIDATION
# ------------------------------------------------------

if st.button("Créer le dossier", type="primary"):
    if nom.strip() == "":
        st.error("Le nom du client est obligatoire.")
    else:
        nouveau_client = {
            "Dossier N": dossier_num,
            "Nom": nom,
            "Catégories": categorie,
            "Sous-catégories": sous_categorie,
            "Visa": visa,
            "Commentaires": autres_commentaires
        }

        db["clients"].append(nouveau_client)
        save_database(db)

        st.success(f"Dossier #{dossier_num} créé avec succès !")
        st.balloons()

        st.info("Vous pouvez créer un nouveau dossier ou changer de page.")
