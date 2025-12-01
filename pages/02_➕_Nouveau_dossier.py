import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database

st.title("➕ Nouveau dossier")

# Chargement base
db = load_database()
clients = db.get("clients", [])
visa_ref = db.get("visa", [])   # 🔥 fichier Visa.xlsx importé

# Structure de référence
df_visa = pd.DataFrame(visa_ref)

# ----------------------------
# Fonction : numéro dossier
# ----------------------------
def nouveau_numero():
    nums = []
    for c in clients:
        n = c.get("Dossier N")
        try:
            n = int(str(n).split("-")[0])
            nums.append(n)
        except:
            pass
    return str(max(nums) + 1 if nums else 1)

# ----------------------------
# FORMULAIRE
# ----------------------------
col1, col2 = st.columns(2)

with col1:
    dossier_num = st.text_input("Dossier N", nouveau_numero())
    nom = st.text_input("Nom")
    categories = sorted(df_visa["Categories"].unique())
    categorie = st.selectbox("Catégorie", categories)

    sous_cat_list = sorted(df_visa[df_visa["Categories"] == categorie]["Sous-categories"].unique())
    sous_categorie = st.selectbox("Sous-catégorie", sous_cat_list)

with col2:
    # 🔥 Filtres croisés Category + Sous-category
    visa_list = df_visa[
        (df_visa["Categories"] == categorie) &
        (df_visa["Sous-categories"] == sous_categorie)
    ]["Visa"].tolist()

    visa = st.selectbox("Visa", visa_list)

    montant_hon = st.number_input("Montant honoraires (US $)", min_value=0.0)
    autres_frais = st.number_input("Autres frais (US $)", min_value=0.0)

commentaires = st.text_area("Commentaires")

# ----------------------------
# ENREGISTREMENT
# ----------------------------
if st.button("Créer le dossier", type="primary"):

    new_client = {
        "Dossier N": dossier_num,
        "Nom": nom,
        "Catégories": categorie,
        "Sous-catégories": sous_categorie,
        "Visa": visa,
        "Montant honoraires (US $)": montant_hon,
        "Autres frais (US $)": autres_frais,
        "Commentaires": commentaires
    }

    clients.append(new_client)
    db["clients"] = clients

    from backend.dropbox_utils import save_database
    save_database(db)

    st.success("Dossier créé ✔")
    st.balloons()
