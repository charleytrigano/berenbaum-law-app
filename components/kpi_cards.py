import streamlit as st

def kpi_card(title, value, icon):
    st.markdown(
        f"""
        <div style="
            background-color: #1A1A1A;
            padding: 14px 18px;
            border-radius: 12px;
            border: 1px solid #444;
            width: 100%;
            margin-bottom: 8px;
        ">
            <div style="font-size:28px; margin-bottom:4px;">
                {icon}
            </div>

            <div style="
                font-size:15px;
                font-weight:500;
                color:#D8B86A;
                margin-bottom:6px;
                white-space:nowrap;
            ">
                {title}
            </div>

            <div style="
                font-size:28px;
                font-weight:700;
                color:#FFD777;
            ">
                {value}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
