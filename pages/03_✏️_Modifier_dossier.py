import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.set_page_config(page_title="Modifier dossier", page_icon="✏️", layout="wide")
st.title("✏️ Modifier un dossier")

# --------------------------------------------------
# Fonction sécurisée pour éviter ValueError
# --------------------------------------------------
def safe_float(x, default=0.0):
    try:
        if x is None:
            return default
        if isinstance(x, (int, float)):
            return float(x)

        x = str(x).replace(",", ".").strip()

        if x == "" or x.lower() in ["nan", "none", "-", "n/a"]:
            return default

        return float(x)
    except:
        return default


# --------------------------------------------------
# Chargement base Dropbox
# --------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier disponible.")
    st.stop()

# --------------------------------------------------
# Sélection du dossier
# --------------------------------------------------
liste = [f"{c.get('Dossier N')} – {c.get('Nom')}" for c in clients]
choix = st.selectbox("Sélectionner un dossier", liste)

index = liste.index(choix)
dossier = clients[index]

st.subheader("🧾 Informations du dossier")

col1, col2 = st.columns(2)

with col1:
    num = st.text_input("Dossier N", value=str(dossier.get("Dossier N", "")))
    nom = st.text_input("Nom", value=str(dossier.get("Nom", "")))
    cat = st.text_input("Catégories", value=str(dossier.get("Catégories", "")))
    souscat = st.text_input("Sous-catégories", value=str(dossier.get("Sous-catégories", "")))
    visa = st.text_input("Visa", value=str(dossier.get("Visa", "")))

with col2:
    honoraires = st.number_input(
        "Montant honoraires (US $)",
        value=safe_float(dossier.get("Montant honoraires (US $)", 0)),
        format="%.2f",
    )

    autres = st.number_input(
        "Autres frais (US $)",
        value=safe_float(dossier.get("Autres frais (US $)", 0)),
        format="%.2f",
    )

    acom1 = st.number_input("Acompte 1", value=safe_float(dossier.get("Acompte 1", 0)), format="%.2f")
    acom2 = st.number_input("Acompte 2", value=safe_float(dossier.get("Acompte 2", 0)), format="%.2f")
    acom3 = st.number_input("Acompte 3", value=safe_float(dossier.get("Acompte 3", 0)), format="%.2f")
    acom4 = st.number_input("Acompte 4", value=safe_float(dossier.get("Acompte 4", 0)), format="%.2f")

comment = st.text_area("Commentaires", value=str(dossier.get("Commentaires", "")))

# --------------------------------------------------
# Bouton Enregistrer
# --------------------------------------------------
if st.button("💾 Enregistrer", type="primary"):
    clients[index] = {
        "Dossier N": num,
        "Nom": nom,
        "Catégories": cat,
        "Sous-catégories": souscat,
        "Visa": visa,
        "Montant honoraires (US $)": honoraires,
        "Autres frais (US $)": autres,
        "Acompte 1": acom1,
        "Acompte 2": acom2,
        "Acompte 3": acom3,
        "Acompte 4": acom4,
        "Commentaires": comment,
    }

    db["clients"] = clients
    save_database(db)

    st.success("✔ Dossier mis à jour")
    st.balloons()


# --------------------------------------------------
# Bouton Supprimer
# --------------------------------------------------
st.markdown("---")
if st.button("🗑️ Supprimer ce dossier"):
    del clients[index]
    db["clients"] = clients
    save_database(db)
    st.success("Dossier supprimé ✔")
    st.stop()
