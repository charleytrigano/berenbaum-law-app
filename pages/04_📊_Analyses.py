import streamlit as st

# ==========================================================
# 🎨 KPI CARD – Version premium stable (ne fuite JAMAIS en brut)
# ==========================================================

def kpi_card(label, value, icon):

    html = f"""
    <div style="
        background: rgba(255, 255, 255, 0.06);
        padding: 14px 18px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 0 8px rgba(255,255,255,0.05);
        text-align: left;
        min-height: 95px;
    ">
        <div style="font-size: 26px; margin-bottom: 4px;">
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

    # 👉 Ce mode d'affichage est le SEUL correct :
    st.markdown(html, unsafe_allow_html=True)
