import streamlit as st

def kpi_card(title, value, icon):
    st.markdown(f"""
    <div style="
        background: linear-gradient(145deg, #1C1C1C, #0F0F0F);
        padding: 18px;
        border-radius: 14px;
        text-align: center;
        border: 1px solid #3a3a3a;
        box-shadow: 0 0 12px rgba(255,215,0,0.15);
        color: #FFD777;
        width: 100%;
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
            font-size: 28px;
            font-weight: 700;
            color: #FFD777;
        ">
            {value}
        </div>
    </div>
    """, unsafe_allow_html=True)
