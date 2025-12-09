import streamlit as st

def kpi_card(label, value, icon, color):
    st.markdown(f"""
    <div style="padding:15px;background:{color};border-radius:12px;color:white;text-align:center;">
        <div style="font-size:28px;font-weight:bold;">{value}</div>
        <div style="font-size:16px;">{icon} {label}</div>
    </div>
    """, unsafe_allow_html=True)

def display_kpi_row(data):
    cols = st.columns(6)

    kpi_card("Total dossiers", data["total"], "📁", "#4A90E2")
    cols[1].markdown("")
    kpi_card("Envoyés", data["envoyes"], "📤", "#F5A623")
    cols[2].markdown("")
    kpi_card("Acceptés", data["acceptes"], "✅", "#7ED321")
    cols[3].markdown("")
    kpi_card("Refusés", data["refuses"], "❌", "#D0021B")
    cols[4].markdown("")
    kpi_card("Escrow en cours", data["escrow_en_cours"], "💰", "#50E3C2")
    cols[5].markdown("")
