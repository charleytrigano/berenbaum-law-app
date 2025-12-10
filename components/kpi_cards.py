import streamlit as st

# ======================================================
# 🎨 STYLE PREMIUM - VERSION STABLE (sans animation)
# ======================================================

def kpi_card(title: str, value, icon: str = "📁"):
    """Affiche un KPI premium statique (Version B)"""

    st.markdown(f"""
    <div style="
        background: rgba(184,134,11,0.10);
        border: 1px solid rgba(184,134,11,0.35);
        padding: 14px 18px;
        border-radius: 12px;
        min-width: 180px;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.25);
    ">

        <div style="font-size: 28px; margin-bottom: 4px;">
            {icon}
        </div>

        <div style="
            font-size: 15px;
            font-weight: 500;
            color: #D8B86A;
            margin-bottom: 6px;
            white-space: nowrap;
        ">
            {title}
        </div>

        <div style="
            font-size: 26px;
            font-weight: 700;
            color: #FFD777;
        ">
            {value:,}
        </div>

    </div>
    """, unsafe_allow_html=True)
