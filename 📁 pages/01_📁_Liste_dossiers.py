import streamlit as st
from backend.dropbox_utils import load_database

st.title("📁 Liste des dossiers")

db = load_database()
clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier client trouvé.")
else:
    st.dataframe(clients, use_container_width=True)
