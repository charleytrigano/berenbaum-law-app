import streamlit as st
import pandas as pd
from components.database import load_database
from components.cards import badge

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Liste des dossiers",
    page_icon="📁",
    layout="wide"
)

st.title("📁 Liste des dossiers")
st.write("Visualisez, filtrez et explorez tous les dossiers clients.")

# ---------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------
try:
    db = load_database()
except Exception as e:
    st.error(f"Erreur lors du chargement de la base : {e}")
    db = {"clients": []}

clients = db.get("clients", [])
df = pd.DataFrame(clients)

if df.empty:
    st.warning("Aucun dossier disponible.")
    st.stop()

# ---------------------------------------------------
# BARRE DE RECHERCHE + FILTRES
# ---------------------------------------------------
st.subheader("🔍 Recherche & Filtres")

col1, col2, col3 = st.columns(3)

with col1:
    search = st.text_input("Recherche (Nom, Dossier N, Visa)")

with col2:
    categorie_filter = st.selectbox(
        "Catégorie",
        options=["Toutes"] + sorted(df["Catégories"].dropna().unique().tolist())
        if "Catégories" in df.columns else ["Toutes"]
    )

with col3:
    visa_filter = st.selectbox(
        "Type de Visa",
        options=["Tous"] + sorted(df["Visa"].dropna().unique().tolist())
        if "Visa" in df.columns else ["Tous"]
    )

# ---------------------------------------------------
# FILTRAGE LOGIQUE
# ---------------------------------------------------
filtered = df.copy()

if search:
    search_lower = search.lower()
    filtered = filtered[
        filtered.astype(str).apply(lambda row: search_lower in row.to_string().lower(), axis=1)
    ]

if categorie_filter != "Toutes" and "Catégories" in df.columns:
    filtered = filtered[filtered["Catégories"] == categorie_filter]

if visa_filter != "Tous" and "Visa" in df.columns:
    filtered = filtered[filtered["Visa"] == visa_filter]

# ---------------------------------------------------
# DATATABLE PRO
# ---------------------------------------------------
st.subheader("📄 Résultats")

def render_row(row):
    dossier = row.get("Dossier N", "")
    nom = row.get("Nom", "")
    cat = row.get("Catégories", "")
    visa = row.get("Visa", "")
    date = row.get("Date", "")

    return f"""
        <div style="padding:12px; border-bottom:1px solid #e0e0e0;">
            <b>{dossier}</b> — {nom}<br>
            <span style='color:#555'>Catégorie : {cat}</span><br>
            <span style='color:#777'>Visa : {visa}</span><br>
            <span style='font-size:12px; color:#999'>Créé le {date}</span>
        </div>
    """

st.markdown(
    "<div style='border:1px solid #DDD; border-radius:10px; padding:5px;'>",
    unsafe_allow_html=True
)

for _, row in filtered.iterrows():
    st.markdown(render_row(row), unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

