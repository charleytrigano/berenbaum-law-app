import streamlit as st
from backend.dropbox_utils import load_database, save_database

st.title("🛂 Dossiers Visa")

db = load_database()
visa = db.get("visa", [])

st.subheader("Liste des dossiers Visa")
st.dataframe(visa, use_container_width=True)

st.subheader("Ajouter un dossier Visa")

nom = st.text_input("Nom")
prenom = st.text_input("Prénom")
pays = st.text_input("Pays")

if st.button("Ajouter"):
    visa.append({
        "Nom": nom,
        "Prenom": prenom,
        "Pays": pays
    })
    db["visa"] = visa
    save_database(db)
    st.success("Dossier Visa ajouté ✔")
