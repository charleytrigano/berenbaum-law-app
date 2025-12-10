import streamlit as st
import uuid

# ==========================================
# 🎨 THEME LUXE AVOCAT – G3 Or Profond
# ==========================================
COLOR_GOLD = "#B8860B"
COLOR_GOLD_SOFT = "#8C6A18"
COLOR_BG_CARD = "rgba(255, 255, 255, 0.05)"
COLOR_BORDER = "rgba(255, 255, 255, 0.15)"

# ==========================================
# 🔢 Injection du JS pour l’animation comptable
# ==========================================
def inject_counter_js():
    counter_js = """
    <script>
    function animateValue(id, start, end, duration) {
        if (start === end) return;
        const range = end - start;
        let current = start;
        const increment = range / (duration / 16);
        const element = document.getElementById(id);
        let timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= end) ||
                (increment < 0 && current <= end)) {
                current = end;
                clearInterval(timer);
            }
            element.innerText = Math.floor(current).toLocaleString();
        }, 16);
    }
    </script>
    """
    st.markdown(counter_js, unsafe_allow_html=True)

inject_counter_js()

# ==========================================
# 🟦 FONCTION KPI CARD – PREMIUM LUXE
# ==========================================
def kpi_card(title, value, icon="📁", color=COLOR_GOLD):
    unique_id = str(uuid.uuid4()).replace("-", "")
    
    card_html = f"""
    <div style="
        padding: 16px;
        border-radius: 16px;
        background: {COLOR_BG_CARD};
        border: 1px solid {COLOR_BORDER};
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        transition: transform 0.2s ease;
    " 
    onmouseover="this.style.transform='scale(1.03)'"
    onmouseout="this.style.transform='scale(1)'">

        <div style="display:flex; align-items:center; gap:10px;">
            <div style="font-size:28px;">{icon}</div>
            <div style="font-size:16px; color:{COLOR_GOLD_SOFT}; font-weight:500;">
                {title}
            </div>
        </div>

        <div id="{unique_id}" style="
            font-size:34px;
            color:{color};
            margin-top:8px;
            font-weight:700;
        ">0</div>

        <script>
            animateValue("{unique_id}", 0, {value}, 1200);
        </script>
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)
