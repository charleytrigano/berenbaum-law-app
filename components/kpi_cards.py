import streamlit as st

def kpi_card(label, value, emoji):
    """
    Affiche un KPI premium en style 'gold'
    avec HTML sécurisé compatible Streamlit Cloud.
    """

    html = f"""
    <div style="
        padding:16px;
        border-radius:12px;
        background-color:#1A1A1A;
        border:1px solid #3A3A3A;
        text-align:center;
        box-shadow:0 0 12px rgba(255,215,100,0.08);
    ">
        
        <div style="font-size:28px; margin-bottom:4px;">
            {emoji}
        </div>

        <div style="
            font-size:15px;
            font-weight:500;
            color:#D8B86A;
            margin-bottom:6px;
            white-space:nowrap;
        ">
            {label}
        </div>

        <div style="
            font-size:28px;
            font-weight:700;
            color:#FFD777;
        ">
            {value:,}
        </div>

    </div>
    """

    st.markdown(html, unsafe_allow_html=True)
