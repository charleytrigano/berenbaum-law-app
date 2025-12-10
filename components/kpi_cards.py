import streamlit as st

def kpi_card(title, value, icon, tooltip=""):
    html = f"""
    <div style="
        background: linear-gradient(145deg, #1C1C1C, #0F0F0F);
        padding: 14px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #3a3a3a;
        box-shadow: 0 0 8px rgba(255,215,0,0.12);
        width: 100%;
        min-width: 140px;
        display: flex;
        flex-direction: column;
        align-items: center;
        transition: 0.2s;
    "
        title="{tooltip}"
    >

        <div style="font-size: 22px; margin-bottom: 2px;">
            {icon}
        </div>

        <div style="
            font-size: 13px;
            font-weight: 500;
            color: #D8B86A;
            margin-bottom: 4px;
            white-space: nowrap;
        ">
            {title}
        </div>

        <div style="
            font-size: 24px;
            font-weight: 700;
            color: #FFD777;
        ">
            {value}
        </div>

    </div>
    """

    st.components.v1.html(html, height=120)
