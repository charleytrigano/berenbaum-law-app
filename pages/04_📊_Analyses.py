import streamlit as st
import plotly.express as px
from backend.google_sheets import load_sheet
from utils.config import SHEET_CLIENTS

st.title("📊 Analyses & Ratios")

df = load_sheet(SHEET_CLIENTS)

if "Catégories" in df.columns:
    fig = px.histogram(df, x="Catégories", title="Répartition par catégorie")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Aucune colonne 'Catégories' trouvée.")

