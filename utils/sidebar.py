# utils/sidebar.py
import streamlit as st
from PIL import Image
import base64
import os

def render_sidebar():
    # --- LOGO TOUJOURS EN HAUT ---
    with st.sidebar:
        st.markdown(
            """
            <style>
            [data-testid="stSidebar"] img {
                margin-bottom: 20px;
                margin-top: 0px !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        logo_path = "assets/logo.png"
        
        if os.path.exists(logo_path):
            st.image(logo_path, width=120)
        else:
            st.warning("⚠️ Logo introuvable : assets/logo.png")

        st.markdown("---")  # ligne de séparation
