import streamlit as st

# ============================================
# 📌 KPI CARD (Gold Premium – Stable version)
# ============================================
def kpi_card(title: str, value, icon: str = "📁"):
    """Affiche un KPI premium sans JS (100% compatible Streamlit Cloud)."""

    st.markdown(f"""
    <div style="
        background:rgba(184,134,11,0.15);
        padding:16px;
        border-radius:12px;
        border:1px solid rgba(184,134,11,0.25);
        margin-bottom:16px;
    ">
        <div style="display:flex; align-items:center; gap:10px;">
            <div style="font-size:26px;">{icon}</div>
            <div style="font-size:15px; color:#CFA650; font-weight:500;">
                {title}
            </div>
        </div>

        <div style="
            font-size:30px;
            color:#FFD777;
            margin-top:6px;
            font-weight:700;
        ">
            {value:,}
        </div>
    </div>
    """, unsafe_allow_html=True)
