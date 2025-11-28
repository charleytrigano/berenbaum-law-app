import streamlit as st
from backend.dropbox_utils import load_database, save_database

st.title("💰 Escrow")

db = load_database()
escrow = db.get("escrow", [])

st.subheader("Liste des mouvements")
st.dataframe(escrow, use_container_width=True)

st.subheader("Ajouter un mouvement")

date = st.date_input("Date")
montant = st.number_input("Montant", step=0.01)
description = st.text_input("Description")

if st.button("Ajouter"):
    escrow.append({
        "Date": str(date),
        "Montant": montant,
        "Description": description
    })
    db["escrow"] = escrow
    save_database(db)
    st.success("Mouvement ajouté ✔")

