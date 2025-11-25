import streamlit as st
from backend.google_sheets import load_sheet
from utils.config import SHEET_COMPTA

st.title("📒 Comptabilité")

df = load_sheet(SHEET_COMPTA)
st.dataframe(df, use_container_width=True)

