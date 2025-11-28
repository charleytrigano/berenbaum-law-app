import streamlit as st
from backend.convert_excel_to_json import convert_excel_to_json

st.title("🛠️ Conversion Excel → JSON")

if st.button("Convertir maintenant"):
    convert_excel_to_json()
    st.success("Base JSON générée avec succès depuis l’Excel !")

