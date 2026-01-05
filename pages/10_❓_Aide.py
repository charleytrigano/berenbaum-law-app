import streamlit as st
from datetime import date

from utils.sidebar import render_sidebar
from utils.help_pdf import build_help_pdf_bytes

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(
    page_title="❓ Aide & Mode d’emploi",
    page_icon="❓",
    layout="wide"
)
render_sidebar()

# =====================================================
# HEADER
# =====================================================
st.title("❓ AIDE & MODE D’EMPLOI")
st.subheader("Application de gestion des dossiers — Cabinet interne")

st.markdown(f"""
Version interne — Cabinet  
Dernière mise à jour : **{date.today().strftime('%d/%m/%Y')}**
""")

st.markdown("---")

# =====================================================
# EXPORT PDF
# =====================================================
st.header("📄 Export du manuel en PDF")

col1, col2 = st.columns(2)

with col1:
    if st.button("⬇️ Télécharger le PDF – Français", type="primary"):
        pdf = build_help_pdf_bytes(language="FR")
        st.download_button(
            "Télécharger",
            data=pdf,
            file_name="Manuel_Cabinet_Interne_FR.pdf",
            mime="application/pdf"
        )

with col2:
    if st.button("⬇️ Télécharger le PDF – English", type="primary"):
        pdf = build_help_pdf_bytes(language="EN")
        st.download_button(
            "Download",
            data=pdf,
            file_name="Internal_Cabinet_Manual_EN.pdf",
            mime="application/pdf"
        )

st.markdown("---")

# =====================================================
# CONTENU À L’ÉCRAN
# =====================================================
st.header("📘 Contenu du manuel")

st.markdown("""
Ce manuel couvre :

- L’objectif global de l’application
- La navigation complète
- Les règles officielles Escrow
- La gestion des dossiers parents et fils
- Les analyses et KPI
- Les exports Excel et PDF
- Les bonnes pratiques cabinet

👉 **Ce document fait foi en interne.**
""")

st.success("📘 Manuel prêt à être imprimé ou diffusé en interne.")