import streamlit as st
from backend.dropbox_utils import load_database, save_database

st.title("✏️ Modifier un dossier")

# --------------------------------------------------
# Safe conversion to float (évite toutes les erreurs Excel/JSON)
# --------------------------------------------------
def safe_float(x, default=0.0):
    try:
        if x is None:
            return default
        if isinstance(x, (int, float)):
            return float(x)
        x = str(x).replace(",", ".").strip()
        return float(x) if x != "" else default
    except:
        return default

# --------------------------------------------------
# Chargement base Dropbox
# --------------------------------------------------
try:
    db = load_database()
except:
    db = {"clients": [], "visa": [], "escrow": [], "compta": []}

clients = db.get("clients", [])

# --------------------------------------------------
# Sélection du dossier à modifier
# --------------------------------------------------
st.subheader("Sélection du dossier")

if not clients:
    st.warning("Aucun dossier enregistré.")
    st.stop()

# Liste déroulante
liste_dossiers = [f"{c.get('Dossier N', '?')} - {c.get('Nom', '')}" for c in clients]
selection = st.selectbox("Choisir un dossier", liste_dossiers)

# Trouver le dossier choisi
index = liste_dossiers.index(selection)
dossier = clients[index]

# --------------------------------------------------
# AFFICHAGE DU FORMULAIRE
# --------------------------------------------------
st.subheader("Modifier les informations")

col1, col2 = st.columns(2)

with col1:
    dossier_num = st.text_input("Dossier N", value=str(dossier.get("Dossier N", "")))
    nom = st.text_input("Nom", value=dossier.get("Nom", ""))
    categorie = st.text_input("Catégorie", value=dossier.get("Catégories", ""))
    sous_categorie = st.text_input("Sous-catégorie", value=dossier.get("Sous-catégories", ""))
    visa = st.text_input("Visa", value=dossier.get("Visa", ""))

with col2:
    montant_honoraires = st.number_input(
        "Montant honoraires (USD)",
        value=safe_float(dossier.get("Montant honoraires (US $)", 0)),
        format="%.2f"
    )
    autres_frais = st.number_input(
        "Autres frais (USD)",
        value=safe_float(dossier.get("Autres frais (US $)", 0)),
        format="%.2f"
    )
    commentaires = st.text_area(
        "Commentaires",
        value=dossier.get("Commentaires", "")
    )

# --------------------------------------------------
# BOUTON ENREGISTRER
# --------------------------------------------------
if st.button("💾 Enregistrer les modifications", type="primary"):

    clients[index] = {
        "Dossier N": dossier_num,
        "Nom": nom,
        "Catégories": categorie,
        "Sous-catégories": sous_categorie,
        "Visa": visa,
        "Montant honoraires (US $)": montant_honoraires,
        "Autres frais (US $)": autres_frais,
        "Commentaires": commentaires
    }

    db["clients"] = clients
    save_database(db)

    st.success("Modifications enregistrées ✔")
    st.balloons()

# --------------------------------------------------
# BOUTON SUPPRIMER
# --------------------------------------------------
st.markdown("---")
st.subheader("❌ Supprimer ce dossier")

if st.button("🗑️ Supprimer définitivement le dossier"):

    del clients[index]
    db["clients"] = clients
    save_database(db)

    st.success("Dossier supprimé ✔")
    st.stop()
