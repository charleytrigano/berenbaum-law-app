import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.title("✏️ Modifier un dossier")

db = load_database()
clients = db.get("clients", [])
visa_ref = db.get("visa", [])

df_visa = pd.DataFrame(visa_ref)

# ---------------------------
# Sélecteur dossier
# ---------------------------
liste = [f"{c['Dossier N']} - {c['Nom']}" for c in clients]
selection = st.selectbox("Choisir un dossier", liste)
index = liste.index(selection)
d = clients[index]

# ---------------------------
# Formulaire
# ---------------------------
col1, col2 = st.columns(2)

with col1:
    dossier_num = st.text_input("Dossier N", value=str(d["Dossier N"]))
    nom = st.text_input("Nom", value=d["Nom"])

    cat_list = sorted(df_visa["Categories"].unique())
    categorie = st.selectbox("Catégorie", cat_list, index=cat_list.index(d["Catégories"]))

    sous_cat_list = sorted(df_visa[df_visa["Categories"] == categorie]["Sous-categories"].unique())
    sous_categorie = st.selectbox("Sous-catégorie", sous_cat_list, index=sous_cat_list.index(d["Sous-catégories"]))

with col2:
    visa_list = df_visa[
        (df_visa["Categories"] == categorie) &
        (df_visa["Sous-categories"] == sous_categorie)
    ]["Visa"].tolist()

    visa = st.selectbox("Visa", visa_list, index=visa_list.index(d["Visa"]) if d["Visa"] in visa_list else 0)

    montant_hon = st.number_input("Montant honoraires (US $)", value=float(d.get("Montant honoraires (US $)",0)))
    autres_frais = st.number_input("Autres frais (US $)", value=float(d.get("Autres frais (US $)",0)))

commentaires = st.text_area("Commentaires", value=d.get("Commentaires",""))

# ---------------------------
# Sauvegarde
# ---------------------------
if st.button("💾 Enregistrer"):

    clients[index] = {
        "Dossier N": dossier_num,
        "Nom": nom,
        "Catégories": categorie,
        "Sous-catégories": sous_categorie,
        "Visa": visa,
        "Montant honoraires (US $)": montant_hon,
        "Autres frais (US $)": autres_frais,
        "Commentaires": commentaires
    }

    db["clients"] = clients
    save_database(db)

    st.success("Modifications enregistrées ✔")
