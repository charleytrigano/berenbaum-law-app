import streamlit as st
from backend.dropbox_utils import load_database, save_database
from backend.dropbox_utils import load_database

st.write("🔍 Test lecture JSON :")
st.json(load_database())


st.set_page_config(page_title="Synchronisation Dropbox", page_icon="🔄")

st.title("🔄 Test de synchronisation Dropbox")
st.write("Test complet : authentification, lecture, écriture du JSON.")

# ------------------------------------------------------
# TEST LECTURE
# ------------------------------------------------------
st.subheader("📥 Lecture Dropbox")

try:
    db = load_database()
    st.success("✔ Lecture JSON OK")
    st.json(db)
except Exception as e:
    st.error(f"❌ Erreur de lecture : {e}")
    st.stop()

# ------------------------------------------------------
# TEST ÉCRITURE
# ------------------------------------------------------
st.subheader("📤 Écriture Dropbox")

try:
    db["__test__"] = "OK"
    save_database(db)
    st.success("✔ Écriture JSON OK (clé '__test__' ajoutée)")
except Exception as e:
    st.error(f"❌ Erreur d'écriture : {e}")
