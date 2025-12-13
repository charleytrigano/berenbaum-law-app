import streamlit as st
import pandas as pd
from datetime import datetime

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(
    page_title="💲 Tarifs par Visa",
    page_icon="💲",
    layout="wide"
)
render_sidebar()
st.title("💲 Tarifs par Visa")

# =====================================================
# LOAD DATABASE
# =====================================================
db = load_database()

tarifs = db.get("tarifs", [])
history = db.get("tarifs_history", [])
visa_ref = pd.DataFrame(db.get("visa", []))

# Liste unique des visas existants
visa_list = sorted(visa_ref["Visa"].dropna().unique().tolist())

# =====================================================
# SÉLECTION VISA
# =====================================================
st.subheader("🎯 Sélection du Visa")

visa = st.selectbox("Visa", visa_list)

current = next((t for t in tarifs if t["Visa"] == visa and t["Actif"]), None)

col1, col2 = st.columns(2)

tarif_actuel = col1.number_input(
    "Tarif actuel (US $)",
    value=float(current["Tarif"]) if current else 0.0,
    step=50.0
)

date_effet = col2.date_input(
    "Date d’effet",
    value=datetime.today().date()
)

# =====================================================
# ENREGISTREMENT
# =====================================================
if st.button("💾 Enregistrer le tarif", type="primary"):

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Désactiver l’ancien tarif
    for t in tarifs:
        if t["Visa"] == visa and t["Actif"]:
            t["Actif"] = False

            history.append({
                "Visa": visa,
                "Ancien_tarif": t["Tarif"],
                "Nouveau_tarif": tarif_actuel,
                "Date_effet": str(date_effet),
                "Modifie_le": now
            })

    # Ajouter le nouveau
    tarifs.append({
        "Visa": visa,
        "Tarif": tarif_actuel,
        "Date_effet": str(date_effet),
        "Actif": True
    })

    db["tarifs"] = tarifs
    db["tarifs_history"] = history
    save_database(db)

    st.success("✔ Tarif mis à jour avec historique conservé")
    st.rerun()

# =====================================================
# HISTORIQUE
# =====================================================
st.markdown("---")
st.subheader("🕓 Historique des tarifs")

hist_df = pd.DataFrame([h for h in history if h["Visa"] == visa])

if hist_df.empty:
    st.info("Aucun historique pour ce visa.")
else:
    st.dataframe(
        hist_df.sort_values("Modifie_le", ascending=False),
        use_container_width=True
    )

