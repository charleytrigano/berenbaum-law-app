import streamlit as st

def kpi_card(label, value, color="#4CAF50"):
    st.markdown(f"""
    <div style="
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 2px solid {color};
        ">
        <h3 style="margin: 0; color: {color};">{label}</h3>
        <h2 style="margin: 5px 0 0 0;">{value}</h2>
    </div>
    """, unsafe_allow_html=True)

