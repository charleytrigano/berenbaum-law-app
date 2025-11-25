import streamlit as st
from backend.google_sheets import load_sheet
from utils.config import SHEET_VISA

st.title("🛂 Visa – Suivi")

df = load_sheet(SHEET_VISA)
st.dataframe(df, use_container_width=True)
