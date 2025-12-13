import streamlit as st

def kpi_card(title, value, icon, help_text=None):
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(145deg, #1C1C1C, #0F0F0F);
            padding: 12px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid #333;
            box-shadow: 0 0 8px rgba(255,215,0,0.15);
            color: #FFD777;
            width: 100%;
        ">
            <div style="font-size:22px; margin-bottom:2px;">{icon}</div>
            <div style="font-size:13px; color:#D8B86A; white-space:nowrap;">
                {title}
            </div>
            <div style="font-size:20px; font-weight:700;">
                {value}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if help_text:
        st.caption(help_text)