import streamlit as st

# ======================================================
# 🎨 KPI CARD – VERSION GOLD PREMIUM FIXÉE
# ======================================================

def kpi_card(title: str, value, icon: str = "📁"):
    """Affiche une carte KPI premium avec HTML interprété correctement."""

    card_html = f"""
    <div style="
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;

        background: rgba(184,134,11,0.12);
        border: 1px solid rgba(184,134,11,0.35);
        padding: 12px 14px;
        border-radius: 12px;

        width: 100%;
        min-height: 120px;

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
            text-wrap: balance;
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
    """

    # KEY FIX QUI EMPÊCHE LE HTML DE S'AFFICHER BRUT
    st.markdown(card_html, unsafe_allow_html=True)
