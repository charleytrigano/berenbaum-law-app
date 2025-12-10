import streamlit as st
from PIL import Image
import os


def render_sidebar():
    with st.sidebar:
        st.markdown(" ")

        candidate_paths = [
            "assets/logo.png",
            "./assets/logo.png",
            "/mount/src/berenbaum-law-app/assets/logo.png",
            "/mount/src/assets/logo.png"
        ]

        logo_loaded = False
        for p in candidate_paths:
            if os.path.exists(p):
                st.image(p, width=140)
                logo_loaded = True
                break

        if not logo_loaded:
            st.warning("⚠️ Logo introuvable")

        st.markdown("---")
