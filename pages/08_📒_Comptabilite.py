import streamlit as st
from backend.dropbox_utils import load_database, save_database

st.title("📒 Comptabilité Clients")

db = load_database()
compta = db.get("comptacli", [])

st.subheader("Entrées comptables")
st.dataframe(compta, use_container_width=True)

st.subheader("Ajouter une entrée comptable")

date = st.date_input("Date")
client = st.text_input("Client")
montant = st.number_input("Montant", step=0.01)

if st.button("Ajouter"):
    compta.append({
        "Date": str(date),
        "Client": client,
        "Montant": montant
    })
    db["comptacli"] = compta
    save_database(db)
    st.success("Entrée ajoutée ✔")

