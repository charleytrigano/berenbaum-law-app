import streamlit as st

def kpi_card(label: str, value, icon: str = "📁"):
    """
    Affiche une carte KPI premium gold + dark mode.
    """

    html = f"""
    <div style="
        background: linear-gradient(145deg, #1c1c1c, #0f0f0f);
        border: 1px solid rgba(255, 215, 0, 0.25);
        padding: 16px 20px;
        border-radius: 14px;
        box-shadow: 0px 4px 14px rgba(0,0,0,0.45);
        text-align: center;
        margin-bottom: 18px;
    ">
        <div style="font-size: 30px; margin-bottom: 4px;">
            {icon}
        </div>

        <div style="
            font-size: 15px;
            font-weight: 500;
            color: #D8B86A;
            margin-bottom: 6px;
            white-space: nowrap;
        ">
            {label}
        </div>

        <div style="
            font-size: 28px;
            font-weight: 700;
            color: #FFD777;
        ">
            {value:,}
        </div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)
