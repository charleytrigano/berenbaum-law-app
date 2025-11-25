import streamlit as st
from backend.google_sheets import load_sheet
from utils.config import SHEET_ESCROW

st.title("💰 Escrow – Gestion")

df = load_sheet(SHEET_ESCROW)
st.dataframe(df, use_container_width=True)
