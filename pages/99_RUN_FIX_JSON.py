import streamlit as st
import importlib

st.set_page_config(page_title="🔧 Réparation JSON", page_icon="🛠️")

st.title("🔧 Réparation JSON Dropbox")
st.write("Cette page sert uniquement à lancer la réparation automatique du JSON.")

if st.button("🚀 Lancer la réparation maintenant"):
    try:
        fix_module = importlib.import_module("99_Fix_JSON")
        importlib.reload(fix_module)

        st.success("✔ Réparation terminée avec succès !")
        st.info("❗ Vous pouvez maintenant supprimer cette page : pages/99_RUN_FIX_JSON.py")

    except Exception as e:
        st.error(f"❌ Erreur lors de la réparation : {e}")
